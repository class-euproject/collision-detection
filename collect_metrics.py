import json
import tempfile
import uuid

import time
import csv
from statistics import mean, median
from columnar import columnar

import requests
from datetime import datetime
import os, errno
import sys

import urllib3
import logging

import click

logging.basicConfig(format='%(message)s', filename='benchmark.log', level=logging.INFO)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

#logging.basicConfig(filename='benchmark.log', level=logging.DEBUG)

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
alias = "DKB"
BENCHLOGS = "newlogs"
#CONTR_REPLICAS_NUM = 4
#INVOKER_REPLICAS_NUM = 4


sep = '\n----------------------------------\n'

#LOG_FILES = []
LOG_FILES_LINES = {}
LOG_SEARCH_META = {}

def find_in_activation_log(log, strToSearch, lineSplitIndex, all_occurences=False, find_after=None):
    res = []

    saved_strToSearch = strToSearch
    if find_after:
        strToSearch = find_after

    for line in log:
        if strToSearch in line:
          if find_after:
              find_after = None
              strToSearch = saved_strToSearch
              continue

          if lineSplitIndex < 0:
            if all_occurences:
              res.append(line)
            else:
              return line
          else:
            return line.split()[lineSplitIndex]
    return res if res else ''

def getActivationProperty(aid, name):
    url = f'{APIHOST}/api/v1/namespaces/{NAMESPACE}/activations/{aid}'
    response = requests.get(url, auth=(user_pass[0], user_pass[1]), verify=False)
    return response.json()[name]

def getActivationLogs(aid):
    try:
        return getActivationProperty(aid, 'logs')
    except Exception:
        time.sleep(0.5)
#        import pdb;pdb.set_trace()
        return getActivationProperty(aid, 'logs')

def getActivationEnd(aid):
    ts = getActivationProperty(aid, 'end')
    return datetime.fromtimestamp(ts / 1000)

def getActivationStart(aid):
    ts = getActivationProperty(aid, 'start')
    return datetime.fromtimestamp(ts / 1000)

def toDatetime(timestamp):
    try:
      res = datetime.strptime(timestamp.rstrip('Z'), '%Y-%m-%dT%H:%M:%S.%f')
    except Exception as e:
      import pdb;pdb.set_trace()
      print(timestamp)
    return res

def time_diff_milli(d1, d2):
    return round(abs(d1.timestamp() * 1000 - d2.timestamp() * 1000), 2)

def getDriverDCTimes(aid):

    dc_start = None
    dc_end = None

    for line in getActivationLogs(aid):
        if 'dataclay start' in line:
            dc_start = toDatetime(line.split()[0][:26])
        elif 'dataclay end' in line:
            dc_end = toDatetime(line.split()[0][:26])

    if not dc_start or not dc_end:
        return 'error'

    return time_diff_milli(dc_end, dc_start)

def getLithopsRuntimesActivationIDS(aid):
    activations = []
    logs = getActivationLogs(aid)
    lithops_activation_start = None
    for line in logs:
        if 'in run' in line:
            lithops_activation_start = toDatetime(line.split()[0][:26])

        if "A_INVOKE_CALL_" in line:
            invoke_timestamp = toDatetime(line.split()[0][:26])
            if line.count("A_INVOKE_CALL_") > 1:
                raise Exception(f"Sorry, something very wrong on this line! {line}")

            call_id = line.split()[7].split('A_INVOKE_CALL_')[1]
            for line in logs:
                if f"A_INVOKE_BACK_{call_id}" in line:
                    invoke_back_timestamp = toDatetime(line.split()[0][:26])

                    if f"A_INVOKE_BACK_{call_id}" not in line.split()[7]:
                        raise Exception(f"Sorry, something very wrong on this line! {line}")

                    _aid = line.split()[7].split('_')[4]
                    activations.append((time_diff_milli(invoke_timestamp, lithops_activation_start), time_diff_milli(invoke_back_timestamp, lithops_activation_start), _aid))
                    break

    return activations

TD_FORMAT = '[%Y-%m-%dT%H:%M:%S.%fZ]'
import re

