#! /usr/bin/python3
import sys
import random
from station import Station
from datetime import datetime, timedelta
from collections import OrderedDict


def is_record_valid(parameters, include_parameters):
    if parameters[0] == 'None':
        return False
    for i in include_parameters:
        if parameters[i + 1] == 'None':
            return False
        if i == 9 and float(parameters[i + 1]) < 0.0:
            # 風速
            return False
        if i == 10 and float(parameters[i + 1]) <= -90.0:
            # 溫度
            return False
        if i == 11 and float(parameters[i + 1]) < 0.0:
            # 溼度
            return False
        if i == 12 and float(parameters[i + 1]) < 0.0:
            # 氣壓
            return False
    return True


def main():
    start_time = datetime(2016, 2, 1, 0, 0)
    end_time = datetime(2016, 7, 1, 0, 0)
    station_name = sys.argv[1]
    station_id = Station.get_station_id(start_time, station_name)

    lead_time_str = sys.argv[2]
    lead_time = int(lead_time_str) // 10 * 10

    selection_method = sys.argv[3]
    if selection_method == 'split':
        # 依筆數從中切開，前半作訓練、後半作測試
        pass
    elif selection_method == 'rotation':
        # 每筆輪流作訓練、測試
        pass
    else:
        exit(1)

    do_delta = sys.argv[4]
    if do_delta == 'delta':
        # 要作變化量
        pass
    elif do_delta == 'no_delta':
        # 不作變化量
        pass
    else:
        exit(1)

    include_parameters_raw = sys.argv[5].split('.')
    include_parameters = []
    for n in include_parameters_raw:
        include_parameters.append(int(n))

    intermediate_file = open("%s-raw" % station_id, 'r')
    train_file = open("%s-%s-%s-%s-%s-train" % (station_id, lead_time_str, selection_method, do_delta, sys.argv[5]), 'w')
    test_file = open("%s-%s-%s-%s-%s-test" % (station_id, lead_time_str, selection_method, do_delta, sys.argv[5]), 'w')

    data = {}
    while True:
        line = intermediate_file.readline()
        if line == '':
            break

        line = line[:-1]
        parameters = line.split(' ')
        timestamp = parameters[0]
        timestamp = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:00")
        parameters = parameters[1:]

        is_valid = is_record_valid(parameters, include_parameters)

        if is_valid:
            data[timestamp] = parameters

    data = OrderedDict(sorted(data.items(), key=lambda t: t[0]))

    # 建立資料樣本
    sample = []
    for key in data:
        keys = [key + timedelta(0, 0, 0, 0, lead_time), key]
        if do_delta == 'delta':
            keys.append(key - timedelta(0, 0, 0, 0, 10))
            keys.append(key - timedelta(0, 0, 0, 0, 30))
            keys.append(key - timedelta(0, 0, 0, 0, 60))

        is_valid = True
        for keys_index in range(len(keys)):
            if keys[keys_index] in data:
                keys[keys_index] = data[keys[keys_index]]
            else:
                is_valid = False
                keys[keys_index] = None
        if not is_valid:
            continue

        if float(keys[0][0]) > 0.0:
            save_list = [2]
        else:
            save_list = [1]

        for j in include_parameters:
            j += 1
            save_list.append(float(keys[1][j]))
            if do_delta == 'delta':
                for k in range(len(keys)):
                    if k < 2:
                        continue
                    value = float(keys[1][j]) - float(keys[k][j])
                    save_list.append(value)

        output_count = 0
        output_str = ''
        for save_item in save_list:
            if output_count > 0:
                output_str += " %s:" % str(output_count)

            output_str += str(round(save_item, 2))

            output_count += 1
        sample.append(output_str)

    count = len(sample)
    test_count = count // 2
    train_count = count - test_count
    train_sample = {}
    test_sample = {}

    for i in range(len(sample)):
        output = None
        if selection_method == 'split':
            if i < train_count:
                output = train_sample
            else:
                output = test_sample
        else:
            if i % 2 == 0:
                output = train_sample
            else:
                output = test_sample

        result = sample[i][0:sample[i].index(' ')]
        if result not in output:
            output[result] = []
        output[result].append(sample[i])

    # 先統計訓練樣本各類型總數最少的數量
    count = -1
    for key in train_sample:
        class_count = len(train_sample[key])
        if count == -1:
            count = class_count
        count = min(count, class_count)

    # 從訓練樣本所有類型取相同數量寫入檔案
    for key in train_sample:
        for i in range(count):
            next_index = random.randrange(len(train_sample[key]))
            train_file.write(train_sample[key].pop(next_index))
            train_file.write('\n')

    for key in test_sample:
        for value in test_sample[key]:
            test_file.write(value)
            test_file.write('\n')

    train_file.flush()
    test_file.flush()

    intermediate_file.close()
    train_file.close()
    test_file.close()

main()
