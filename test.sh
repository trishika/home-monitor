#!/bin/sh

###### ADD

curl -i -X POST --data "switch_host='todd:5000'&switch_id=2&sensor_host='todd:5000'&sensor_id=0&start_time=20&end_time=07&temp=22" http://localhost:5001/rules/
curl -i -X POST --data "switch_host='todd:5000'&switch_id=2&sensor_host='todd:5000'&sensor_id=0&start_time=07&end_time=20&temp=22" http://localhost:5001/rules/

curl -i -X GET http://localhost:5001/rules/

curl -i -X DELETE http://localhost:5001/rules/0/

