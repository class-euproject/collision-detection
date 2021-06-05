print("before imports")

import os 
import time

import lithops

from cd.CD import collision_detection

from geolib import geohash
import paho.mqtt.client as mqtt

from cd.dataclayObjectManager import DataclayObjectManager as CD_DOM
from tp.dataclayObjectManager import DataclayObjectManager as TP_DOM
import click

print("after imports")

dm = None

def getLimitedNumberOfObjects(objects, limit):
    while len(objects) < limit:
        objects.extend(objects)

    return objects[:limit]

CONCURRENCY = 1 
def acquireLock(REDIS_HOST, operation):
    import redis
    redis_client = redis.StrictRedis(host=REDIS_HOST,port=6379)
    for i in range(CONCURRENCY):
        lock = redis_client.lock(f'{operation}{i}', 60, 0.1, 0.01)
        if lock.acquire():
            return lock
    return None

def run(params=[]):
    print(f"in run with {params}")
#    import pdb;pdb.set_trace()

    operation = params.get('OPERATION')

    lock = acquireLock(params['REDIS_HOST'], operation)
#    if not lock:
#        return {'error': f'There currently maximum number of {CONCURRENCY} simulatiously running {operation} actions'}

    config_overwrite = {'serverless': {}, 'lithops': {}}
    if params.get('STORAGELESS', True):
        config_overwrite['lithops']['storage'] = 'storageless'
        config_overwrite['lithops']['rabbitmq_monitor'] = True 
    else:
        config_overwrite['serverless']['customized_runtime'] = False


    def get_map_function():
        if params.get("DC_DISTRIBUTED", False):
            if operation == 'cd':
                from dist_cd import detect_collision_distributed_dc_pairs
                return detect_collision_distributed_dc_pairs
            if operation == 'tp':
                from map_tp import traj_pred_v2_distr
                return traj_pred_v2_distr
        else:
            if operation == 'cd':
                from centr_cd import detect_collision_centralized
                return detect_collision_centralized
            if operation == 'tp':
                from map_tp import traj_pred_v2_wrapper
                return traj_pred_v2_wrapper
        
    map_function = get_map_function()
    function_mod_name = os.path.basename(map_function.__code__.co_filename)
    if function_mod_name.endswith('.py'):
        function_mod_name = function_mod_name[:-3]

    if params.get('DICKLE', False):
        config_overwrite['serverless']['customized_runtime'] = True
        config_overwrite['serverless']['map_func_mod'] = function_mod_name
        config_overwrite['serverless']['map_func'] = map_function.__name__

    log_level = params.get('LOG_LEVEL', 'INFO')

    fexec = lithops.FunctionExecutor(log_level=log_level, runtime=params.get('RUNTIME'), config_overwrite=config_overwrite)

    if 'ALIAS' not in params: 
        print("Params %s missing ALIAS parameter" % params)
        exit()

    alias = params['ALIAS']

    global dm

    if not dm:
      print("creating dm instance")

      if operation == 'cd':
        dm = CD_DOM(alias=alias)
      else:
        dm = TP_DOM(alias=alias)

    limit = None
    if 'LIMIT' in params and params['LIMIT'] != None: 
        limit = int(params['LIMIT'])

    chunk_size = 1
    if 'CHUNK_SIZE' in params and params['CHUNK_SIZE'] != None:
        chunk_size =  int(params['CHUNK_SIZE'])

    
#    import pdb;pdb.set_trace()
    if params.get("DC_DISTRIBUTED"):
        objects = dm.getAllObjectsIDs()
    elif params.get("STEAM_UP"):
#        objects = getLimitedNumberOfObjects([], int(s_up))
        objects = dm.get_dummy_objects()
    else:
        objects = dm.getAllObjects()

    print("after dm.getAllObjects")
