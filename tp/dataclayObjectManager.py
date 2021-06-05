from dataclay.api import init, finish
from collections import deque
init()
from tp.v3TP_new import QUAD_REG_LEN_DICT, QUAD_REG_MIN_DICT
from dataclay import getRuntime
from dataclay.api import get_backend_id_by_name
from CityNS.classes import uuid
from CityNS.classes import DKB

class DataclayObjectManager:
    KB = None
    
    def __init__(self, alias="DKB"):
        print("in DataclayObjectManager.__init__")
        self.backend_id = get_backend_id_by_name("DS1")
        print("1")
        try:
            print(2)
            self.KB = DKB.get_by_alias(alias)
            print(3)
        except Exception:
            print(4)
            self.KB = DKB()
            print(5)
            self.KB.cloud_backend_id = self.backend_id
            print(6)
            self.KB.make_persistent(alias="DKB")
            print(7)
        print("after DataclayObjectManager.__init__")

    def get_dummy_objects(self):
        return [42]
#        return [['cbe71526-d6bd-435e-a989-83152aa11fe1:9c928e62-75e6-4e19-a5d3-5a465f06c9f3', [], [], [], 'dnpz7ck', [[35.031355404187224, 35.031352428636616, 35.031350444100944, 35.03134904392341, 35.031347991189904, 35.03134714609026, 35.031359071211966, 35.03136996353651, 35.031377201183496, 35.03138157725674, 35.0313841908153, 35.03138589644434, 35.031388673149465, 35.031390453384425, 35.03139001789305, 35.03139147862476, 35.0313923821388, 35.03139294286909, 35.03137328746597, 35.031383245337736, 35.03136961404745, 35.03138078235282, 35.031387682265766, 35.03139177380347, 35.0313940679391, 35.031394127084155, 35.03139408957237, 35.03139401477817, 35.031393921003044, 35.031393812347424, 35.031393688759835, 35.031393549036835, 35.031391826434934, 35.0313922160606, 35.03139236920287, 35.03139235917077, 35.03139327282966, 35.03139377323227, 35.03137688555011, 35.031364597121055], [-78.93070694989784, -78.93070416833498, -78.93070250784389, -78.9307014219754, -78.93070060866096, -78.93069990244442, -78.93071352067842, -78.93072559270428, -78.93073264134397, -78.93073564687593, -78.93073664603195, -78.93073689390744, -78.9307377505122, -78.93073790926208, -78.93073696668392, -78.93073725845566, -78.93073724966709, -78.93073711262944, -78.93072040093806, -78.93072782937313, -78.9307162895327, -78.93072484764825, -78.93072995611352, -78.93073285346166, -78.93073438151778, -78.93073479603959, -78.93073508230964, -78.93073528413723, -78.9307354197485, -78.93073549959415, -78.93073553128248, -78.93073552083315, -78.93073474314168, -78.93073502422342, -78.93073511200889, -78.9307350691187, -78.9307352389141, -78.93073517996584, -78.93072147725161, -78.93071154473795], [1622024047624, 1622024047664, 1622024047704, 1622024047744, 1622024047784, 1622024047824, 1622024047864, 1622024047904, 1622024047944, 1622024047984, 1622024048024, 1622024048064, 1622024048104, 1622024048144, 1622024048184, 1622024048224, 1622024048264, 1622024048304, 1622024048344, 1622024048384, 1622024048424, 1622024048464, 1622024048504, 1622024048544, 1622024048584, 1622024048624, 1622024048664, 1622024048704, 1622024048744, 1622024048784, 1622024048824, 1622024048864, 1622024048904, 1622024048944, 1622024048984, 1622024049024, 1622024049064, 1622024049104, 1622024049144, 1622024049184]], '2405_14', 283, 27, 20]]

    def getAllObjectsIDs(self):
        res = []
        for obj in self.getAllObjects():
            res.append((obj[0], obj[7]))
        return res
 
    def getAllObjects(self):
        res = []
        objects = self.KB.get_objects(events_length_max=QUAD_REG_LEN_DICT, events_length_min=QUAD_REG_MIN_DICT)
        for obj in objects:
            lobj = list(obj)
            lobj[5] = [list(obj[5][0]), list(obj[5][1]), list(obj[5][2])]
            res.append(lobj)
        return res
    
    def getObject(self, oid):
        obj_id, class_id = oid.split(":")
        obj_id = uuid.UUID(obj_id)
        class_id = uuid.UUID(class_id)
        return getRuntime().get_object_by_id(obj_id, hint=self.backend_id, class_id=class_id)

    def storeResult(self, obj, fx, fy, ft, tp_timestamp, frame_tp):
        print(f"converting to regular lists? {type(fx)} {type(fy)} {type(ft)} ")
        obj.add_prediction(fx, fy, ft, tp_timestamp, frame_tp)

    def getResult(self, oid):
        obj = self.getObject(oid)
        return obj.trajectory_px, obj.trajectory_py, obj.trajectory_pt
