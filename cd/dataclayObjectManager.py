from dataclay.api import init, finish

init()

from CityNS.classes import DKB

from geolib import geohash

from dataclay import getRuntime
from dataclay.api import get_backend_id_by_name


class DataclayObjectManager:
    objectsDKB = None
    
    def __init__(self, alias):
        self.objectsDKB = DKB.get_by_alias(alias)
        self.backend_id = get_backend_id_by_name("DS1")

    def getAllObjects(self, with_tp=False, connected=False, with_event_history=True):
        objects = self.objectsDKB.get_objects([], False, with_tp, connected)
        if with_event_history:
            return objects
        else:
            res = []
            for obj in objects:
                res.append(obj[1:5] + obj[6:])
            return res

    def getObject(self, oid):
        obj_id, class_id = oid.split(":")
        obj_id = uuid.UUID(obj_id)
        class_id = uuid.UUID(class_id)
        return getRuntime().get_object_by_id(obj_id, hint=self.backend_id, class_id=class_id)

    def alertCollision(self, v_main, v_other, col):
        print(f"----------------------------------------")
        print(f"WARNING!!! Possible collision detected")
        print(f"  v_main: {v_main} v_other: {v_other}")
        print(f"    x: {col[0]} y: {col[1]} t: {col[2]}")
        print(f"----------------------------------------")
