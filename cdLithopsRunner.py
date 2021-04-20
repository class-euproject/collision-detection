print("before imports")

import os 
import time

import lithops

from cd.CD import collision_detection

from geolib import geohash
import paho.mqtt.client as mqtt

from cd.dataclayObjectManager import DataclayObjectManager
import click

print("after imports")


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
    print(f"in run with {params}")

    lock = acquireLock(params['REDIS_HOST'])
    if not lock:
        return {'error': f'There currently maximum number of {CONCURRENT_CD} simulatiously running CD actions'}

    config_overwrite = {'serverless': {}, 'lithops': {}}
    if params.get('DICKLE', False):
        config_overwrite['serverless']['customized_runtime'] = params['DICKLE']
    if params.get('RABBITMQ_MONITOR', False):
        config_overwrite['lithops']['rabbitmq_monitor'] = params['RABBITMQ_MONITOR']
    if params.get('STORAGELESS', False):
        config_overwrite['lithops']['storage'] = 'storageless'

    fexec = lithops.FunctionExecutor(log_level='DEBUG', config_overwrite=config_overwrite)

    if 'ALIAS' not in params: 
        print("Params %s missing ALIAS parameter" % params)
        exit()

    alias = params['ALIAS']

    print("creating dm instance")
    dm = DataclayObjectManager(alias=alias)

    limit = None
    if 'LIMIT' in params and params['LIMIT'] != None: 
        limit = int(params['LIMIT'])

    chunk_size = 1
    if 'CHUNK_SIZE' in params and params['CHUNK_SIZE'] != None:
        chunk_size =  int(params['CHUNK_SIZE'])

    objectsIDs = dm.getAllObjectsIDs()
    objects = dm.getAllObjects(with_tp=True, with_event_history=False)

    if params.get("DC_DISTRIBUTED"):
        objects = objectsIDs
    print("after dm.getAllObjects")

    if limit:
        objects = getLimitedNumberOfObjects(objects, limit)

    print(f"OBJECTS #{len(objects)}")

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
        connected_cars = select_connected_cars(objects)
    else:
        if params.get("CCS_LIMIT"):
            print(f'Limiting number of connected cars to {params.get("CCS_LIMIT")}')

            connected_cars = objects[:int(params.get("CCS_LIMIT"))]
        else:
            connected_cars = objects

    kwargs = []
    res = []

    if objects:
      print("before lithops fexec.map")
      if params.get("DC_DISTRIBUTED"):
        for objects_chunk in chunker(objects, chunk_size):
            kwargs.append({'objects_chunk': objects_chunk, 'cc_num_limit': limit})

        from dist_cd import detect_collision_distributed_dc
        fexec.map(detect_collision_distributed_dc, kwargs, extra_env = {'__LITHOPS_LOCAL_EXECUTION': True})
      else:
        for objects_chunk in chunker(objects, chunk_size):
          kwargs.append({'objects_chunk': objects_chunk, 'connected_cars': connected_cars})

        from centr_cd import detect_collision_centralized
        fexec.map(detect_collision_centralized, kwargs, extra_env = {'__LITHOPS_LOCAL_EXECUTION': True})

      print("after lithops fexec.map")
      if objects:
#        fexec.wait(download_results=False, WAIT_DUR_SEC=0.015)
        res = fexec.get_result(WAIT_DUR_SEC=0.015)

    print("lithops finished")
    client=mqtt.Client()
    client.connect("192.168.7.42")
    topic = "cd-out"
    client.publish(topic,f"CD finished")

    print("results: {}".format(res))

    lock.release()

    print("returning from lithops function")
    return {"finished": "true"}



@click.command()
@click.option('--redis', default='10.106.33.95', help='Redis host', type=str)
@click.option('--chunk_size', default=1, help='Size of object chunks, the actual number of chunks will be determined based on object_num / chunk_size', type=int)
@click.option('--limit', default='-1', help='Limits the number of objects. In case number of actual objects is lower it will duplicate objects up to specified limit', type=int)
@click.option('--ccs_limit', default=None, help='Hard limit number of connected cars', type=int)
@click.option('--dc_distributed', help='if specified will use DC in distributed approach', is_flag=True)

@click.option('--dickle', help='If specified set customized_runtime option to True', is_flag=True)
@click.option('--rabbitmq_monitor', help='If specified set rabbitmq_monitor option to True', is_flag=True)
@click.option('--storageless', help='If specified set storage mode to storageless', is_flag=True)
def run_wrapper(redis, chunk_size, limit, ccs_limit, dc_distributed, dickle, rabbitmq_monitor, storageless):
    params={"CHUNK_SIZE": chunk_size, "LIMIT": limit, "ALIAS" : "DKB", "CCS_LIMIT": ccs_limit, 'REDIS_HOST': redis,
            'DC_DISTRIBUTED': dc_distributed, 'DICKLE': dickle, 'RABBITMQ_MONITOR': rabbitmq_monitor, 'STORAGELESS': storageless}

    run(params=params)


if __name__ == '__main__':
    run_wrapper()
