print("before imports")

import os 
import time

import lithops

from cd.CD import collision_detection

from geolib import geohash
import paho.mqtt.client as mqtt

from cd.dataclayObjectManager import DataclayObjectManager

print("after imports")

def _is_collided(main_object, other_object):
    res = []
    if main_object[0] and main_object[1] and main_object[2] and other_object[0] and other_object[1] and other_object[2] and min(main_object[0])>-180 and max(main_object[0])<180 and min(other_object[0])>-180 and max(other_object[0])<180 and min(main_object[1])>-90 and min(other_object[1])>-90 and max(main_object[0])<90 and max(other_object[1])<90 and (max(main_object[0])-min(main_object[0]))<2 and (max(main_object[1])-min(main_object[1]))<2 and (max(other_object[0])-min(other_object[0]))<2 and (max(other_object[1])-min(other_object[1]))<2:
        print(f"before call collision_detection={main_object[4]}:{other_object[4]}")
        res = collision_detection(main_object, other_object)
        print(f"after call collision_detection={main_object[4]}:{other_object[4]}")
    return res

def _getConnectedCarsInWA(my_object, connected_cars_objects):
    res = []
    for cc in connected_cars_objects:
        if my_object[4] != cc[4] and (my_object[3] == cc[3] or my_object[3] in geohash.neighbours(cc[3])):
            res.append(cc)
    return res



def detect_collision_distributed_dc(objects_chunk, cc_num_limit, cc_ids):
    res = []
    print(f"in detect_collision_distributed_dc with {objects_chunk} --------")
    dm = DataclayObjectManager(alias='DKB')

    connected_cars = []
    if cc_ids:
        print(f"getting all cc objects from {cc_ids}")
        for cc_id in cc_ids:
            connected_cars.append(dm.getObject(cc_id))
    else:
        print(f"getting all cc object sin batch")
        connected_cars = dm.getAllObjects(with_tp=True, with_event_history=False)

    connected_cars = getLimitedNumberOfObjects(connected_cars, cc_num_limit)
    print(f"PAIRS_NUM:{len(objects_chunk) * len(connected_cars)}")

    for my_object in objects_chunk:
      obj = dm.getObject(my_object)
      my_object = (obj.trajectory_px, obj.trajectory_py, obj.trajectory_pt, obj.geohash, obj.id_object, obj.type)

      cc_in_wa = connected_cars
#      cc_in_wa = _getConnectedCarsInWA(my_object, connected_cars)

      for cc in cc_in_wa:
        start = time.time()
        collisions = _is_collided(my_object, cc)
        if collisions:
            my_id = my_object[4]
            ccid = cc[4]

            print(f"Collision detected, before mqtt={my_id}:{ccid}")
            time_detected = time.time()
            client=mqtt.Client()
            client.connect("192.168.7.42")

            client.publish("test",f"{my_id} {ccid} {collisions} {my_object[0]} {my_object[1]} {my_object[2]} {cc[0]} {cc[1]} {cc[2]}")
            print(f"Collision detected, after mqtt={my_id}:{ccid}")

            # push to car mqtt topic
            res.append((my_id, ccid, collisions))
    print(f"after for cc in cc_in_wa")

def publish_result(object0, object1):
    my_id = object0[4]
    ccid = object1[4]

    print(f"Collision detected, before mqtt={my_id}:{ccid}")
    time_detected = time.time()
    client=mqtt.Client()
    client.connect("192.168.7.42")

    client.publish("test",f"{my_id} {ccid} {collisions} {my_object[0]} {my_object[1]} {my_object[2]} {cc[0]} {cc[1]} {cc[2]}")
    print(f"Collision detected, after mqtt={my_id}:{ccid}")

def detect_collision_distributed_dc_pairs(pairs_chunk):
    res = []
    print(f"in  detect_collision_distributed_dc_pairs with {pairs_chunk} --------!!")
    dm = DataclayObjectManager(alias='DKB')

    print(f"PAIRS_NUM:{len(pairs_chunk)}")

    for pair in pairs_chunk:
        obj0 = dm.getObject(pair[0])
        obj1 = dm.getObject(pair[1])
        object0 = (obj0.trajectory_px, obj0.trajectory_py, obj0.trajectory_pt, obj0.geohash, obj0.id_object, obj0.type)
        object1 = (obj1.trajectory_px, obj1.trajectory_py, obj1.trajectory_pt, obj1.geohash, obj1.id_object, obj1.type)

        start = time.time()
        collisions = _is_collided(object0, object1)
        if collisions:
            publish_result(object0, object1)
        collisions = _is_collided(object1, object0)
        if collisions:
            publish_result(object1, object0)

    print(f"after for cc in cc_in_wa")

def getLimitedNumberOfObjects(objects, limit):
    while len(objects) < limit:
        objects.extend(objects)

    return objects[:limit]
