import os 
import time

import lithops

from geolib import geohash
import paho.mqtt.client as mqtt

#from cd.dataclayObjectManager import DataclayObjectManager as CD_DOM
#from tp.dataclayObjectManager import DataclayObjectManager as TP_DOM
import click

from geolib import geohash


dm = None

def getLimitedNumberOfObjects(objects, limit):
    while len(objects) < limit:
        objects.extend(objects)

    if type(objects[0]) is tuple:
      for i in range(limit):
        objects[i] = [*objects[i]]
        objects[i][4] = f'{objects[i][4].split("_")[0]}_{i}'
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
  try:
    print(f"in run with: {params}")

#    start = time.time()
#    import pdb;pdb.set_trace()

    operation = params.get('OPERATION')

#    lock = acquireLock(params['REDIS_HOST'], operation)
#    if not lock:
#        return {'error': f'There currently maximum number of {CONCURRENCY} simulatiously running {operation} actions'}

    config_overwrite = {'serverless': {}, 'lithops': {}}
    if params.get('STORAGELESS', True):
        config_overwrite['lithops']['storage'] = 'storageless'
        config_overwrite['lithops']['rabbitmq_monitor'] = True 
    else:
        config_overwrite['serverless']['customized_runtime'] = False


    def get_map_function():
        if params.get("GEO_CHUNKER", False):
            if operation == 'cd':
                from centr_cd import new_detect_collision_centralized
                return new_detect_collision_centralized
            if operation == 'tp':
                from map_tp import traj_pred_v2_wrapper
                return traj_pred_v2_wrapper
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

    print('dataclay start')

    if not dm:
      print("creating dm instance")

      if operation == 'cd':
        from cd.dataclayObjectManager import DataclayObjectManager as CD_DOM
        dm = CD_DOM(alias=alias)
      else:
        from tp.dataclayObjectManager import DataclayObjectManager as TP_DOM
        dm = TP_DOM(alias=alias)


    if params.get("STEAM_UP"):
        objects = dm.get_dummy_objects()
    else:
        objects = dm.getAllObjects()

    print("dataclay end")

    limit = None
    if 'LIMIT' in params and params['LIMIT'] != None: 
        limit = int(params['LIMIT'])

    chunk_size = 1
    if 'CHUNK_SIZE' in params and params['CHUNK_SIZE'] != None:
        chunk_size =  int(params['CHUNK_SIZE'])

    if objects and limit:
        objects = getLimitedNumberOfObjects(objects, limit)

    print(f"OBJECTS #{len(objects)}")

    def chunker(seq, size):
        return (seq[pos:pos + size] for pos in range(0, len(seq), size))

    # This chunker is a generator that returns only pairs of <cc,obj> where obj is in the WA of cc and obj != cc
    def geo_pair_chunker(objects, connected_cars, chunk_size):
        cc_geomap = dict()   # Set map of geohash -> {CC with this geohash in WA}
        obj_geomap = dict()  # Set map of geohash -> {obj in this geohash}
        bg_obj_map = dict()  # Global background map of objid -> obj
        cc_pairs_map = dict()  # Set map to avoid duplicate / reflective CC pairs

        # Add an object id to a map of (key -> object id set) according to a key
        def add_to_setmap(setmap, key, objid):
            if not (key in setmap):
                setmap[key] = set()
            setmap[key].add(objid)

        # Build the CC geomap
        for cc in connected_cars:
            add_to_setmap(cc_geomap, cc[3], cc[4])
            add_to_setmap(cc_pairs_map, cc[4], cc[4])    # Add the CC id as first element to its own set to avoid reflective (cc, cc) pairs
            for gh in geohash.neighbours(cc[3]):
                add_to_setmap(cc_geomap, gh, cc[4])

        # Build the object geomap and background object map - only for objects that have geo-hashes matching CC
        for obj in objects:
            if obj[3] in cc_geomap:
               add_to_setmap(obj_geomap, obj[3], obj[4])
               bg_obj_map[obj[4]] = obj

        # Start generating matching pairs based on the obj_geomap
        obj_map=dict()
        pair_seq=[]
        count=0
        # Iterate over geohashes to create concise chunks
#        import pdb;pdb.set_trace()
        for gh in obj_geomap:
            # For each geohash, do Cartesian product of cc x obj
            for ccid in cc_geomap[gh]:
                for objid in obj_geomap[gh]:
                    # Check that objid is not of a CC, and that if objid blongs to CC, it wasn't paired with ccid before and that objid != ccid
                    if (not (objid in cc_pairs_map)) or (not(ccid in cc_pairs_map[objid])):
                        # For every suitable pair, insert objects to map and pair to seq
                        obj_map[ccid] = bg_obj_map[ccid]
                        obj_map[objid] = bg_obj_map[objid]
