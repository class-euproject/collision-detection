#!/bin/bash

wsk -i action invoke class/tpAction -p CHUNK_SIZE 1 -p LIMIT 30 -p STEAM_UP True --result
sleep 30
wsk -i action invoke class/cdAction -p CHUNK_SIZE 1 -p LIMIT 30 -p STEAM_UP True --result 
sleep 10
wsk -i action invoke class/tpAction -p CHUNK_SIZE 1 -p LIMIT 30 -p STEAM_UP True --result
sleep 10
wsk -i action invoke class/cdAction -p CHUNK_SIZE 1 -p LIMIT 30 -p STEAM_UP True --result 
sleep 10
wsk -i action invoke class/tpAction -p CHUNK_SIZE 1 -p LIMIT 30 -p STEAM_UP True --result
