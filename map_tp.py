print("before imports")

import time

from tp.dataclayObjectManager import DataclayObjectManager 
from tp.v3TP import traj_pred_v3
from tp.v3TP import QUAD_REG_LEN_DICT


import paho.mqtt.client as mqtt
print("after imports")

def traj_pred_v2_wrapper(objects_chunk):
    print(" = ==================in traj_pred_v2_wrapper ===============")
    print(f"with input: {objects_chunk}")
    dm = DataclayObjectManager()
    print(f"objects in chunk: {len(objects_chunk)}")
    
    for objectTuple in objects_chunk:
        print(f"before dm.getObject: {objectTuple[0]}")
        obj = dm.getObject(objectTuple[0])
        # calculate trajectory by v2
        print(f"before traj_pred_v3:{objectTuple[0]}")
        fx, fy, ft = traj_pred_v3(objectTuple[5][0], objectTuple[5][1], objectTuple[5][2])

        print(f"v_id: {objectTuple[0]} x: {fx} y: {fy} t: {ft}")

        tp_timestamp = objectTuple[5][2][-1]
        dm.storeResult(obj, fx, fy, ft, tp_timestamp, objectTuple[7])
        print(f"after dm.storeResult:{objectTuple[0]}")

    print(" = ==================out traj_pred_v2_wrapper ===============")

def traj_pred_v2_distr(objects_chunk):
    print(" = ==================in traj_pred_v2_distr ===============")
    print(" with input: " + str(objects_chunk))
    dm = DataclayObjectManager()
    print(f"objects in chunk: {len(objects_chunk)}")

    for object_id_frame in objects_chunk:
      # geto object by id
      print(f"before dm.getObject: {object_id_frame[0]}")
      obj = dm.getObject(object_id_frame[0])
      events_history = obj.get_events_history(QUAD_REG_LEN_DICT[obj.type])

      print(f"before traj_pred_v3:{object_id_frame[0]}")
      # calculate trajectory by v2
      fx, fy, ft = traj_pred_v3(events_history[0], events_history[1], events_history[2])

      print(f"v_id: {object_id_frame[0]} x: {fx} y: {fy} t: {ft}")

      tp_timestamp = events_history[2][-1]
      dm.storeResult(obj, fx, fy, ft, tp_timestamp, object_id_frame[1])
      print(f"after dm.storeResult:{object_id_frame[0]}")
    print(" = ==================out traj_pred_v2_distr ===============")
