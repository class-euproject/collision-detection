#!/bin/bash

REDIS_HOST=`kubectl -n openwhisk get svc|grep redis|awk '{print $3}'`
NODES="41 43 44 45"
RUNTIME_IMAGE_NAME=192.168.7.40:5000/kpavel/lithops_runtime:42.3
RUNTIME_NAME=lithops-runtime
MEMORY=512

tput setaf 2
echo "======================================="
echo "Extending ${RUNTIME_IMAGE_NAME} with new stubs"
echo "======================================="
tput setaf 7

PROJECTS_ROOT_DIR="${HOME}"
source ${PROJECTS_ROOT_DIR}/venv/bin/activate
LOG_LEVEL='INFO'

function pull_image_on_nodes() {
    image_name=$1
    tput setaf 2
    echo "Refreshing runtimes docker images in the cluster"
    tput setaf 7
    for node in $NODES; do
        ssh $node docker pull $image_name &
    done
}

ssh pkravche@192.168.7.32 "cd /m/home/pkravche/dataclay-class/examples/dataclay-class/dataclay-cloud/;./GetStubs.sh"
scp -r pkravche@192.168.7.32:/m/home/pkravche/dataclay-class/examples/dataclay-class/dataclay-cloud/stubs ${PROJECTS_ROOT_DIR}/collision-detection/

cd ${PROJECTS_ROOT_DIR}/collision-detection/
docker build -t $RUNTIME_IMAGE_NAME -f Dockerfile.stubs . 
docker push $RUNTIME_IMAGE_NAME

pull_image_on_nodes $RUNTIME_IMAGE_NAME

if true; then
    tput setaf 2
    echo "Restarting ow invokers"
    tput setaf 7
    kubectl -n openwhisk delete pod owdev-invoker-0 owdev-invoker-1 owdev-invoker-2 owdev-invoker-3 2>/dev/null
#    kubectl -n openwhisk delete pod owdev-controller-0 owdev-controller-1 owdev-controller-2 owdev-controller-3 2>/dev/null
    sleep 20
fi

tput setaf 2
echo -n "Update collision detection and trajectory prediction OW actions"
tput setaf 7

cd ${PROJECTS_ROOT_DIR}/collision-detection
rm classAction.zip
zip -r classAction.zip __main__.py .lithops_config cfgfiles/ stubs/ lithops_runner.py cd tp map_tp.py centr_cd.py dist_cd.py
wsk -i action update class/cdAction --docker $RUNTIME_IMAGE_NAME --timeout 300000  -p ALIAS DKB -p CHUNK_SIZE 3 -p STORAGELESS True -p DICKLE True -p REDIS_HOST ${REDIS_HOST} --memory $MEMORY -p OPERATION cd -p RUNTIME ${RUNTIME_NAME} -p LOG_LEVEL $LOG_LEVEL classAction.zip
wsk -i action update class/tpAction --docker $RUNTIME_IMAGE_NAME --timeout 300000  -p ALIAS DKB -p CHUNK_SIZE 3 -p STORAGELESS True -p DICKLE True -p REDIS_HOST ${REDIS_HOST} --memory $MEMORY -p OPERATION tp -p RUNTIME ${RUNTIME_NAME} -p LOG_LEVEL $LOG_LEVEL classAction.zip

tput setaf 2
echo '=================================================================================='
echo Fast update finished
echo '=================================================================================='
tput setaf 7
