import time

import requests
from datetime import datetime
import os, errno

import urllib3

import click

import signal
import sys
import json


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

APIHOST = 'https://192.168.7.42:31001'
AUTH_KEY = '23bc46b1-71f6-4ed5-8c54-816aa4f8c502:123zO3xZCLrMN6v2BKK1dXYFpXlPkccOFqm12CdAsMgRU4VrNZ9lyGVCGuMDGIwP'
NAMESPACE = '_'
BLOCKING = 'true'
RESULT = 'false'

TP_ACTION = 'class/tpAction'
CD_ACTION = 'class/cdAction'

tp_url = f'{APIHOST}/api/v1/namespaces/{NAMESPACE}/actions/{TP_ACTION}'
cd_url = f'{APIHOST}/api/v1/namespaces/{NAMESPACE}/actions/{CD_ACTION}'

user_pass = AUTH_KEY.split(':')

metrics = []

@click.command()
@click.argument('filename')
@click.option('--operation', help='Operation type, cd or tp', required=True)
@click.option('--chunk_size', default=1, help='Size of object chunks, the actual number of chunks will be determined based on object_num / chunk_size', type=int)
@click.option('--limit', default='-1', help='Limits the number of objects. In case number of actual objects is lower it will duplicate objects up to specified limit', type=int)
def benchmark(filename, operation, chunk_size, limit):

#    def signal_handler(sig, frame):
#        print('Good bye, have a nice day')
        # now save to specified file
#        with open(f"{filename}", mode='w') as f:
#            json.dump(data, f)
#            sys.exit(0)
#
#    signal.signal(signal.SIGINT, signal_handler)

    
    data = {'LOG_LEVEL': 'DEBUG'}
    if chunk_size:
        data["CHUNK_SIZE"]= chunk_size
    if limit:
        data["LIMIT"] = limit
     
    if operation == 'cd':
        url = cd_url
    else:
        url = tp_url

    while True:
        req_start = datetime.now()

        response = requests.post(url, params={'blocking':BLOCKING, 'result':RESULT}, json=data, auth=(user_pass[0], user_pass[1]), verify=False)

        req_end = datetime.now()

        result = response.json()['response']['result']

        ok = result['finished']

        req_end_to_end = round(req_end.timestamp() * 1000 - req_start.timestamp() * 1000, 1)

        aid = response.json()["activationId"]

        short_res = {'aid': aid, "finished": ok, "connected_cars": result["connected_cars"], "objects_len": result["objects_len"]}
        print(short_res)

        res = {'operation': operation, 'e2e': req_end_to_end, 'start': req_start.timestamp() * 1000, 'end': req_end.timestamp() * 1000}
        res.update(short_res)

        metrics.append(res)

        with open(f"{filename}", mode='w') as f:
            json.dump(metrics, f)



if __name__ == '__main__':
#        import pdb;pdb.set_trace()
    benchmark()
