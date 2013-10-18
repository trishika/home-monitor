#!/bin/sh

###### ADD

curl -i -X POST --data "switch_host=todd&switch_id=2&sensor_host=todd&sensor_id=0&start_time=20&end_time=07&temp=22" http://localhost:5001/rules/

