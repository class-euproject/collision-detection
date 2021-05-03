## collision-detection

## Acknowledgements

This work has been supported by the EU H2020 project CLASS, contract #780622.


# Project structure

```
collision-detection
|-- cd
|   |-- fileBasedObjectManager.py
|   |-- dataclayObjectManager.py
|   |-- __init__.py
|   `-- CD.py
|-- tp
|   |-- fileBasedObjectManager.py
|   |-- dataclayObjectManager.py
|   |-- __init__.py
|   `-- v3TP.py
|-- lithops_runner.py
|-- README.md
|-- test-file.py
|-- test-dataclay.py
|-- data
|   `-- data.txt
```

# Testing
Update dataclay cfgfiles with your credentials

Copy dataclay stubs and cfgfiles to the root directory
e.g.
```
ssh <user>@<dataclay host> "cd <DATACLAY_CLOUD_DIR>/;./GetStubs.sh
scp -r <user>@<dataclay host> "cd <DATACLAY_CLOUD_DIR>/stubs .
```

Update lithops config with [optimal setup](https://github.com/class-euproject/lithops/blob/extend_runtime2/docs/mode_serverless.md#dynamic-runtime-customization)

Run collision detection with defaults:
```
python lithops_runner.py --operation cd
```

Or run trajectory prediction with defaults:
```
python lithops_runner.py --operation tp
```

The data sent to workers in chunks when default chunk size is 1. Use --chunk_size parameter to control the level of concurrency, e.g.
```
python lithops_runner.py --operation cd --chunk_size 3
```

Extend runtime docker image with map function module and dependencies using [lithops runtime extend](https://github.com/class-euproject/lithops/blob/extend_runtime2/docs/mode_serverless.md#dynamic-runtime-customization)
```
lithops runtime extend $RUNTIME_NAME --filepath /home/class/collision-detection/centr_cd.py --function detect_collision_centralized
```

In order to avoid expensive serialization/deserialization on driver and workers layers --dickle, "dockerized pickle", parameter can be applied along with previously extended runtime docker image
```
python lithops_runner.py --operation cd --chunk_size 3 --dickle --runtime <EXTENDED_RUNTIME_IMAGE>
```

In case .lithops_config has rabbitmq section configured, to avoid interaction with object storage in driver and worker layers
```
python lithops_runner.py --operation cd --chunk_size 3 --dickle --runtime <EXTENDED_RUNTIME_IMAGE> --storageless
```
