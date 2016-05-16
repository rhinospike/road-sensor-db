#!/bin/bash
SENSORID="30:52:cb:e7:ff:11"
SERVER="https://road-sensor-db.herokuapp.com"
#SERVER=localhost:5000
STARTTIME=$(date -I)
for i in `seq 1 3`; do
	curl -vX POST $SERVER/insert -H "Content-type: application/json" -d '{"sensorid": "'$SENSORID'","timestamp": "'$(date -Is)'","sensors":{"co": '$RANDOM', "dust": '$RANDOM', "noise": '$RANDOM'}}'
	sleep 1
done

curl -v $SERVER/retrieve?sensorid=$SENSORID\&starttime=$STARTTIME
