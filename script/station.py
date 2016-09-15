#! /usr/bin/python3

import xml.etree.ElementTree as ET
import glob
from datetime import datetime, timedelta


class Station:
    namespace = {"cwb": "urn:cwb:gov:tw:cwbcommon:0.1"}
    cache = {}

    locationName = None
    lat = None
    lon = None
    stationId = None
    obsTime = None
    windSpeed = None
    temp = None
    humidity = None
    pres = None
    elev = None
    min10 = None

    def __init__(self, timestamp: datetime, station_name: str):
        xml_root = Station.get_file_by_obs_time(9176, timestamp, station_name)
        if xml_root is not None:
            all_location = xml_root.iterfind("cwb:location", Station.namespace)
            found = False
            for station in all_location:
                location_name = station.find("cwb:locationName", Station.namespace)
                if location_name.text == station_name:
                    self.locationName = station_name
                    found = True
                    break

            if found:
                self.lat = float(station.find("cwb:lat", Station.namespace).text)
                self.lon = float(station.find("cwb:lon", Station.namespace).text)

                all_weather_element = station.iterfind("cwb:weatherElement", Station.namespace)
                for weatherElement in all_weather_element:
                    element_name = weatherElement.find("cwb:elementName", Station.namespace).text
                    value = weatherElement.find(
                        "./{urn:cwb:gov:tw:cwbcommon:0.1}elementValue/{urn:cwb:gov:tw:cwbcommon:0.1}value").text
                    if element_name == "WDSD":
                        self.windSpeed = float(value)
                        # if self.wdsd < 0.0:
                        # raise FileNotFoundError('', '')
                    elif element_name == "TEMP":
                        self.temp = float(value)
                        # if self.temp <= -90.0:
                        # raise FileNotFoundError('', '')
                    elif element_name == "HUMD":
                        self.humidity = float(value)
                        # if self.humd < 0.0:
                        # raise FileNotFoundError('', '')
                    elif element_name == "PRES":
                        self.pres = float(value)
                        # if self.pres < 0.0:
                        # raise FileNotFoundError('', '')
                    if (self.windSpeed is not None and
                            self.temp is not None and
                            self.humidity is not None and
                            self.pres is not None):
                        break

        xml_root = Station.get_file_by_obs_time(9177, timestamp, station_name)
        if xml_root is not None:
            all_location = xml_root.iterfind("cwb:location", Station.namespace)
            found = False
            for station in all_location:
                location_name = station.find("cwb:locationName", Station.namespace)
                if location_name.text == station_name:
                    found = True
                    break

            if found:
                self.stationId = station.find("cwb:stationId", Station.namespace).text
                self.obsTime = station.find("./{urn:cwb:gov:tw:cwbcommon:0.1}time/{urn:cwb:gov:tw:cwbcommon:0.1}obsTime").text

                all_weather_element = station.iterfind("cwb:weatherElement", Station.namespace)
                for weatherElement in all_weather_element:
                    element_name = weatherElement.find("cwb:elementName", Station.namespace).text
                    value = weatherElement.find(
                        "./{urn:cwb:gov:tw:cwbcommon:0.1}elementValue/{urn:cwb:gov:tw:cwbcommon:0.1}value").text
                    if element_name == "ELEV":
                        self.elev = float(value)
                    elif element_name == "MIN_10":
                        self.min10 = float(value)
                        if self.min10 == -998.0:
                            self.min10 = 0.0
                        # elif self.min10 < 0.0:
                        # raise FileNotFoundError('', '')

                    if (self.elev is not None and
                            self.min10 is not None):
                        break

    @staticmethod
    def get_file_by_obs_time(file_id: int, target_time: datetime, target: str):
        Station.clean_cache(target_time)

        file_id = str(file_id)
        file_time = target_time

        if file_id not in Station.cache:
            Station.cache[file_id] = {}

        if target_time in Station.cache[file_id]:
            return Station.cache[file_id][target_time]

        for i in range(30):
            path = file_time.strftime("../data/%s/%s.%%Y_%%m_%%d-%%H_%%M_*.xml" % (file_id, file_id))

            for file in glob.glob(path):
                try:
                    found_location = False
                    tree = ET.parse(file)
                    root = tree.getroot()

                    obs_time = root.find(".//{urn:cwb:gov:tw:cwbcommon:0.1}obsTime")
                    if obs_time is None:
                        continue

                    obs_time = datetime.strptime(obs_time.text, "%Y-%m-%dT%H:%M:00+08:00")
                    if obs_time < target_time:
                        continue

                    if obs_time > target_time:
                        Station.cache[file_id][target_time] = None
                        return None

                    all_location = root.iterfind("cwb:location", Station.namespace)
                    for station in all_location:
                        location_name = station.find("cwb:locationName", Station.namespace)
                        if location_name.text == target:
                            found_location = True
                            break

                    if not found_location:
                        continue

                    Station.cache[file_id][target_time] = root
                    return root
                except ET.ParseError:
                    continue

            file_time = file_time + timedelta(0, 0, 0, 0, 1)

        Station.cache[file_id][target_time] = None
        return None

    @staticmethod
    def clean_cache(target_time: datetime):
        need_delete_key = []

        for i in Station.cache:
            for j in Station.cache[i]:
                if j < target_time:
                    need_delete_key.append(j)

        for i in Station.cache:
            for j in need_delete_key:
                if j in Station.cache[i]:
                    del Station.cache[i][j]

    @staticmethod
    def get_station_id(search_time: datetime, station_name: str) -> str:
        s = Station(search_time, station_name)
        return s.stationId
