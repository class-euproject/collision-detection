#!/bin/bash
set echo-control-characters Off
stty -echoctl

first=true

echo '['
trap 'echo ]' EXIT
while true
do
	res=`wsk -i action invoke class/cdAction -p CHUNK_SIZE 5 --result`

	if [ $first != true ]; then
		sleep 0.05
		echo ','
	else
		first=false
	fi

	echo $res
done
