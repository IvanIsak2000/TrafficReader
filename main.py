#!/usr/bin/env python3
import time
import collections
import threading
import pdb
import sqlite3
from datetime import datetime
import pytz

import dearpygui.dearpygui as dpg
import psutil


with sqlite3.connect("network_history.db") as db:  # create db for program

    cursor = db.cursor()
    query_start = """ CREATE TABLE IF NOT EXISTS network(
        KB_per_second TEXT,
        recording_time TEXT
        ) """
    cursor.execute(query_start)

nsamples = 100

global data_y
global data_x
data_y = [0.0] * nsamples
data_x = [0.0] * nsamples


UPDATE_DELAY = 0.1


def get_net_speed():
    io = psutil.net_io_counters()

    bytes_sent, bytes_recv = io.bytes_sent, io.bytes_recv
    time.sleep(UPDATE_DELAY)
    io_2 = psutil.net_io_counters()
    us, ds = io_2.bytes_sent - bytes_sent, io_2.bytes_recv - bytes_recv

    us = (us / 1024) / UPDATE_DELAY
    ds = (ds / 1024) / UPDATE_DELAY  # download speed

    return (us, ds)
    bytes_sent, bytes_recv = io_2.bytes_sent, io_2.bytes_recv


def update_data():
    sample = 1
    t0 = time.time()

    frequency = 1.0
    while True:
        t = time.time() - t0
        y = float(get_net_speed()[1])
        data_x.append(t)
        data_y.append(y)

        # set the series x and y to the last nsamples
        dpg.set_value('series_tag',
                      [list(data_x[-nsamples:]),
                       list(data_y[-nsamples:])])
        dpg.fit_axis_data('x_axis')
        dpg.fit_axis_data('y_axis')

        time.sleep(0.01)
        sample = sample + 1

        recording_time = datetime.now(pytz.timezone(
            'Europe/Moscow')).strftime("%H:%M:%S %Y-%m-%d")  # UTC+3

        with sqlite3.connect("network_history.db") as db:
            cursor = db.cursor()
            query = """INSERT INTO network(KB_per_second,recording_time) VALUES(?,?) """
            data = [(str(get_net_speed()[1]), str(recording_time))]
            cursor.executemany(query, data)


dpg.create_context()
dpg.create_viewport(title='network-speed', width=850, height=640)
with dpg.window(label='', width=800, height=600, tag='Primary Window'):

    with dpg.plot(label='Speed', height=-1, width=-1):

        dpg.add_plot_legend()

        x_axis = dpg.add_plot_axis(
            dpg.mvXAxis,
            label='time by start',
            tag='x_axis')
        y_axis = dpg.add_plot_axis(dpg.mvYAxis, label='KB/s', tag='y_axis')

        dpg.add_line_series(x=list(data_x), y=list(data_y),
                            label='Download speed', parent='y_axis',
                            tag='series_tag')


dpg.setup_dearpygui()
dpg.show_viewport()
thread = threading.Thread(target=update_data)
dpg.set_primary_window('Primary Window', True)
thread.start()
dpg.start_dearpygui()
dpg.destroy_context()
