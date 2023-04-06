#!/usr/bin/python3
'''
Description: 
LastEditors: zzh
LastEditTime: 2023-04-06 16:03:25
FilePath: /grill_tk/main.py
'''

import tkinter as tk
from tkinter import *
from tkinter import ttk
# from tkinter import filedialog
from tkinter import messagebox

import os
import cv2
import time
import serial
import recv_data
from recv_data import RAW_PACKAGE_LEN
import numpy as np
from time import sleep
from PIL import Image, ImageTk
import serial.tools.list_ports
from multiprocessing import Process, Queue, Manager, managers, freeze_support

from signal import signal
from signal import SIGINT
from signal import SIGTERM

# config for image display
bbox_display = False

pixel_scale_factor = 20
photo_size_col = 32
photo_size_row = 24

pixel_raw_data = np.zeros((photo_size_row*pixel_scale_factor,
                          photo_size_col*pixel_scale_factor, 3), dtype=np.uint8)
temp_raw = [[j for j in range(photo_size_col)]
            for i in range(photo_size_row)]

# click point
click_point_x = 0
click_point_y = 0

# shared queue
share_serial_port = Queue()
share_proc_run_flag = Queue()
share_success_queue = Queue()


def btn_handle_update_port():
    """ update port handler """
    port_lists = list(serial.tools.list_ports.comports())
    port_lists.append('custom')
    cbox_serial_port['value'] = port_lists
    cbox_serial_port.current(0)


def btn_handle_connect():
    """ connect port handler """
    cur_serial_port = cbox_serial_port.get()
    if cur_serial_port == 'custom':
        messagebox.showwarning(
            '[Warning] Please connect current serial device')
        return

    cur_serial_port = cur_serial_port.split('-')[0]
    cur_serial_port = cur_serial_port.replace(' ', '')
    share_serial_port.put(cur_serial_port)
    if get_data_handle.is_alive():
        share_proc_run_flag.get()
        sleep(0.5)
        get_data_handle.terminate()
        get_data_handle.join(0.5)
        button_connect['text'] = "connect"
    else:
        print('Start connect device via' + cur_serial_port)
        try:
            ser = serial.Serial(cur_serial_port, 115200)
            if ser.is_open == False:
                return
        except Exception as e:
            messagebox.showinfo('[Error] ', e)
            return
        share_proc_run_flag.put(True)
        get_data_handle = Process(target=recv_data.get_data, args=(
            share_serial_port, share_IR_data, share_proc_run_flag, share_success_queue))
        get_data_handle.start()
        button_connect['text'] = "disconnect"


def btn_handle_detect():
    """ update port handler """
    bbox_display = not bbox_display


def btn_handle_save_plot():
    """ save plot """
    fig_file_path = os.path.join(recv_data.root_path, 'figs/Fig_'+time.asctime(
        time.localtime()).replace(' ', '_').replace(':', '-')+'.png')
    print('save fig to' + fig_file_path)
    heat_img.save(fig_file_path)


def btn_handle_save_raw():
    """ save raw IR sensor data """
    pass


def photo_click_handle(event):
    """
    photo_click_handler 
    """
    click_x = int(event.x / pixel_scale_factor)
    click_y = int(event.y / pixel_scale_factor)
    print(click_x, click_y)
    if click_x > photo_size_col or click_x < 0:
        print('[Error] x-col ', click_x)
        return

    if click_y > photo_size_row or click_y < 0:
        print('[Error] y-row ', click_y)
        return

    click_point_x = click_x
    click_point_y = click_y


def trans_temp_to_color(minx, maxx, temp):
    """ trans temp to color """
    delta_temp = maxx - minx
    cur_delta_temp = temp - minx
    gray_val = int(cur_delta_temp * 255 / delta_temp)

    # FIXME: gray2RGB algorithm
    r = abs(0 - gray_val)
    g = abs(127 - gray_val)
    b = abs(255 - gray_val)

    return r, g, b


def set_photo_pixel_data(x, y, r, g, b):
    """ set pixel_raw_data """
    if x > photo_size_col:
        print('set photo x is larger than ', photo_size_col)
        return
    if y > photo_size_row:
        print('set photo x is larger than ', photo_size_row)
        return

    for i in range(pixel_scale_factor):
        for j in range(pixel_scale_factor):
            pixel_raw_data[y*pixel_scale_factor +
                           i][x*pixel_scale_factor+j][0] = r
            pixel_raw_data[y*pixel_scale_factor +
                           i][x*pixel_scale_factor+j][1] = g
            pixel_raw_data[y*pixel_scale_factor +
                           i][x*pixel_scale_factor+j][2] = b


