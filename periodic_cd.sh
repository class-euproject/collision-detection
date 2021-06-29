#!/bin/bash

#while true; do wsk -i action invoke class/cdAction -p CHUNK_SIZE 5 -p CCS 20,21,30,31,40 --result; sleep 0.05; done
while true; do wsk -i action invoke class/cdAction -p CHUNK_SIZE 5 --result; sleep 0.05; done
