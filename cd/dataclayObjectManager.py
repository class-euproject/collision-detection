from dataclay.api import init, finish

init()

from CityNS.classes import *

from geolib import geohash
PRECISION = 7

class DataclayObjectManager:
    objectsDKB = None
    
    def __init__(self, alias):
        self.objectsDKB = DKB.get_by_alias(alias)

#    def getObjectsRefs(self, limit=None):
#        # get latest snapshot
#        latestEventSnapshotID = len(self.objectsDKB.kb) - 1
#        if latestEventSnapshotID >= 0:
#            return self.objectsDKB.kb[latestEventSnapshotID].objects_refs[:limit]
#        return []

    def getObjectTuplesWithTp(self, with_tp=False, connected=False, limit=None):
        objects = self.objectsDKB.get_objects([], False, with_tp, connected)
        res = []
        for obj in objects:
            res.append((str(obj.id_object), obj.trajectory_px, obj.trajectory_py, obj.trajectory_pt, obj.geohash))  
            if limit and len(res) == limit:
                return res
        return res

    def getAllObjects(self, with_tp=False, connected=False):
        return self.objectsDKB.get_objects([], False, with_tp, connected)

    def covertObjectsWithTpToTuples(self, objects, limit=None):
        res = []
        for obj in objects:
            res.append((str(obj.id_object), obj.trajectory_px, obj.trajectory_py, obj.trajectory_pt, obj.geohash))
            if limit and len(res) == limit:
                return res
        return res
            
    def foo(self, objects_refs):
        res = []
        for obj_ref in objects_refs:
            obj = Object.get_by_alias(str(obj_ref))
            if obj.trajectory_px:
                res.append((str(obj_ref), obj.trajectory_px, obj.trajectory_py, obj.trajectory_pt, obj.geohash))
        return res

    def alertCollision(self, v_main, v_other, col):
        print(f"----------------------------------------")
        print(f"WARNING!!! Possible collision detected")
        print(f"  v_main: {v_main} v_other: {v_other}")
        print(f"    x: {col[0]} y: {col[1]} t: {col[2]}")
        print(f"----------------------------------------")
