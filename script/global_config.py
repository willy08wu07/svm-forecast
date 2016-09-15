#! /usr/bin/python3
import sys
from station import Station
from datetime import datetime


class GlobalConfig:
    @staticmethod
    def get_intermediate_file_path(station_id: str) -> str:
        return "%s-raw" % station_id

    @staticmethod
    def get_station_id() -> str:
        start_time = datetime(2016, 2, 1, 0, 0)
        station_name = sys.argv[1]
        station_id = Station.get_station_id(start_time, station_name)
        return station_id

if __name__ == "__main__":
    print(GlobalConfig.get_station_id())
