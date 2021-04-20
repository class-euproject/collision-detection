print("before imports")

import time

from cd.CD import collision_detection

from geolib import geohash
import paho.mqtt.client as mqtt

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

def detect_collision_centralized(objects_chunk, connected_cars):
    res = []
    print(f"PAIRS_NUM:{len(objects_chunk) * len(connected_cars)}")
    for my_object in objects_chunk:
      print(f"in detect_collision_centralized with {my_object}")
      cc_in_wa = _getConnectedCarsInWA(my_object, connected_cars)

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

def getLimitedNumberOfObjects(objects, limit):
    while len(objects) < limit:
        objects.extend(objects)

    return objects[:limit]
