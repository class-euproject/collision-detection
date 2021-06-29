print("before imports")

import time
import os

#from tp.dataclayObjectManager import DataclayObjectManager 
from tp.v3TP_new import traj_pred_v3


from tp.v3TP_new import QUAD_REG_LEN_DICT


import paho.mqtt.client as mqtt
print("after imports")

dm = None


def traj_pred_v2_wrapper(objects_chunk):
  try:
    print(" = ==================in new_traj_pred_v2_wrapper!!! ===============")
    print(f"with input: {objects_chunk}")
    global dm
    if not dm:
      print(f"creating DATAMANAGER INSTANce")
      from tp.dataclayObjectManager import DataclayObjectManager
      dm = DataclayObjectManager()
    print(f"objects in chunk: {len(objects_chunk)}")
    print(objects_chunk)
    print(objects_chunk[0])
    print('---')
    if isinstance(objects_chunk[0], int):
        print("steam up, return")
        time.sleep(0.3)
        return

    tps_results = []
    
    for objectTuple in objects_chunk:
        print(f"before dm.getObject: {objectTuple[0]}")

        # calculate trajectory by v2
        print(f"before traj_pred_v3:{objectTuple[0]}")
        fx, fy, ft = traj_pred_v3(objectTuple[5][0], objectTuple[5][1], objectTuple[5][2], objectTuple[8], objectTuple[9], objectTuple[6].split('_')[0])

        print(f"v_id: {objectTuple[0]} x: {fx} y: {fy} t: {ft}")

        tp_timestamp = objectTuple[5][2][-1]

        try:
            tps_results.append((objectTuple[0], fx, fy, ft, tp_timestamp, objectTuple[7]))
        except Exception as e:
            import traceback
            traceback.print_exc()
            print("Got some bad DC exception, ignoring")

            client=mqtt.Client()
            client.connect("192.168.7.42")
            client.publish("test", f"Got some bad DC exception, ignoring. AID: {os.environ['__OW_ACTIVATION_ID']}")

            print("----TP objects--------")
            print(f'fx: {fx} fy: {fy} ft: {ft}')

            print("----TP objects types--------")
            print(f'fx: {type(fx)} fy: {type(fy)} ft: {type(ft)}')

            print("----TP objects list items types--------")
            print(f'fx: {type(fx[0])} fy: {type(fy[0])} ft: {type(ft[0])}')

            print("----------------------------")


        print(f"after dm.storeResult:{objectTuple[0]}")

    print(f"storing results: {tps_results}")
    dm.storeBulkResult(tps_results)
    print(" = ==================out traj_pred_v2_wrapper ===============")
  except Exception as e:
    print("Got exception")
    client=mqtt.Client()
    client.connect("192.168.7.42")
    client.publish("test", f"Got an unknown exception in TP, raising. AID: {os.environ['__OW_ACTIVATION_ID']}")
    raise e
