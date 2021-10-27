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
    

data = [[0.0, 0.0, 0.0, 0.0],[0.0, 0.0, 0.0, 0.0],[0.0, 0.0, 0.0, 0.0],[0.0, 0.0, 0.0, 0.0]]
map = {
    0: (0, 0),
    1: (0, 1),
    2: (0, 2),
    3: (0, 3),
    4: (1, 0),
    5: (1, 1),
    6: (1, 2),
    7: (1, 3),
    8: (2, 0),
    9: (2, 1),
    10: (2, 2),
    11: (2, 3),
    12: (3, 0),
    13: (3, 1),
    14: (3, 2),
    15: (3, 3)
}

# display
plt.ion()
plt.show()
fig, ax = plt.subplots()

def display(front, roiindex):
    plt.cla()
    print(roiindex)
    try:
        x = map.get(roiindex)[0]
        y = map.get(roiindex)[1]
        data[x][y] = round(front * 100, 2)
    except:
        return
    
    print(data)
    im = ax.imshow(data)
    for i in range(4):
        for j in range(4):
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

def store(distance_front, roiindex_front):
    try:
        point = Point("mem").tag("roiindex_front", roiindex_front).field("distance_front", round(distance_front * 100, 2)).time(datetime.utcnow(), WritePrecision.NS)    
        write_api.write(bucket, org, point)
    except:
        print("Something unexpected happened.")
    print(distance_front, roiindex_front)
    

if __name__ == '__main__':
    # Initialize the low-level drivers (don't list the debug drivers)
    cflib.crtp.init_drivers(enable_debug_driver=False)
    cf = Crazyflie(rw_cache='./cache')

    with SyncCrazyflie(URI, cf=cf) as scf:
        with Multiranger(scf) as multi_ranger:
            while True:
                if MODE == "display":
                    display(multi_ranger.front, multi_ranger.roiindex)
                elif MODE == "store":
                    store(multi_ranger.front, multi_ranger.roiindex)
                else:
                    print("MODE SELECTION ERROR")

                # time.sleep(1)
