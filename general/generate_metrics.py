#!/usr/bin/python3
# -*- coding: UTF-8 -*-
#

import json
# import random
from datetime import datetime, timedelta
import numpy as np


def normal(x, mu, sigma):
    return (2. * np.pi * sigma ** 2.) \
        ** -.5 * np.exp(-.5 * (x - mu) ** 2. / sigma ** 2.)


now = datetime.now()
oneHourAgo = now - timedelta(hours=1)
nowUnixTime = now.timestamp()
ohaUnixTime = oneHourAgo.timestamp()

metricDict = {"dimensions": {}, "links": [], "collection": []}

# print("now: ", now)
# print("oneHourAgo: ", oneHourAgo)
# print("nowUnixTime: ", nowUnixTime)
# print("ohaUnixTime: ", ohaUnixTime)
# print("-------")
count = -30
mu, sigma = 0., 10.

for metricTime in range(int(nowUnixTime) * 1000,
                        int(ohaUnixTime) * 1000,
                        -60000):
    # print("metricTime: ", metricTime)
    count += 1
    # value = random.randint(0, 10)
    metricValue = round(normal(count, mu, sigma) * 1000 + 50, 3)
    metricElement = {"timestamp": metricTime,
                     "value": metricValue,
                     "links": []}
    metricDict["collection"].append(metricElement)
print(json.dumps(metricDict, indent=2))

# data format
#
# {
#   "dimensions": {},
#   "links": [],
#   "collection": [
#     {
#       "timestamp": 1613498720000,
#       "value": 36.206588509610626,
#       "links": []
#     },
# ...
