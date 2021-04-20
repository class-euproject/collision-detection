from dataclay.api import init, finish

init()

from CityNS.classes import DKB
from CityNS.classes import uuid

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
        

        for obj in self.objectsDKB.get_objects([], False, True, False):

            obj_id = getRuntime().get_object_id_by_alias(obj[4])
            class_id = 'b79a0fd1-ac91-41fe-b5c6-ff0a5b993a83'

#            obj_id = uuid.UUID(obj_id)
#            class_id = uuid.UUID(class_id)
#            res.append(f'{str(obj_id)}:{class_id}')
#            res.append(obj[4])

        print(res)

        return ['c6a40ff3-58ef-4dd6-8ae6-0e50e7be01cb:b79a0fd1-ac91-41fe-b5c6-ff0a5b993a83', '65fb542a-bc97-45cd-a0fe-ee1856567ff1:b79a0fd1-ac91-41fe-b5c6-ff0a5b993a83', 'adb2e31d-833b-4d22-9201-ee85240368cd:b79a0fd1-ac91-41fe-b5c6-ff0a5b993a83', 'ce31cb7f-1df1-4df4-b9ee-5a20ecbe3d38:b79a0fd1-ac91-41fe-b5c6-ff0a5b993a83', '6ecd72b9-849b-4c22-8fd2-6a7ff2bfa881:b79a0fd1-ac91-41fe-b5c6-ff0a5b993a83', '0e5721d4-48d2-4635-9976-21566e23388f:b79a0fd1-ac91-41fe-b5c6-ff0a5b993a83', '4214749f-2af0-4761-9f08-22eded6303f3:b79a0fd1-ac91-41fe-b5c6-ff0a5b993a83', 'd1ad2b37-c799-43b6-86d6-e5ffbdf60c2e:b79a0fd1-ac91-41fe-b5c6-ff0a5b993a83', '4b4ef304-20f9-4d59-af6c-2073abba00c1:b79a0fd1-ac91-41fe-b5c6-ff0a5b993a83', 'cbc4932c-73d9-4008-b4e6-ae7a8c22d31c:b79a0fd1-ac91-41fe-b5c6-ff0a5b993a83', '219a6aa1-9f7f-4846-be9c-b13cc4f59d2e:b79a0fd1-ac91-41fe-b5c6-ff0a5b993a83', '08494182-faaf-4233-a872-f4f51b96e585:b79a0fd1-ac91-41fe-b5c6-ff0a5b993a83', '9be0730a-30c4-43b1-af83-b8739720c429:b79a0fd1-ac91-41fe-b5c6-ff0a5b993a83', '4052f93c-ca54-4bcb-9d9a-143aacb4d6c9:b79a0fd1-ac91-41fe-b5c6-ff0a5b993a83', 'f30b7051-dd34-4a50-af2a-175c555a9f3b:b79a0fd1-ac91-41fe-b5c6-ff0a5b993a83', '1e1fceeb-d99a-4c03-b03a-f44dfbfbb0d8:b79a0fd1-ac91-41fe-b5c6-ff0a5b993a83', '5671d570-1aa3-4021-ae10-5517900efad9:b79a0fd1-ac91-41fe-b5c6-ff0a5b993a83', '5024ab5b-db70-4f79-a131-3fbce7f69e20:b79a0fd1-ac91-41fe-b5c6-ff0a5b993a83', 'f0d4895e-1556-4ce5-babd-561c282df0b1:b79a0fd1-ac91-41fe-b5c6-ff0a5b993a83', '18deab07-daad-479f-9294-cfe19e9b51f6:b79a0fd1-ac91-41fe-b5c6-ff0a5b993a83', '313bcd69-eb52-48fd-b1ae-c5ab0df0e067:b79a0fd1-ac91-41fe-b5c6-ff0a5b993a83']

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
