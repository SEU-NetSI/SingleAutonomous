import sys
from datetime import datetime

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.utils.multiranger import Multiranger

from matplotlib import pyplot as plt
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

URI = 'radio://0/80/2M'
MODE = "display"

if len(sys.argv) > 1:
    MODE = sys.argv[1]
if len(sys.argv) > 2:
    URI = sys.argv[2]
    

# data = [[0.0, 0.0, 0.0, 0.0],[0.0, 0.0, 0.0, 0.0],[0.0, 0.0, 0.0, 0.0],[0.0, 0.0, 0.0, 0.0]]
size = 8
data = [[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]]
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
    plt.cla()
    print(roiindex, front, datetime.now().time())
    try:
        x = map.get(roiindex)[0]
        y = map.get(roiindex)[1]
        data[x][y] = round(front * 100, 2)
    except:
        return
    
    # print(data)
    im = ax.imshow(data)
    for i in range(size):
        for j in range(size):
            # text = ax.text(j, i, data[i][j], ha="center", va="center", color="w")
            text = ax.text(j, i, data[i][j], ha="center", va="center", color="w")
    # plt.matshow(data)
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
        point = Point("mem").tag("roiindex", roiindex).field("distance", round(distance * 100, 2)).time(datetime.utcnow(), WritePrecision.NS)    
        write_api.write(bucket, org, point)
    except:
        print("Something unexpected happened.")
    print(distance, roiindex)
    

if __name__ == '__main__':
    setup()
    # Initialize the low-level drivers (don't list the debug drivers)
    cflib.crtp.init_drivers(enable_debug_driver=False)
    cf = Crazyflie(rw_cache='./cache')

    with SyncCrazyflie(URI, cf=cf) as scf:
        with Multiranger(scf) as multi_ranger:
            while True:
                if MODE == "display":
                    display(multi_ranger.single, multi_ranger.roiindex)
                elif MODE == "store":
                    store(multi_ranger.single, multi_ranger.roiindex)
                else:
                    print("MODE SELECTION ERROR")

                # time.sleep(1)
