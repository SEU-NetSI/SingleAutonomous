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
URI = 'radio://0/80/2M'
MODE = "display"

if len(sys.argv) > 1:
    MODE = sys.argv[1]
if len(sys.argv) > 2:
    URI = sys.argv[2]

mycf = None
data = [0] * 16
last_mean = 0
covQueue = queue.Queue(maxsize=5)

def calculate_mean():
    mean = np.mean(data)
    print("[Mean]" + str(mean))
    if last_mean != 0 and mean - last_mean > 5:
        cf_up()
        cf_front()
    else:
        cf_up()

def cf_up():
    print("[Up]5cm")

def cf_front():
    print("[Front]20cm")

def calculate_vari():
    vari = np.std(data)
    print("[Vari]" + str(vari))

def calculate_cov():
    covQueue.put(data)
    if covQueue._qsize() < 5:
        return
    else:
        cov = np.corrcoef(list(covQueue.queue))
        print(cov)

def display(distance, roiindex):
    # print(roiindex, distance, datetime.now().time())
    try:
        data[roiindex] = round(distance * 100, 2)
    except:
        return
    if roiindex < 15:
        return

    calculate_mean()
    # calculate_vari()
    # calculate_cov()
    
def cf_logger():
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