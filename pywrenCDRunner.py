from dataclay.api import init, finish
from collections import deque

import os 
import time

init()

from CityNS.classes import *

import pywren_ibm_cloud as pywren

from cd.dataclayObjectManager import DataclayObjectManager
from cd.CD import collision_detection

from geolib import geohash
import random

import time

# needed for debugging
BEGIN = time.time()
start = BEGIN

def timeConsumed(name):
    global start
    print(f'{name} time: {time.time() - start}, current time: {time.time()}')
    start = time.time()
##############




# TODO:
# either return from dataclay only relevant data (to optimize times)
# or move this filtering logic down to cd.CD.collision_detection()
def _is_collided(main_object, other_object):
    res = []
    if main_object[1] and main_object[2] and main_object[3] and other_object[1] and other_object[2] and other_object[3] and min(main_object[1])>-180 and max(main_object[1])<180 and min(other_object[1])>-180 and max(other_object[1])<180 and min(main_object[2])>-90 and min(other_object[2])>-90 and max(main_object[1])<90 and max(other_object[2])<90 and (max(main_object[1])-min(main_object[1]))<2 and (max(main_object[2])-min(main_object[2]))<2 and (max(other_object[1])-min(other_object[1]))<2 and (max(other_object[2])-min(other_object[2]))<2:
        print("before collision_detection(main_object,other_object)")
        res = collision_detection(main_object,other_object)
        print("after collision_detection(main_object,other_object)")
    return res

# TODO: delete this method, all_objects object should actually contain connected cars only
def _getConnectedCarsInWA(my_object, connected_cars_objects):
    res = []
    for cc in random.choices(connected_cars_objects, k=5): #TODO: currently dummy limit of MAX 5 random vehicles
        if my_object[4] == cc[4] or my_object[4] in geohash.neighbours(cc[4]):
            res.append(cc)
    return res

# should it be called from pywren map or just a single OW function?!
# how the result should be processed?
def detect_collision(my_object, all_objects):
    print("in detect_collision with: {} and cc_in_wa {}".format(my_object, all_objects))

    cc_in_wa = _getConnectedCarsInWA(my_object, all_objects)

    res = []
    for cc in cc_in_wa:
        if _is_collided(my_object, cc):
            print(">>> Collision with connected car {} detected".format(cc[0]))
            if cc[0] not in res:
                res.append(cc[0])

    return res

def run(params=[]):

    timeConsumed("start")   #TODO: to be removed. needed for debugging

    pw = pywren.function_executor()
    timeConsumed("pw_executor")   #TODO: to be removed. needed for debugging
    if 'ALIAS' not in params:  #TODO: to be removed. needed for debugging
        print("Params %s missing ALIAS parameter" % params)
        exit()

    alias = params['ALIAS']
    print("ALIAS: %s" % alias)

    dm = DataclayObjectManager(alias=alias)
    timeConsumed("DataclayVehicleManager")   #TODO: to be removed. needed for debugging

    if 'LIMIT' in params:  #TODO: to be removed. needed for debugging
        limit = int(params['LIMIT'])  #TODO: to be removed. needed for debugging

    objects = dm.getObjects(limit)
    kwargs = []
    for obj in objects:
        kwargs.append({'my_object': obj})

    pw.map(detect_collision, kwargs, extra_args={'all_objects': objects})
    timeConsumed("pw.map")

    pw.wait(download_results=False, WAIT_DUR_SEC=0.015)
    timeConsumed("pw.wait")

    return {"finished": "true"}

if __name__ == '__main__':
    limit = 1
    if len(sys.argv) > 1:
        limit = sys.argv[1]
    run(params={"LIMIT": limit, "ALIAS" : "DKB"})
