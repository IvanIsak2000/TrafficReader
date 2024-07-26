#!/usr/bin/env python3
import os
import sys
import redis
import time
import threading
from sqlite3 import connect
from datetime import datetime
import pytz
import dearpygui.dearpygui as dpg
from psutil import net_io_counters
from datetime import datetime

from termcolor import colored


# Like a environment variable, can be change
UPDATE_DELAY = 0.1
FOLDER = 'history'
TIMEZONE = 'Europe/Moscow'
TERMINAL_OUTPUT = True
ROW_LIMIT = 30


class Counter():
    '''
    Counter class for storing upload/download speed record's ID.
    '''
    def __init__(self):
        counter = 0
        self.counter = counter

    def update(self):
        self.counter += 1

    def get(self) -> int:
        return self.counter


class DB():
    """
    Data base class.
    """
    def __init__(self) -> None:
        file = f"{FOLDER}/{datetime.now(pytz.timezone(TIMEZONE)).strftime('%Y-%m-%d %H:%M:%S')}.db"
        self.file = file

    def create_db(self) -> None:
        try:
            os.mkdir(FOLDER)
        except FileExistsError:
            pass

        with connect(self.file) as db:  # create db for program
            cursor = db.cursor()
            query_start = """CREATE TABLE IF NOT EXISTS network(
                upload_speed REAL,
                download_speed REAL,
                timestamp TEXT
                );"""
            cursor.execute(query_start)

    def add_record(self, upload_speed: float, download_speed: float) -> None:
        timestamp = datetime.now(pytz.timezone(TIMEZONE)).strftime("%Y-%m-%d %H:%M:%S")
        with connect(self.file) as db:
            cursor = db.cursor()
            query = """
            INSERT INTO network(upload_speed, download_speed, timestamp) VALUES(?, ?, ?);
            """
            data = [upload_speed, download_speed, timestamp]
            cursor.execute(query, data)


def colored_text(upload_speed: float, download_speed: float) -> tuple():
    if upload_speed == 0:
        u_s = colored(f"{upload_speed:.2f}", 'red')
    elif upload_speed >= 1000:
        u_s = colored(upload_speed, 'green')
    else:
        u_s = colored(f'{upload_speed:.2f}', 'white')

    if download_speed == 0:
        d_s = colored(f"{download_speed:.2f}", 'red')
    elif download_speed >= 1000:
        d_s = colored(download_speed, 'green')
    else:
        d_s = colored(f'{download_speed:.2f}', 'white')
    return (u_s, d_s)


def get_net_speed() -> tuple[float, float]:
    io = net_io_counters()
    bytes_sent, bytes_recv = io.bytes_sent, io.bytes_recv
    time.sleep(UPDATE_DELAY)
    io_2 = net_io_counters()

    upload_speed: float = (io_2.bytes_sent - bytes_sent) / 1024 / UPDATE_DELAY
    download_speed: float = (io_2.bytes_recv - bytes_recv) / 1024 / UPDATE_DELAY
    now_time = datetime.now(pytz.timezone(TIMEZONE)).strftime("%Y-%m-%d %H:%M:%S")

    upload_speed = round(upload_speed, 2)
    download_speed = round(download_speed, 2)
    return (upload_speed, download_speed, now_time)


def print_to_terminal(u_s, d_s, timestamp: str) -> None:
    row_count = counter.get()
    if row_count % ROW_LIMIT == 0 and row_count >= 10:
        os.system('clear')  
    u_s, d_s = colored_text(u_s, d_s)
    print('{:>16} ⬆️   {:>16} ⬇️   {:>5} ⌛  {:>5} 🆔'.format(u_s, d_s, timestamp, row_count))
    counter.update()


def update_data() -> None:
    sample: int = 1
    t0: float = time.time()
    while True:
        t = time.time() - t0
        y1 = float(get_net_speed()[0])
        y = float(get_net_speed()[1])

        timestamp = get_net_speed()[2]
        upload_speed = y1
        download_speed = y

        if TERMINAL_OUTPUT:
            print_to_terminal(u_s=upload_speed, d_s=download_speed, timestamp=timestamp)

        data_x.append(t)
        data_y.append(y)
        data_x1.append(t)
        data_y1.append(y1)
        # set the series x and y to the last nsamples
        dpg.set_value(
            "plot1", [list(data_x[-nsamples:]), list(data_y[-nsamples:])]
        )
        dpg.set_value(
            "plot2", [list(data_x1[-nsamples:]), list(data_y1[-nsamples:])]
        )
        dpg.fit_axis_data("x_axis")
        dpg.fit_axis_data("y_axis")
        dpg.fit_axis_data("x1_axis")
        dpg.fit_axis_data("y1_axis")
        sample = sample + 1

        db.add_record(upload_speed=str(upload_speed), download_speed=str(download_speed))


if __name__ == "__main__":
    r = redis.Redis()
    counter = Counter()
    db = DB()
    db.create_db()

    nsamples: int = 100
    data_y: list[float] = [0.0] * nsamples
    data_x: list[float] = [0.0] * nsamples
    data_y1: list[float] = [0.0] * nsamples
    data_x1: list[float] = [0.0] * nsamples

    dpg.create_context()
    dpg.create_viewport(title="network-speed", width=850, height=640)
    try:
        with dpg.window(label="", width=800, height=600, tag="Primary Window"):
            with dpg.plot(label="Speed", height=-1, width=-1):
                dpg.add_plot_legend()
                x_axis = dpg.add_plot_axis(
                    dpg.mvXAxis, label="time by start", tag="x_axis"
                )
                y_axis = dpg.add_plot_axis(dpg.mvYAxis, label="KB/s", tag="y_axis")
                dpg.add_line_series(
                    x=list(data_x),
                    y=list(data_y),
                    label="Download speed",
                    parent="y_axis",
                    tag="plot1",
                )
                x1_axis = dpg.add_plot_axis(dpg.mvXAxis, label="", tag="x1_axis")
                y1_axis = dpg.add_plot_axis(dpg.mvYAxis, label="", tag="y1_axis")
                dpg.add_line_series(
                    x=list(data_x1),
                    y=list(data_y1),
                    label="Upload speed",
                    parent="y1_axis",
                    tag="plot2",
                )
                dpg.setup_dearpygui()
                dpg.show_viewport()
                thread = threading.Thread(target=update_data)
                dpg.set_primary_window("Primary Window", True)
                thread.start()
                dpg.start_dearpygui()
                dpg.destroy_context()
    except KeyboardInterrupt:
        sys.exit()
    except SystemError:
        sys.exit()
