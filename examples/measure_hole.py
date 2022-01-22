import sys
from datetime import datetime

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.utils.multiranger import Multiranger

from matplotlib import pyplot as plt
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie

from cflib.crazyflie.log import LogConfig
from cflib.crazyflie.syncLogger import SyncLogger
import time
import queue
import numpy as np
import math
URI = 'radio://0/80/2M'
MODE = "display"

if len(sys.argv) > 1:
    MODE = sys.argv[1]
if len(sys.argv) > 2:
    URI = sys.argv[2]

mycf = None
data = [[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]]

size = len(data)
map = {}
def setup():
    for i in range(size):
        for j in range(size):
            map[i * size + j] = (i, j)
    print(map)

def has_hole():
    count_one = 0.0
    count_two = 0.0
    count_three = 0.0
    count_four = 0.0

    for i in range(len(data)):
        for j in range(len(data)):
            if (i == 0 or i == 6) or (j == 0 or j == 6):
                count_one += data[i][j]
            elif (i == 1 or i == 5) or (j == 1 or j == 5):
                count_two += data[i][j]
            elif (i == 2 or i == 4) or (j == 2 or j == 4):
                count_three += data[i][j]
            elif (i == 3 or i == 3) or (j == 3 or j == 6):
                count_four += data[i][j]
    
    mean_one = count_one / (7 * 4 - 4)
    mean_two = count_two / (5 * 4 - 4)
    mean_three = count_three / (3 * 4 - 4)
    mean_four = count_four / 1

    if mean_one < mean_four:
        print("Center-hole detected\n")
        calculate_size(mean_one)
        # print(mean_one, mean_four)
        return True
    else:
        print("No center-hole detected\n")
        return False

def calculate_size(largest_circle):
    hole_size = 2 * 0.13 * largest_circle
    print("Hole size: " + str(hole_size) + "\n")

def display(distance, roiindex):
    # print(roiindex, distance, datetime.now().time())
    try:
        x = map.get(roiindex)[0]
        y = map.get(roiindex)[1]
        data[x][y] = round(distance * 100, 2)
    except:
        return
    # if roiindex < size * size - 1:
    #     return

    has_hole()
    
def cf_logger():
    setup()
    # Initialize the low-level drivers (don't list the debug drivers)
    cflib.crtp.init_drivers(enable_debug_driver=False)
    cf = Crazyflie(rw_cache='./cache')

    with SyncCrazyflie(URI, cf=cf) as scf:
        mycf = scf
        with Multiranger(scf, rate_ms=10) as multi_ranger:
            while True:
                display(multi_ranger.single, multi_ranger.roiindex)
                time.sleep(0.05)

if __name__ == '__main__':
    cf_logger()