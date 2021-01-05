from dataclay.api import init, finish

init()

from CityNS.classes import *

from geolib import geohash
PRECISION = 7

class DataclayObjectManager:
    objectsDKB = None
    
    def __init__(self, alias):
        self.objectsDKB = DKB.get_by_alias(alias)

    def getAllObjects(self, with_tp=False, connected=False, with_event_history=True):
        objects = self.objectsDKB.get_objects([], False, with_tp, connected)
        if with_event_history:
            return objects
        else:
            res = []
            for obj in objects:
                res.append(obj[:5])
            return res

    def alertCollision(self, v_main, v_other, col):
        print(f"----------------------------------------")
        print(f"WARNING!!! Possible collision detected")
        print(f"  v_main: {v_main} v_other: {v_other}")
        print(f"    x: {col[0]} y: {col[1]} t: {col[2]}")
        print(f"----------------------------------------")
