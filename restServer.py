#!/usr/bin/env python2.7
# -*- encoding: utf-8 -*-
"""
    Home-rest
    ~~~~~~~~~

    :copyright: (c) 2013 by Aurélien Chabot <aurelien@chabot.fr>
    :license: LGPLv3, see COPYING for more details.
"""
try:
	from flask import Flask, request, abort, json
	from subprocess import call, Popen, PIPE
	from traceback import print_exc
	import threading
	import ConfigParser
	import sys, os
	import sqlite3
	import datetime
except ImportError as error:
	print 'ImportError: ', str(error)
	exit(1)

try:
	sys.path.insert(0, '../rest/')
	sys.path.insert(0, '/usr/local/bin/')
	from restClientLib import get_nodes, set_switch, update_sensor, update_switch
except ImportError as error:
	print 'Custom py ImportError: ', str(error)
	exit(1)

if len(sys.argv) > 1:
	config = sys.argv[1]
else:
	print("You need to provide a configuration")
	exit(1)

app = Flask(__name__)
app.config.from_pyfile(config, silent=True)

print(config)

try:
	fd = open(app.config["SERVERS"])
	servers = json.load(fd)
except:
	print("Invalid configuration file")
	exit(1)

db = sqlite3.connect('monitor.db')


################### RULES API

def createRulesTable():
	c = db.cursor()
	c.execute('''CREATE TABLE rules (
				id integer PRIMARY KEY AUTOINCREMENT, sensor_host text, sensor_id integer, switch_host text, switch_id interger,
				start_time timestamp, end_time timestamp, temp real)''')
	db.commit()

#createRulesTable()

# Get list of rules
@app.route("/rules/")
def get_rules():
	try:
		c = db.cursor()
		return json.dumps(c.execute('SELECT * FROM rules'))
	except:
		print_exc()
		return json.dumps({})

# Get one rule
@app.route("/rules/<int:ruleId>/", methods = ["GET"])
def get_rule(ruleId):
	try:
		c = db.cursor()
		return json.dumps(c.execute('SELECT * FROM rules WHERE id=:id', { "id": ruleId }))
	except:
		print_exc()
		return json.dumps({})

# Add one rule
@app.route("/rules/", methods = ["POST"])
def add_rule():
	try:
		c = db.cursor()
		c.execute('''INSERT INTO rules ( switch_host, switch_id, sensor_host, sensor_id, start_time, stop_time, temp)
				VALUES (:switch_host, :switch_id, :sensor_host, :sensor_id, :start_time, :stop_time, :temp''',
			{"switch_host" : request.form["switch_host"], "switch_id" : request.form["switch_id"],
			"sensor_host" : request.form["sensor_host"], "sensor_id" : request.form["sensor_id"],
			"start_time" : request.form['start_time'], "end_time" : request.form['end_time'], "temp" : request.form['temp']})
	except:
		print_exc()

	return json.dumps({})

# Del one rule
@app.route("/rules/<int:ruleId>/", methods = ["DELETE"])
def del_rule(ruleId):
	try:
		c = db.cursor()
		c.execute('DELETE FROM rules WHERE id=:id', { "id": ruleId })
		db.commit()

	except:
		print_exc()

	return json.dumps({})

app.run("0.0.0.0", app.config["PORT"])

def monitor():

	while True:

		switches,sensors = get_nodes(servers)

		c = db.cursor()
		for rule in c.execute('SELECT * FROM rules'):
			now = datetime.datetime.now().time()
			if now > rule["start_time"] and now < rule["end_time"]:

				for sensor in sensors:
					if sensor['host'] == rule['host']:
						switch = { 'host' : rule['switch_host'], 'id' : rule['switch_id']}
						if sensors['value'] < (rule['temp'] - 0.5):
							set_switch(switch, 1)
						if sensors['value'] > (rule['temp'] + 0.5):
							set_switch(switch, 0)

		time.sleep(6*60)


