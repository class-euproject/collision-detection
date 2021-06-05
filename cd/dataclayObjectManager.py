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
        self.backend_id = get_backend_id_by_name("DS1")

        try:
            self.KB = DKB.get_by_alias(alias)
        except Exception:
            self.KB = DKB()
            self.KB.cloud_backend_id = self.backend_id
            self.KB.make_persistent(alias="DKB")

        self.objectsDKB = DKB.get_by_alias(alias)
        self.backend_id = get_backend_id_by_name("DS1")

    def get_dummy_objects(self):
        return [([35.03100107347143, 35.03101945302576, 35.03104596715896, 35.03108061587101, 35.03112339916193], [-78.93056656648699, -78.93057797939056, -78.93059476964628, -78.93061693725413, -78.93064448221412], [1622024043464, 1622024044464, 1622024045464, 1622024046464, 1622024047464], 'dnpz7ch', '2405_11', 'car')]

    def getAllObjects(self, with_tp=True, connected=False, with_event_history=False):
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

        return ['0bd030a1-b220-451b-91e2-491e440e9824:649420f0-98bb-4a7f-b9e9-cfb3a5d1683c', '6c2cfffd-305c-4fcc-a17a-617a87e132c8:649420f0-98bb-4a7f-b9e9-cfb3a5d1683c', '6bbff6d3-1717-4d2d-a3e4-b10323b13114:649420f0-98bb-4a7f-b9e9-cfb3a5d1683c', '34082340-8c92-4d20-ad89-06e82c73ad84:649420f0-98bb-4a7f-b9e9-cfb3a5d1683c', '2d7d973c-843c-447a-bc74-7875baafd9c0:649420f0-98bb-4a7f-b9e9-cfb3a5d1683c', 'b1dd4284-151b-4450-9fa3-512e10dbe8d4:649420f0-98bb-4a7f-b9e9-cfb3a5d1683c', 'facbae07-3ace-4f37-8842-456e4cd8690e:649420f0-98bb-4a7f-b9e9-cfb3a5d1683c', 'd4b23a92-00c3-4c2b-88f0-53db534d4996:649420f0-98bb-4a7f-b9e9-cfb3a5d1683c', 'fb480175-5760-47f8-b5e3-cf84086b5a0b:649420f0-98bb-4a7f-b9e9-cfb3a5d1683c', 'a10d0c53-9fba-4bfa-bf5b-1149f2b7d241:649420f0-98bb-4a7f-b9e9-cfb3a5d1683c', 'fd12a19f-d166-47fe-9554-51bcd62cbe32:649420f0-98bb-4a7f-b9e9-cfb3a5d1683c', 'ce7dc91c-d19e-420d-af9f-688b39f4095f:649420f0-98bb-4a7f-b9e9-cfb3a5d1683c', 'b5c76764-6063-47c0-8beb-478f5e54d722:649420f0-98bb-4a7f-b9e9-cfb3a5d1683c', '342c1146-2a9c-4b10-886e-600a46eb8657:649420f0-98bb-4a7f-b9e9-cfb3a5d1683c', '68d921fc-2e5d-4aff-882e-34a4ca2ed674:649420f0-98bb-4a7f-b9e9-cfb3a5d1683c', '9dc4914b-0894-4a21-a9fa-e10648830c42:649420f0-98bb-4a7f-b9e9-cfb3a5d1683c', 'f238215c-785a-4ded-86d7-eda82104ef86:649420f0-98bb-4a7f-b9e9-cfb3a5d1683c', '326b6e4d-d6cc-421a-88f0-7a8d2afad3ea:649420f0-98bb-4a7f-b9e9-cfb3a5d1683c', '3023b5ea-8000-40a1-8924-d5548005d294:649420f0-98bb-4a7f-b9e9-cfb3a5d1683c', 'da54ed26-580a-49f5-83a5-f998aa3e3c19:649420f0-98bb-4a7f-b9e9-cfb3a5d1683c', '4aba55b7-d7a7-4b15-b280-7788504d6567:649420f0-98bb-4a7f-b9e9-cfb3a5d1683c'] 

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
