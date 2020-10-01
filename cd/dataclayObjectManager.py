from dataclay.api import init, finish

init()

from CityNS.classes import *

from geolib import geohash
PRECISION = 7

class DataclayObjectManager:
    objectsDKB = None
    
    def __init__(self, alias):
        self.objectsDKB = DKB.get_by_alias(alias)

    # TODO: delete it once geohash making it inside dataclay object model
    def _add_geohash(self, objectTuple):
        obj = Object.get_by_alias(str(objectTuple[0]))
        history = obj.get_events_history()
        last_long = history[0][len(history[0]) - 1]
        last_lat = history[1][len(history[1]) - 1]
        object_geohash = geohash.encode(last_lat, last_long, PRECISION)
        return objectTuple + (object_geohash, )

    def getObjects(self, limit=None):
        _objects = self.objectsDKB.get_objects_from_dkb()
        objects = []
        for obj in _objects:
            objects.append(self._add_geohash(obj))

        if limit:  #TODO: to be removed. needed for debugging
            return objects[:limit]

        return objects

    def alertCollision(self, v_main, v_other, col):
        print(f"----------------------------------------")
        print(f"WARNING!!! Possible collision detected")
        print(f"  v_main: {v_main} v_other: {v_other}")
        print(f"    x: {col[0]} y: {col[1]} t: {col[2]}")
        print(f"----------------------------------------")
