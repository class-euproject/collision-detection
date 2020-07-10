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
|-- README.md
|-- test-file.py
|-- test-dataclay.py
|-- data
|   `-- data.txt
```

# Testing

To run it using local files from project root directory run:
```
python test-file.py
```

To test it with Dataclay, update stubs and cfgfiles folders with relevant files and run:
```
python test-dataclay.py
``` 
