#!/bin/bash
SENSORID="30:52:cb:e7:ff:11"
STARTTIME=$(date -I)
for i in `seq 1 3`; do
	curl -vX POST localhost:5000/insert -H "Content-type: application/json" -d '{"sensorid": "'$SENSORID'","timestamp": "'$(date -Is)'","sensors":{"co": '$RANDOM', "dust": '$RANDOM', "noise": '$RANDOM'}}'
	sleep 1
done

curl -v localhost:5000/retrieve?sensorid=$SENSORID\&starttime=$STARTTIME
