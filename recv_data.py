#!/usr/bin/python3
'''
Description: 
LastEditors: zzh
LastEditTime: 2023-04-04 12:49:04
FilePath: /grill_tk/recv_data.py
'''

import os
import sys
import time
import serial
import binascii

root_path = os.path.split(sys.argv[0])[0]

RAW_PACKAGE_LEN = 769
MAX_SINGLE_PACKAGE_LEN = 1538


def get_data(share_serial_port_info, share_get_data_type, share_proc_run_flag):
    """ 
    get data
    from serial port 
    """
    global RAW_PACKAGE_LEN

    # open serial
    serial_port = share_serial_port_info.get()
    send_to_robot_cmd = '*DS' + share_get_data_type.get() + '\r'
    start_send_fd_data_cmd = bytes(send_to_robot_cmd.encode('utf-8'))
    stop_send_fd_data_cmd = bytes('*DS0\r'.encode('utf-8'))

    print('send cmd: ' + send_to_robot_cmd + '\n')
    print(serial_port)

    ser = serial.serial(serial_port, 115200, timeout=0.1)

    # save to file
    log_file_str = time.asctime(time.localtime()).replace(
        ' ', '_').replace(':', '_')
    log_file_path = os.path.join(
        root_path, "raw_data/log_" + log_file_str + ".txt")
    log_file_fd = open(log_file_path, 'w', newline='')  # without newline

    last_data = b'00'

    if ser.is_open:
        print("serial port is open")
        ser.flush()
    else:
        print("serial port is closed")
        # TODO: error handle here

    ser.write(start_send_fd_data_cmd)
    not_recv_data_cnt = 0

    decode_step = 0
    length_buff = 10000
    recv_len_buff = b''
    recv_data_buff = []
    recv_bytes_buff = b''

    while ser.is_open and share_proc_run_flag.empty() == false:
        r_data = ser.read(1)
        if r_data:
            not_recv_data_cnt = 0
            int_data = int.from_bytes(r_data, byteorder='little')
            # bytes -> hex
            hex_data = binascii.b2a_hex(r_data)
            header_buff = last_data + hex_data
            last_data = hex_data

            # decode step
            # =====================
            # header -- length -- sensor_data -- check_sum
            if decode_step == 0:
                # byte0 - byte
                if header_buff == b'5a5a':
                    log_file_fd.write('\n')
                    decode_step = 1
                    length_buff = 10000
                    recv_len_buff = b''

            elif decode_step == 1:
                # byte2 - byte3
                recv_len_buff += r_data
                if len(recv_len_buff) == 2:
                    # length_buff * 255 + int_data
                    length_buff = int.from_bytes(
                        recv_len_buf, byteorder='little')
                    if length_buff == MAX_SINGLE_PACKAGE_LEN:
                        decode_step = 2
                        recv_data_buff.clear()
                        recv_bytes_buff = b''
                        log_file_fd.write(
                            'start recv data, len: ' + str(length_buff) + '\n')
                    else:
                        decode_step = 0
                        log_file_fd.write(
                            'length of recv data is not good: ' + str(length_buff) + '\n')

        else:
            not_recv_data_cnt += 1
            if not_recv_data_cnt > 100:
                not_recv_data_cnt = 0
                # FIXME: start again?
                ser.write(start_send_fd_data_cmd)

    ser.write(stop_send_fd_data_cmd)
    print("exit recv data process")
    if ser.is_open:
        ser.close()
    log_file_fd.close()
    while share_proc_run_flag.empty() == False:
        pass


def replay_data():
    """ replay saved raw data """
    pass
