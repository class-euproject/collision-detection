print("before imports")

import os 
import time

import lithops

from cd.CD import collision_detection

from geolib import geohash
import paho.mqtt.client as mqtt

print("after imports")

# needed for debugging
#BEGIN = time.time()
#start = BEGIN

#def timeConsumed(name):
#    global start
#    print(f'{name} time: {time.time() - start}, current time: {time.time()}')
#    start = time.time()
##############

# either return from dataclay only relevant data (to optimize times)
# or move this filtering logic down to cd.CD.collision_detection()
def _is_collided(main_object, other_object):
    res = []
    if main_object[0] and main_object[1] and main_object[2] and other_object[0] and other_object[1] and other_object[2] and min(main_object[0])>-180 and max(main_object[0])<180 and min(other_object[0])>-180 and max(other_object[0])<180 and min(main_object[1])>-90 and min(other_object[1])>-90 and max(main_object[0])<90 and max(other_object[1])<90 and (max(main_object[0])-min(main_object[0]))<2 and (max(main_object[1])-min(main_object[1]))<2 and (max(other_object[0])-min(other_object[0]))<2 and (max(other_object[1])-min(other_object[1]))<2:
        print(f"before call collision_detection={main_object[4]}:{other_object[4]}")
        res = collision_detection(main_object, other_object)
        print(f"after call collision_detection={main_object[4]}:{other_object[4]}")
    return res

def _getConnectedCarsInWA(my_object, connected_cars_objects):
    res = []
    for cc in connected_cars_objects:
        if my_object[4] != cc[4] and (my_object[3] == cc[3] or my_object[3] in geohash.neighbours(cc[3])):
#            print("my_object[4] == cc[4] {}, my_object[4] in geohash.neighbours(cc[4]) {}".format(my_object[4] == cc[4], my_object[4] in geohash.neighbours(cc[4])))
            res.append(cc)
    return res

# should it be called from pywren map or just a single OW function?!
# how the result should be processed?
def detect_collision(objects_chunk, connected_cars):
    res = []
    print(f"PAIRS_NUM:{len(objects_chunk) * len(connected_cars)}")
    for my_object in objects_chunk:
#      print(f"in detect collision with {my_object}")
      cc_in_wa = _getConnectedCarsInWA(my_object, connected_cars)

      for cc in cc_in_wa:
        start = time.time()
        collisions = _is_collided(my_object, cc)
        if collisions:
            my_id = my_object[4]
            ccid = cc[4]

            print(f"Collision detected, before mqtt={my_id}:{ccid}")
            time_detected = time.time()
            client=mqtt.Client()
            client.connect("192.168.7.42")
            
#            dm = DataclayObjectManager(alias='DKB')
#            cc_obj = dm.getObject(cc[0])
#            my_obj = dm.getObject(my_object[0])
#            my_object += (my_obj.id_object,)
#            cc += (cc_obj.id_object,)
            
#            _my_object = my_object[1:5]
#            _cc = cc[1:5]
            client.publish("test",f"{my_id} {ccid} {collisions} {my_object[0]} {my_object[1]} {my_object[2]} {cc[0]} {cc[1]} {cc[2]}")
            print(f"Collision detected, after mqtt={my_id}:{ccid}")
#            client.publish("test","Collision of {} with connected car {} detected, COLLISION DATA {} ==== TRAJ1 {} ==== TRAJ2 {} ==== obj1 {} === obj2 {}".format(my_obj.id_object, cc_obj.id_object, collisions, cc, my_object, cc_obj, my_obj))

            # here will be push to car mqtt topic
            res.append((my_id, ccid, collisions))

    return res

def getLimitedNumberOfObjects(objects, limit):
    while len(objects) < limit:
        objects.extend(objects)

    return objects[:limit]

CONCURRENT_CD = 4
def acquireLock(REDIS_HOST):
    import redis
    redis_client = redis.StrictRedis(host=REDIS_HOST,port=6379)
    for i in range(CONCURRENT_CD):
        lock = redis_client.lock(f'cdlock{i}', 60, 0.1, 0.01)
        if lock.acquire():
            return lock
    return None

def run(params=[]):
    print("in run")

#    timeConsumed("start")

    from cd.dataclayObjectManager import DataclayObjectManager

    lock = acquireLock(params['REDIS_HOST'])
    if not lock:
        return {'error': f'There currently maximum number of {CONCURRENT_CD} simulatiously running CD actions'}

#    timeConsumed("dataclay.init")   #TODO: to be removed. needed for debugging

    fexec = lithops.FunctionExecutor(log_level='DEBUG')

