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

Update lithops config with [optimal setup][https://github.com/class-euproject/lithops/blob/extend_runtime2/docs/mode_serverless.md#dynamic-runtime-customization]

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

In case the runtime been extended with map function module and dependencies using ```lithops runtime extend``` (there an option to specify runtime expilictly instead of updating .lithops_config) the --dickle, "dockerized pickle", can be applied
```
python lithops_runner.py --operation cd --chunk_size 3 --dickle --runtime <EXTENDED_RUNTIME_IMAGE>
```

In case .lithops_config has rabbitmq section configured it is possible to avoid object storage
```
python lithops_runner.py --operation cd --chunk_size 3 --dickle --runtime <EXTENDED_RUNTIME_IMAGE> --storageless
```
