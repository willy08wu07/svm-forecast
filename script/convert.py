#! /usr/bin/python3

import signal
from station import Station
from radar_point import RadarPoint
from datetime import datetime, timedelta
import sys
import math

terminate_signal = False


def signal_handling(signum, frame):
    global terminate_signal
    terminate_signal = True


def convert_to_intermediate_file(start_time: datetime, end_time: datetime, station_name: str):
    global terminate_signal

    start_time = datetime_ceil(start_time)
    end_time = datetime_floor(end_time)
    station_id = Station.get_station_id(start_time, station_name)

    try:
        intermediate_file = open("%s-raw" % station_id, 'r')
    except FileNotFoundError:
        intermediate_file = None

    data_list = []
    if intermediate_file is not None:
        while True:
            line = intermediate_file.readline()
            if line == '':
                intermediate_file.close()
                break
            timestamp = line[0:line.index(' ')]
            timestamp = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:00")
            data_list.append(timestamp)

    intermediate_file = open("%s-raw" % station_id, 'a')

    task_list = []
    needed_timestamp = start_time
    while needed_timestamp <= end_time:
        if needed_timestamp not in data_list:
            task_list.append(needed_timestamp)
        needed_timestamp = needed_timestamp + timedelta(0, 0, 0, 0, 10)

    for processing_time in task_list:
        if terminate_signal:
            return

        s = Station(processing_time, station_name)
        radars = []
        for lon in [-0.1, 0, 0.1]:
            for lat in [-0.1, 0, 0.1]:
                if s.lon is None or s.lat is None:
                    radars.append(RadarPoint(processing_time, None, None))
                else:
                    radars.append(RadarPoint(processing_time, s.lon + lon, s.lat + lat))

        # if s.min10 <= 0:
            # io.write("1")
        # else:
            # io.write("2")
        save_list = [s.min10]

        for radar in radars:
            save_list.append(radar.db)
        save_list.append(s.windSpeed)
        save_list.append(s.temp)
        save_list.append(s.humidity)
        save_list.append(s.pres)

        intermediate_file.write(processing_time.strftime("%Y-%m-%dT%H:%M:00"))
        for save_item in save_list:
            intermediate_file.write(" ")
            if save_item is None:
                intermediate_file.write("None")
            else:
                intermediate_file.write(str(round(save_item, 2)))
        intermediate_file.write("\n")
        intermediate_file.flush()

        print(processing_time.strftime("%Y-%m-%d %H:%M"), save_list)
    intermediate_file.close()


def datetime_ceil(value: datetime) -> datetime:
    # 以 10 分鐘為單位，無條件進位
    raw_minute = value.minute
    ceil_minute = round(math.ceil(raw_minute / 10) * 10)
    diff = ceil_minute - raw_minute
    return value + timedelta(0, 0, 0, 0, diff)


def datetime_floor(value: datetime) -> datetime:
    # 以 10 分鐘為單位，無條件捨去
    floor_minute = round(math.floor(value.minute / 10) * 10)
    return value.replace(minute=floor_minute)


def main() -> None:
    signal.signal(signal.SIGINT, signal_handling)

    station_name = sys.argv[1]
    start_time = datetime(2016, 2, 1, 0, 0)
    end_time = datetime(2016, 7, 1, 0, 0)

    convert_to_intermediate_file(start_time, end_time, station_name)

main()
