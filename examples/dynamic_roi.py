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
URI = 'radio://0/80/2M'
MODE = "display"

if len(sys.argv) > 1:
    MODE = sys.argv[1]
if len(sys.argv) > 2:
    URI = sys.argv[2]
    
# hard code: data only


# data = [[0.0, 0.0, 0.0, 0.0],[0.0, 0.0, 0.0, 0.0],[0.0, 0.0, 0.0, 0.0],[0.0, 0.0, 0.0, 0.0]]
# data = [[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
# [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
# [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
# [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]]
data = [[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]]


size = len(data)
map = {}

# display
plt.ion()
plt.show()
fig, ax = plt.subplots()

def setup():
    for i in range(size):
        for j in range(size):
            map[i * size + j + 1] = (i, j)
    map[0] = (size - 1, size - 1)
    print(map)


def display(front, roiindex):
    print(roiindex, front, datetime.now().time())
    try:
        x = map.get(roiindex)[0]
        y = map.get(roiindex)[1]
        data[x][y] = round(front * 100, 2)
    except:
        return
    
    if roiindex < size * size - 1:
        return
    plt.cla()
    im = ax.imshow(data)
    # for i in range(size):
    #     for j in range(size):
    #         text = ax.text(j, i, data[i][j], ha="center", va="center", color="w")
    plt.draw()
    plt.pause(0.001)


# storage
token = "nLbDMODq7DICXnSxlT0KK37ti1ZnQ_s4KakVBfFu--pQtrjQs3x6ENM6Xfxk8xN4vs9Aizrt5OMorizbzMwm0A=="
org = "seu"
bucket = "myinflux"

client = InfluxDBClient(url="http://localhost:8086", token=token)
write_api = client.write_api(write_options=SYNCHRONOUS)

def store(distance, roiindex):
    try:
        point = Point("mem").tag("roiindex", "%02d" % roiindex).field("distance", round(distance * 100, 2)).time(datetime.utcnow(), WritePrecision.NS)    
        write_api.write(bucket, org, point)
    except:
        print("Something unexpected happened.")
    print(distance, roiindex)
    

def old_logger():
    setup()
    # Initialize the low-level drivers (don't list the debug drivers)
    cflib.crtp.init_drivers(enable_debug_driver=False)
    cf = Crazyflie(rw_cache='./cache')

    with SyncCrazyflie(URI, cf=cf) as scf:
        with Multiranger(scf, rate_ms=10) as multi_ranger:
            while True:
                if MODE == "display":
                    display(multi_ranger.single, multi_ranger.roiindex)
                elif MODE == "store":
                    store(multi_ranger.single, multi_ranger.roiindex)
                else:
                    print("MODE SELECTION ERROR")

                # time.sleep(1)

def simple_log_async(scf, logconf):
    cf = scf.cf
    cf.log.add_config(logconf)
    logconf.data_received_cb.add_callback(log_stab_callback)
    logconf.start()
    time.sleep(5)
    logconf.stop()

def log_stab_callback(timestamp, data, logconf):
    print('[%d][%s]: %s' % (timestamp, logconf.name, data))
    
def new_logger():
    setup()
    cflib.crtp.init_drivers()
    lg_stab = LogConfig(name='multiranger', period_in_ms=10)
    lg_stab.add_variable('range.single', 'float')
    lg_stab.add_variable('range.roiindex', 'float')
    with SyncCrazyflie(URI, cf=Crazyflie(rw_cache='./cache')) as scf:

        simple_log_async(scf, lg_stab)

if __name__ == '__main__':
    old_logger()