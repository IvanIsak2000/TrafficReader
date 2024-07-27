#!/usr/bin/env python3
import os
import redis
import time
import argparse
from sqlite3 import connect
from datetime import datetime
import pytz
from psutil import net_io_counters
from datetime import datetime
from termcolor import colored


# Like a environment variable, can be change
UPDATE_DELAY = 0.1
FOLDER = 'history'
TIMEZONE = 'Europe/Moscow'
TERMINAL_OUTPUT = False
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


def get_net_speed() -> tuple[float, float, str]:
    io = net_io_counters()
    bytes_sent, bytes_recv = io.bytes_sent, io.bytes_recv
    time.sleep(UPDATE_DELAY)
    io_2 = net_io_counters()

    upload_speed: float = (io_2.bytes_sent - bytes_sent) / 1024
    download_speed: float = (io_2.bytes_recv - bytes_recv) / 1024

    return (round(upload_speed, 2), round(download_speed, 2))


def print_to_terminal(u_s, d_s, timestamp: str) -> None:
    row_count = counter.get()
    if row_count % ROW_LIMIT == 0 and row_count >= 10:
        os.system('clear')
    u_s, d_s = colored_text(u_s, d_s)
    print('{:>16} ⬆️   {:>16} ⬇️   {:>5} ⌛  {:>5} 🆔'.format(u_s, d_s, timestamp, row_count))
    counter.update()


def getting_traffic() -> None:
    while True:
        upload_speed = float(get_net_speed()[0])
        download_speed = float(get_net_speed()[1])
        timestamp = datetime.now(pytz.timezone(TIMEZONE)).strftime("%Y-%m-%d %H:%M:%S")

        if TERMINAL_OUTPUT:
            print_to_terminal(u_s=upload_speed, d_s=download_speed, timestamp=timestamp)

        db.add_record(upload_speed=upload_speed, download_speed=download_speed)


if __name__ == "__main__":
    r = redis.Redis()
    r.set('terminal_output', 'False')
    counter = Counter()
    db = DB()
    db.create_db()

    parser = argparse.ArgumentParser(description='Welcome to traffic reader')
    parser.add_argument('-c' '--colored', action='store_true', help='colored text to terminal output', default=False)
    args = parser.parse_args()

    if args.c__colored:
        r.set('terminal_output', 'gfgf')
        TERMINAL_OUTPUT = True

    print(r.get('terminal_output'))
    getting_traffic()
