import logging
import sys
import time
import json

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.utils.multiranger import Multiranger

URI = 'radio://0/25/2M'

if len(sys.argv) > 1:
    URI = sys.argv[1]

# Only output errors from the logging framework
logging.basicConfig(level=logging.ERROR)


logger = logging.getLogger()
logger.setLevel(logging.WARNING)
formatter = logging.Formatter(
    '%(message)s')

fh = logging.FileHandler(str(int(time.time() * 1000)) + '_distance.json')
fh.setLevel(logging.WARNING)
fh.setFormatter(formatter)

ch = logging.StreamHandler()
ch.setLevel(logging.WARNING)
ch.setFormatter(formatter)

logger.addHandler(ch)
logger.addHandler(fh)

logging.warning("[")


if __name__ == '__main__':
    # Initialize the low-level drivers (don't list the debug drivers)
    cflib.crtp.init_drivers(enable_debug_driver=False)

    cf = Crazyflie(rw_cache='./cache')
    with SyncCrazyflie(URI, cf=cf) as scf:
        with Multiranger(scf) as multi_ranger:
            keep_testing = True

            while keep_testing:
                item = {
                    "front": multi_ranger.front,
                    "back": multi_ranger.back,
                    "left": multi_ranger.left,
                    "right": multi_ranger.right,
                    "up": multi_ranger.up
                }
                logging.warning(json.dumps(item)+",")
                print(item)
        
                time.sleep(1)

        print('Demo terminated!')