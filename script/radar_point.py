#! /usr/bin/python3

from PIL import Image
import math
import glob
import datetime
import sys


class RadarPoint:
    cacheTime = None
    cacheImg = None

    db = None

    def __init__(self, file_time: datetime, x, y):
        if x is None or y is None:
            return

        if file_time != RadarPoint.cacheTime:
            file = RadarPoint.get_image_by_time(file_time)
            if file is None:
                RadarPoint.cacheTime = file_time
                RadarPoint.cacheImg = None
                return

            RadarPoint.cacheTime = file_time
            try:
                RadarPoint.cacheImg = Image.open(file)
            except OSError as e:
                # 損壞的圖片檔可能造成此例外
                RadarPoint.cacheImg = None
                print(e, file_time, file=sys.stderr)
                return

        im = RadarPoint.cacheImg
        if im is None:
            return

        x = float(x)
        y = float(y)
        x = round((x - 115.0) / 0.007411267442)
        y = round((27.2 - y) / 0.0074142724745)
        xy = (x, y)
        try:
            color = im.getpixel(xy)
        except IndexError as e:
            # 有時候會出現異常圖片格式，不同看圖軟體對此檔案會看到不同畫面，此時很可能發生 IndexError
            print(e, file_time, xy, file=sys.stderr)
            return
        except SyntaxError as e:
            # 損壞的圖片檔可能造成此例外
            print(e, file_time, xy, file=sys.stderr)
            return

        if color == (255, 255, 255, 0):
            self.db = 15
        elif color == (238, 140, 140, 255):
            self.db = 20
        elif color == (201, 112, 112, 255):
            self.db = 25
        elif color == (0, 251, 144, 255):
            self.db = 30
        elif color == (0, 187, 0, 255):
            self.db = 35
        elif color == (255, 255, 112, 255):
            self.db = 40
        elif color == (208, 208, 96, 255):
            self.db = 45
        elif color == (255, 96, 86, 255):
            self.db = 50
        elif color == (218, 0, 0, 255):
            self.db = 55
        elif color == (174, 0, 0, 255):
            self.db = 60
        elif color == (0, 0, 255, 255):
            self.db = 65
        elif color == (254, 254, 254, 255):
            self.db = 70

    @staticmethod
    def get_image_by_time(target_time: datetime):
        file_id = 6159
        file_id = str(file_id)
        file_time = target_time

        for i in range(10):
            path = file_time.strftime("../data/" + file_id + "/" + file_id + ".%Y_%m_%d-%H_%M_*.png")

            for file in glob.glob(path):
                return file

            file_time = file_time - datetime.timedelta(0, 0, 0, 0, 1)

        return None