#    timeConsumed("executor")   #TODO: to be removed. needed for debugging
    if 'ALIAS' not in params:  #TODO: to be removed. needed for debugging
        print("Params %s missing ALIAS parameter" % params)
        exit()

    alias = params['ALIAS']
#    print("ALIAS: %s" % alias)

    print("creating dm instance")
    dm = DataclayObjectManager(alias=alias)
#    timeConsumed("DataclayVehicleManager")   #TODO: to be removed. needed for debugging

    limit = None
    if 'LIMIT' in params and params['LIMIT'] != None:  #TODO: to be removed. needed for debugging
        limit = int(params['LIMIT'])  #TODO: to be removed. needed for debugging

    chunk_size = 1
    if 'CHUNK_SIZE' in params and params['CHUNK_SIZE'] != None:
        chunk_size =  int(params['CHUNK_SIZE'])

#    import pdb;pdb.set_trace()
    objects = dm.getAllObjects(with_tp=True, with_event_history=False)
    print("after dm.getAllObjects")
#    timeConsumed("dm.getAllObjects")

    if limit:
        objects = getLimitedNumberOfObjects(objects, limit)

    print(f"OBJECTS #{len(objects)}")

    ####################
    '''
    collided = ['c9ff81dc-51e1-45c8-8311-b4b31983b158:a7b9fc01-4d65-4ae0-b55e-ed5b820454a3', '5960f199-f89c-4bc0-b2eb-30284743b648:a7b9fc01-4d65-4ae0-b55e-ed5b820454a3', '905053aa-43e0-4dd5-9baf-b7856678dcd4:a7b9fc01-4d65-4ae0-b55e-ed5b820454a3', 'e15cd8bf-a254-481a-8741-9dceb1287452:a7b9fc01-4d65-4ae0-b55e-ed5b820454a3', '307ea265-bb16-4b95-8366-5786ad8ae5a2:a7b9fc01-4d65-4ae0-b55e-ed5b820454a3', '5960f199-f89c-4bc0-b2eb-30284743b648:a7b9fc01-4d65-4ae0-b55e-ed5b820454a3']
    test = []
    for obj in objects:
        if obj[0] in collided:
            test.append(obj)
    objects = test
    '''
    #####################

    def select_connected_cars(objects):
        CONNECTED_CARS = ['obj_10_132','obj_10_105','obj_10_151','obj_10_150', 'obj_10_28','obj_10_13','','']
        res = []
        for obj in objects:
            if dm.getObject(obj[0]).id_object in CONNECTED_CARS:
                res.append(obj)
        return res

    def chunker(seq, size):
        return (seq[pos:pos + size] for pos in range(0, len(seq), size))

    if False:
        connected_cars = select_connected_cars(objects)#objects
    else:
        if params.get("CCS_LIMIT"):
            print(f'Limiting number of connected cars to {params.get("CCS_LIMIT")}')

            connected_cars = objects[:int(params.get("CCS_LIMIT"))]
        else:
            connected_cars = objects
#    import pdb;pdb.set_trace()
#    timeConsumed("connected_cars = dm.getObjectTuplesWithTp")

    kwargs = []
    res = []

    if objects:
      for objects_chunk in chunker(objects, chunk_size):
        kwargs.append({'objects_chunk': objects_chunk, 'connected_cars': connected_cars})

      #timeConsumed("kwargs.append for {} number of objects".format(len(objects)))

#      import pdb;pdb.set_trace()
      print("before lithops fexec.map")
      fexec.map(detect_collision, kwargs, extra_env = {'__LITHOPS_LOCAL_EXECUTION': True})

#      timeConsumed("fexec.map")

#    pw.wait(download_results=False, WAIT_DUR_SEC=0.015)
      print("after lithops fexec.map")
      if objects:
        res = fexec.get_result(WAIT_DUR_SEC=0.015)

    print("lithops finished")
    client=mqtt.Client()
    client.connect("192.168.7.42")
    topic = "cd-out"
    client.publish(topic,f"CD finished")

    print("results: {}".format(res))
#    timeConsumed("fexec.wait")

    lock.release()

    print("returning from lithops function")
    return {"finished": "true"}


REDIS_HOST = '10.97.50.24'

if __name__ == '__main__':
    import sys
    limit = None
    chunk_size = 1
    if len(sys.argv) > 1:
        chunk_size = sys.argv[1]
    if len(sys.argv) > 2:
        limit = sys.argv[2]
    ccs_limit = None
    if len(sys.argv) > 3:
        ccs_limit = sys.argv[3]
    run(params={"CHUNK_SIZE" : chunk_size, "LIMIT": limit, "ALIAS" : "DKB", "CCS_LIMIT": ccs_limit, 'REDIS_HOST': REDIS_HOST})
