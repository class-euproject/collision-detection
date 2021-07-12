#!/bin/bash

while true; do wsk -i action invoke class/tpAction -p CHUNK_SIZE 5 --result; sleep 0.05; done
