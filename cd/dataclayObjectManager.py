from dataclay.api import init, finish

init()

from CityNS.classes import *

class DataclayObjectManager:
    objectsDKB = None
    
    def __init__(self, alias):
        self.objectsDKB = DKB.get_by_alias(alias) # to check

    def getObjects(self, limit=None):
        objects = self.objectsDKB.get_objects_from_dkb() # to check

        if limit:  #TODO: to be removed. needed for debugging
            return objects[:limit]

        return objects

    def alertCollision(self, v_main, v_other, col):
        print(f"----------------------------------------")
        print(f"WARNING!!! Possible collision detected")
        print(f"  v_main: {v_main} v_other: {v_other}")
        print(f"    x: {col[0]} y: {col[1]} t: {col[2]}")
        print(f"----------------------------------------")
