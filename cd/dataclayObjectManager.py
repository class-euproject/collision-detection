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
#        import pdb;pdb.set_trace()
        return self.objectsDKB.get_objects([], False, with_tp, connected)

    def getAllObjectsIDs(self):

        res = []

        for obj in self.objectsDKB.get_objects([], False, True, True):
            obj_id = getRuntime().get_object_id_by_alias(obj[4])
            class_id = 'b79a0fd1-ac91-41fe-b5c6-ff0a5b993a83'

            obj_id = uuid.UUID(obj_id)
            class_id = uuid.UUID(class_id)
            res.append(f'{obj_id}:{class_id}')

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
