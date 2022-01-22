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
import random

URI = 'radio://0/80/2M'

data = [[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]]

size = len(data)
randomdraw = 0
map = {}

# display
plt.ion()
plt.show()
fig, ax = plt.subplots()


def display(front, roiindex):
    global randomdraw
    print(roiindex, front, datetime.now().time())
    try:
        x = map.get(roiindex)[0]
        y = map.get(roiindex)[1]
        data[x][y] = round(front * 100, 2)
    except:
        return
    
    if roiindex != randomdraw:
        return
    randomdraw = random.randint(0, size * size - 1)
    plt.cla()
    ax.imshow(data)
    for i in range(size):
        for j in range(size):
            ax.text(j, i, data[i][j], ha="center", va="center", color="w")
    plt.draw()
    plt.pause(0.001)


def setup():
    for i in range(size):
        for j in range(size):
            map[i * size + j] = (i, j)
    # map[0] = (size - 1, size - 1)
    print(map)


def start():
    setup()
    # Initialize the low-level drivers (don't list the debug drivers)
    cflib.crtp.init_drivers(enable_debug_driver=False)
    cf = Crazyflie(rw_cache='./cache')

    with SyncCrazyflie(URI, cf=cf) as scf:
        with Multiranger(scf, rate_ms=20) as multi_ranger:
            while True:
                display(multi_ranger.single, multi_ranger.roiindex)
                time.sleep(0.03)


if __name__ == '__main__':
    start()