#                        import pdb;pdb.set_trace()

                        pair_seq.append((objid, ccid))
                        count += 1
                        # For pairs of connected cars, update the pairs map to avoid future duplications
                        if objid in cc_pairs_map:
                            add_to_setmap(cc_pairs_map, ccid, objid)
                            add_to_setmap(cc_pairs_map, objid, ccid)
                        # Every time we accumulate <chunk_size> pairs, yield and reset
                        if count == chunk_size:
                            ret_obj_map = obj_map
                            ret_pair_seq = pair_seq
                            obj_map=dict()
                            pair_seq=[]
                            count=0
                            yield ret_pair_seq, ret_obj_map
        # Yield final partial chunk, if remaining
        if count > 0:
            yield pair_seq, obj_map

    cc_classes = []
    if params.get("CCS"):
        print(f'Limiting set of connected cars to classes {params.get("CCS")}')
        cc_classes = params.get("CCS").split(',')
    
    connected_cars = []
    if params.get("STEAM_UP") or not params.get("CCS"):
        connected_cars = objects
    else:
        for obj in objects:
            if obj[5] in cc_classes:
                connected_cars.append(obj)

#    import pdb;pdb.set_trace()
    print(f"connected cars number: {len(connected_cars)}")

    kwargs = []
    res = []

    def get_chunks(objects, chunk_size):
        kwargs = []
        if operation == 'tp':
            for objects_chunk in chunker(objects, chunk_size):
                kwargs.append({'objects_chunk': objects_chunk})
        else:
            if params.get("GEO_CHUNKER"):
                for pairs_chunk, object_map in geo_pair_chunker(objects, connected_cars, chunk_size):
                    kwargs.append({'pairs_chunk': pairs_chunk, 'object_map': object_map})                
            else:
                for objects_chunk in chunker(objects, chunk_size):
                    kwargs.append({'objects_chunk': objects_chunk, 'connected_cars': connected_cars})
        return kwargs

#    import pdb;pdb.set_trace()
    if params.get("STEAM_UP") or (objects and operation == 'tp') or connected_cars:
      print("before lithops fexec.map")

      start_get_chunks = time.time()
      kwargs = get_chunks(objects, chunk_size)
      print(f"Chunker time: {time.time() - start_get_chunks}")
#      fexec.map(map_function, kwargs, extra_env = {'__LITHOPS_LOCAL_EXECUTION': True}, include_modules = ['cd', 'tp'])
      fexec.map(map_function, kwargs, extra_env = {'__LITHOPS_LOCAL_EXECUTION': True})

      print("after lithops fexec.map")
      if objects:
        fexec.wait(download_results=False, WAIT_DUR_SEC=0.015)

    print("lithops finished")
    client=mqtt.Client()
    client.connect("192.168.7.42")
    topic = "cd-out"
    client.publish(topic,f"{operation} finished")

    print("results: {}".format(res))

#    lock.release()

    print("returning from lithops function")

    return {"finished": "true", "aid": os.environ['__OW_ACTIVATION_ID'], 'objects_len': len(objects), 'connected_cars': len(connected_cars)}
  except Exception:
    import traceback
    traceback.print_exc()

    return {"finished": "error", "aid": os.environ['__OW_ACTIVATION_ID']}




@click.command()
@click.option('--operation', help='Operation type, cd or tp', required=True)

@click.option('--redis', default='10.106.33.95', help='Redis host', type=str)
@click.option('--chunk_size', default=1, help='Size of object chunks, the actual number of chunks will be determined based on object_num / chunk_size', type=int)
@click.option('--limit', help='Limits the number of objects. In case number of actual objects is lower it will duplicate objects up to specified limit', type=int)
@click.option('--ccs', default=None, help='Hard limit connected cars', type=str)
@click.option('--geo_chunker', help='if specified will use geo chunker in driver', is_flag=True)
@click.option('--dickle', help='If specified set customized_runtime option to True', is_flag=True)
@click.option('--storageless', help='If specified set storage mode to storageless', is_flag=True)
@click.option('--runtime', help='Lithops runtime docker image to use')
@click.option('--steam_up', help='If specified steaming up to the limit', is_flag=True)
@click.option('--log_level', help='Log level', default='DEBUG')
def run_wrapper(redis, chunk_size, limit, ccs, geo_chunker, dickle, storageless, operation, runtime, steam_up, log_level):
    params={"CHUNK_SIZE": chunk_size, "LIMIT": limit, "ALIAS" : "DKB", "CCS": ccs, 'REDIS_HOST': redis,
            'GEO_CHUNKER': geo_chunker, 'DICKLE': dickle, 'STORAGELESS': storageless, 'OPERATION': operation, 'RUNTIME': runtime, 'STEAM_UP': steam_up, 'LOG_LEVEL': log_level}

    run(params=params)


if __name__ == '__main__':
    run_wrapper()
