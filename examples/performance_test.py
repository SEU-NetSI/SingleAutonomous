import logging
from datetime import datetime

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.log import LogConfig
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.crazyflie.syncLogger import SyncLogger
from cflib.utils import uri_helper
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import json

# URI to the Crazyflie to connect to
uri = uri_helper.uri_from_env(default='radio://0/80/2M/E7E7E7E7E7')

# Only output errors from the logging framework
logging.basicConfig(level=logging.ERROR)

# storage
token = "nLbDMODq7DICXnSxlT0KK37ti1ZnQ_s4KakVBfFu--pQtrjQs3x6ENM6Xfxk8xN4vs9Aizrt5OMorizbzMwm0A=="
org = "seu"
bucket = "myinflux"

client = InfluxDBClient(url="http://localhost:8086", token=token)
write_api = client.write_api(write_options=SYNCHRONOUS)

def store(times, mv, level, length):
    try:
        time = datetime.utcnow()
        point = [Point("performance").tag("performance", "performance").field("mv", mv).time(time, WritePrecision.NS),
        Point("performance").tag("performance", "performance").field("times", times).time(time, WritePrecision.NS),
        Point("performance").tag("performance", "performance").field("level", level).time(time, WritePrecision.NS), 
        Point("performance").tag("performance", "performance").field("length", length).time(time, WritePrecision.NS)]
        write_api.write(bucket, org, point)
    except:
        print("Something unexpected happened.")

def simple_log(scf, logconf):

    with SyncLogger(scf, lg_stab) as logger:
        lastTimes = -1
        lastTimestamp = -1
        while(1):
            for log_entry in logger:
                timestamp = log_entry[0]
                data = log_entry[1]
                times = data["performance.times"]

                if lastTimes != times:
                    print('[%d]: %s - [%d]' % (timestamp, data, timestamp - lastTimestamp))
                    store(data["performance.times"], data["pm.vbatMV"], data["pm.batteryLevel"], timestamp - lastTimestamp)
                    lastTimes = data["performance.times"]
                    lastTimestamp = timestamp

                break

if __name__ == '__main__':
    # Initialize the low-level drivers
    cflib.crtp.init_drivers()

    lg_stab = LogConfig(name='Performance', period_in_ms=10)
    lg_stab.add_variable('pm.vbatMV', 'uint16_t')
    lg_stab.add_variable('performance.times', 'uint16_t')
    lg_stab.add_variable('pm.batteryLevel', 'uint8_t')



    with SyncCrazyflie(uri, cf=Crazyflie(rw_cache='./cache')) as scf:

        simple_log(scf, lg_stab)