#    import pdb;pdb.set_trace()

    if limit:
        objects = getLimitedNumberOfObjects(objects, limit)

    print(f"OBJECTS #{len(objects)}")

    def chunker(seq, size):
        return (seq[pos:pos + size] for pos in range(0, len(seq), size))

    cc_ids = []
    if params.get("CCS"):
        print(f'Limiting set of connected cars to {params.get("CCS")}')
        cc_ids = params.get("CCS").split(',')
    
    connected_cars = []
    for obj in objects:
        if not params.get("STEAM_UP") and obj[4] in cc_ids:
            connected_cars.append(obj)
        elif not params.get("STEAM_UP"):
            connected_cars = objects

    print(f"connected cars len: {len(connected_cars)}")

    kwargs = []
    res = []

    def get_chunks(objects, chunk_size):
        kwargs = []
        if operation == 'tp':
            for objects_chunk in chunker(objects, chunk_size):
                kwargs.append({'objects_chunk': objects_chunk})
        else:
            if params.get("DC_DISTRIBUTED"):
                from itertools import combinations
                for pairs_chunk in chunker(list(combinations(objects, r=2)), chunk_size):
                    kwargs.append({'pairs_chunk': pairs_chunk})
            else:
                for objects_chunk in chunker(objects, chunk_size):
                    kwargs.append({'objects_chunk': objects_chunk, 'connected_cars': connected_cars})
        return kwargs

#    import pdb;pdb.set_trace()
    if params.get("STEAM_UP") or (objects and operation == 'tp') or len(connected_cars) > 1:
      print("before lithops fexec.map")

      kwargs = get_chunks(objects, chunk_size)
#      fexec.map(map_function, kwargs, extra_env = {'__LITHOPS_LOCAL_EXECUTION': True}, include_modules = ['cd', 'tp'])
      fexec.map(map_function, kwargs, extra_env = {'__LITHOPS_LOCAL_EXECUTION': True})

      print("after lithops fexec.map")
      if objects:
        fexec.wait(download_results=False, WAIT_DUR_SEC=0.015)
#        res = fexec.get_result(WAIT_DUR_SEC=0.015)

    print("lithops finished")
    client=mqtt.Client()
    client.connect("192.168.7.42")
    topic = "cd-out"
    client.publish(topic,f"CD finished")

    print("results: {}".format(res))

#    lock.release()

    print("returning from lithops function")
    return {"finished": "true"}



@click.command()
@click.option('--operation', help='Operation type, cd or tp', required=True)

@click.option('--redis', default='10.106.33.95', help='Redis host', type=str)
@click.option('--chunk_size', default=1, help='Size of object chunks, the actual number of chunks will be determined based on object_num / chunk_size', type=int)
@click.option('--limit', default='-1', help='Limits the number of objects. In case number of actual objects is lower it will duplicate objects up to specified limit', type=int)
@click.option('--ccs', default=None, help='Hard limit connected cars', type=str)
@click.option('--dc_distributed', help='if specified will use DC in distributed approach', is_flag=True)
@click.option('--dickle', help='If specified set customized_runtime option to True', is_flag=True)
@click.option('--storageless', help='If specified set storage mode to storageless', is_flag=True)
@click.option('--runtime', help='Lithops runtime docker image to use')
@click.option('--steam_up', help='If specified steaming up to the limit', is_flag=True)
@click.option('--log_level', help='Log level', default='DEBUG')
def run_wrapper(redis, chunk_size, limit, ccs, dc_distributed, dickle, storageless, operation, runtime, steam_up, log_level):
    params={"CHUNK_SIZE": chunk_size, "LIMIT": limit, "ALIAS" : "DKB", "CCS": ccs, 'REDIS_HOST': redis,
            'DC_DISTRIBUTED': dc_distributed, 'DICKLE': dickle, 'STORAGELESS': storageless, 'OPERATION': operation, 'RUNTIME': runtime, 'STEAM_UP': steam_up, 'LOG_LEVEL': log_level}

    run(params=params)


if __name__ == '__main__':
    run_wrapper()
