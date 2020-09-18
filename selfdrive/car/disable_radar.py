#!/usr/bin/env python3
import traceback

from tqdm import tqdm

import cereal.messaging as messaging
from panda.python.uds import NegativeResponseError
from selfdrive.car.isotp_parallel_query import IsoTpParallelQuery
from selfdrive.swaglog import cloudlog

RADAR_ADDR = 0x7D0
EXT_DIAG_REQUEST = b'\x10\x03'
EXT_DIAG_RESPONSE = b'\x50\x03'
COM_CONT_REQUEST = b'\x28\x83\x03'
COM_CONT_RESPONSE = b''

def disable_radar(logcan, sendcan, bus, i, timeout=0.1, retry=5, debug=True):
  print(f"radar disable {hex(RADAR_ADDR)} ...")
  for i in range(retry):
    try:
      # enter extended diagnostic session
      query = IsoTpParallelQuery(sendcan, logcan, bus, [RADAR_ADDR], [i], [EXT_DIAG_RESPONSE], debug=debug)
      for addr, dat in query.get_data(timeout).items():
        print("radar communication control disable tx/rx ...")
        # communication control disable tx and rx
        query = IsoTpParallelQuery(sendcan, logcan, bus, [RADAR_ADDR], [i], [COM_CONT_RESPONSE], debug=debug)
        query.get_data(0)
        return True
      print(f"radar disable retry ({i+1}) ...")
    except Exception:
      cloudlog.warning(f"radar disable exception: {traceback.format_exc()}")

  return False


if __name__ == "__main__":
  import time
  sendcan = messaging.pub_sock('sendcan')
  logcan = messaging.sub_sock('can')
  time.sleep(1)

  l = list(range(0x10000))
  for i in l:
    disabled = disable_radar(logcan, sendcan, 2, i, debug=True)
    print(f"disabled: {disabled}")