def get_invocation_times(aid):
    logs = getActivationLogs(aid)

    d_s = find_in_activation_log(logs, f'storing results: ', 0)
    if d_s:
        dataclay_start = toDatetime(d_s.split()[0][:26])
    d_e = find_in_activation_log(logs, f'=======out traj_pred_v2_wrapper', 0, find_after='storing results: ')
    if d_e:
        dataclay_end = toDatetime(d_e.split()[0][:26])

    if d_e and d_s:
        dataclay_time = time_diff_milli(dataclay_end, dataclay_start)
    else:
        dataclay_time = 0

    invocation_start = getActivationStart(aid)
    invocation_end = getActivationEnd(aid)

    return [ aid, invocation_start.timestamp() * 1000, invocation_end.timestamp() * 1000, dataclay_time]

def time_diff_by_labels(logs, l1, l2):
    before = toDatetime(find_in_activation_log(logs, l1, 0).split()[0][:26])
    after = toDatetime(find_in_activation_log(logs, l2, 0).split()[0][:26])
    return time_diff_milli(before, after)

@click.command()
@click.argument('filename')
@click.option('--output-folder', help='tmp, if not specified')
def benchmark(filename, output_folder):
    first_time = True

    with open(filename) as f:
        driver_data = json.load(f)

    if not output_folder:
        driver_output_file = tempfile.mkstemp(suffix = '_driver.csv')[1]
        workers_output_file = tempfile.mkstemp(suffix = '_workers.csv')[1]
    else:
        if not os.path.exists(f"{output_folder}"):
            os.makedirs(f"{output_folder}")
        prefix = str(uuid.uuid4())
        driver_output_file = f"{output_folder}/{prefix}_driver.csv"
        workers_output_file = f"{output_folder}/{prefix}_workers.csv"

    for driver_invocation in driver_data:
        ok = driver_invocation['finished']
        e2e = driver_invocation['e2e']
        aid = driver_invocation["aid"]
        start = driver_invocation['start']
        end = driver_invocation['end']

        driver_headers = ['aid', 'start', 'end', 'e2e', 'dataclay', 'ok']
    
        driver_dc_time = getDriverDCTimes(aid)
        driver_metrics = [[aid, start, end, e2e, driver_dc_time, ok]]

        table = columnar(driver_metrics, driver_headers, no_borders=False)
        print(table)
        logging.info(table)

        activations = getLithopsRuntimesActivationIDS(aid)
        activationsData = []
        for activation in activations:
            activation_invocation_times = [aid]
            try:
                activation_invocation_times.extend(get_invocation_times(activation[2]))
            except Exception as e:
                import pdb;pdb.set_trace()
                get_invocation_times(activation[2])
                print(e)
        
            data = []

            for i, at in enumerate(activation_invocation_times):
                data.append(at)

            activationsData.append(data)

        def column(matrix, i):
            return [row[i] for row in matrix]

        worker_headers = ['parent_aid', 'aid', 'start', 'end', 'dc_time']
        max_worker_dc = 0
        worker_table = None
        try:
            if activationsData:
                worker_table = columnar(activationsData, worker_headers, no_borders=False)
                print(worker_table)
                logging.info(worker_table)
                try:
                    max_dc = max(column(activationsData, 4))
                except:
                    pass
        except Exception as e:
            import pdb;pdb.set_trace()
            pass

        with open(f"{driver_output_file}", mode='a') as f:
            writer = csv.writer(f)

            if first_time:
                writer.writerow(driver_headers)

            writer.writerows(driver_metrics)

        if activationsData:
            with open(f"{workers_output_file}", mode='a') as f:
                writer = csv.writer(f)

                if first_time:
                    writer.writerow(worker_headers)
                    first_time = False

                writer.writerows(activationsData)

    print("\n\n=================================================")
    print(f"\033[92mResults:\n{driver_output_file}")
    if activationsData:
        print(f'{workers_output_file}')
    print("\033[0m=================================================")



if __name__ == '__main__':
#    if True:
#        import pdb;pdb.set_trace()
    benchmark()
