#!/usr/bin/python3
'''
Description: 
LastEditors: zzh
LastEditTime: 2023-04-04 11:48:48
FilePath: /grill_tk/main.py
'''

import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import filedialog

import os
import cv2
import time
import serial
import recv_data
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


# click point
click_point_x = 0
click_point_y = 0

# shared queue
share_serial_port = Queue()
share_get_data_type = Queue()
share_proc_run_flag = Queue()


def btn_handle_update_port():
    """ update port handler """
    pass


def btn_handle_connect():
    """ connect port handler """
    pass


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
    
    pass


def update_plot_data():
    """ recv & updat """
    pass
    

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

    # TODO: 添加 点选显示温度功能
    display_img.bind('<Button-1>', photo_click_handle)


    # TODO: recv & get data 下位机 利用 Process
    # get_date_handle = Process(target=recv_data.get_data, 
    # args=(serial_port_if, shared_1, shared_2, )
    # )
    get_data_handle = Process(
        target=recv_data.get_data, args=(share_serial_port, share_get_data_type, share_proc_run_flag))

    update_plot_data()

    root.mainloop()
    print("GoodBye")