def update_plot_data():
    """ recv & updat """
    global real_time_update_plot
    if share_success_queue.empty() == False:
        # single frame data
        share_success_queue.get()
        # FIXME: optimization
        max_temp = share_IR_data[0]
        min_temp = share_IR_data[1]
        for i in range(RAW_PACKAGE_LEN - 1):
            if share_IR_data[i] > max_temp:
                max_temp = share_IR_data[i]
            if share_IR_data[i] < min_temp:
                min_temp = share_IR_data[i]

        for i in range(RAW_PACKAGE_LEN - 1):
            # temp_raw[index_row][index_col] -- right top as origin point
            # RAW_PACKAGE_LEN - 1 -- not include body temparature
            # should be Left and right mirroring
            temp_raw[int(i / 32)][int(i % 32)] = share_IR_data[i]
            t_r, t_g, t_b = trans_temp_to_color(
                max_temp, min_temp, share_IR_data[i]
            )
            set_photo_pixel_data(int(i % 32), int(i / 32), t_r, t_g, t_b)

        heat_img = Image.fromarray(pixel_raw_data)
        tk_img = ImageTk.PhotoImage(heat_img)

        # body temparature
        stat_ta_temp_data['text'] = str(float(share_IR_data[768] / 100))
        stat_min_temp_data['text'] = str(float(min_temp / 100))
        stat_max_temp_data['text'] = str(float(max_temp / 100))
        stat_point_temp_data['text'] = str(
            float(temp_raw[click_point_y][click_point_x] / 100))
        display_img.configure(img=tk_img)
        # TODO: remove
        display_img.image = tk_img

    real_time_update_plot = root.after(10, update_plot_data)


if __name__ == "__main__":
    """
    main ui 
    """
    root = tk.Tk()
    root.title("Grill TK")
    root.geometry('880x520+500+200')

    btns_area = tk.Frame(root, width=500, height=100)
    btns_area.pack(side=TOP, fill=BOTH, expand=0)

    # serial_port as combobox
    port_lists = list(serial.tools.list_ports.comports())
    port_lists.append('custom')
    cbox_serial_port = ttk.Combobox(btns_area, width=10, height=10)
    cbox_serial_port.grid(row=1, sticky='NW')
    cbox_serial_port['value'] = port_lists
    cbox_serial_port.current(0)

    # update ports
    button_update_port = tk.Button(
        btns_area, text="ports refresh", command=btn_handle_update_port)
    button_update_port.grid(row=1, column=1, sticky='NW')

    # connect ports
    button_connect = tk.Button(
        btns_area, text="connect", command=btn_handle_connect)
    button_connect.grid(row=1, column=2, sticky='NW')

    # detect
    button_connect = tk.Button(
        btns_area, text="detect bbox", command=btn_handle_detect)
    button_connect.grid(row=1, column=3, sticky='NW')

    # save plots
    button_connect = tk.Button(
        btns_area, text="save plots", command=btn_handle_save_plot)
    button_connect.grid(row=1, column=4, sticky='NW')

    # save raw data
    button_connect = tk.Button(
        btns_area, text="save raw", command=btn_handle_save_raw)
    button_connect.grid(row=1, column=5, sticky='NW')

    # statics data display
    stat_area = tk.Frame(root)
    stat_area.pack(side=LEFT, anchor='center', expand=0)

    stat_point_temp_name = tk.Label(stat_area, text='Select Point Temperature')
    stat_point_temp_name.grid(row=1, column=1, sticky='NW')
    stat_point_temp_data = tk.Label(stat_area, text='0')
    stat_point_temp_data.grid(row=1, column=2, sticky='NW')

    stat_ta_temp_name = tk.Label(stat_area, text='Sensor Body Temperature')
    stat_ta_temp_name.grid(row=2, column=1, sticky='NW')
    stat_ta_temp_data = tk.Label(stat_area, text='0')
    stat_ta_temp_data.grid(row=2, column=2, sticky='NW')

    stat_max_temp_name = tk.Label(stat_area, text='Max Temperature')
    stat_max_temp_name.grid(row=3, column=1, sticky='NW')
    stat_max_temp_data = tk.Label(stat_area, text='0')
    stat_max_temp_data.grid(row=3, column=2, sticky='NW')

    stat_min_temp_name = tk.Label(stat_area, text='Min Temperature')
    stat_min_temp_name.grid(row=4, column=1, sticky='NW')
    stat_min_temp_data = tk.Label(stat_area, text='0')
    stat_min_temp_data.grid(row=4, column=2, sticky='NW')

    # heat img
    img_area = tk.Frame(root)
    img_area.pack(side=RIGHT, fill=BOTH, expand=0)
    heat_img = Image.fromarray(pixel_raw_data)
    tk_img = ImageTk.PhotoImage(heat_img)

    display_img = Label(img_area, bg='red', image=tk_img)
    display_img.grid(row=0, column=0)
    display_img.bind('<Button-1>', photo_click_handle)

    # recv data from IRSensor
    share_IR_data = Manager().list(np.zeros(RAW_PACKAGE_LEN))
    get_data_handle = Process(
        target=recv_data.get_data, args=(share_serial_port, share_IR_data, share_proc_run_flag, share_success_queue))
    get_data_handle.daemon = True

    update_plot_data()
    root.mainloop()
    print("GoodBye")
