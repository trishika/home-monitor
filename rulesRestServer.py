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
	import json
	import urllib2
	import ConfigParser
	import sys, os, time, datetime
	import sqlite3
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

try:
	fd = open(app.config["SERVERS"])
	servers = json.load(fd)
except:
	print("Invalid configuration file")
	exit(1)


def dict_factory(cursor, row):
	d = {}
	for idx,col in enumerate(cursor.description):
		d[col[0]] = row[idx]
	return d

db = sqlite3.connect(app.config['DB'])
db.row_factory = dict_factory

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
		return json.dumps(c.execute('SELECT * FROM rules').fetchall())
	except:
		print_exc()
		return json.dumps({})

# Get one rule
@app.route("/rules/<int:ruleId>/", methods = ["GET"])
def get_rule(ruleId):
	try:
		c = db.cursor()
		return json.dumps(c.execute('SELECT * FROM rules WHERE id=:id', { "id": ruleId }).fetchall())
	except:
		print_exc()
		return json.dumps({})

# Add one rule
@app.route("/rules/", methods = ["POST"])
def add_rule():
	try:
		c = db.cursor()
		c.execute('''INSERT INTO rules
					( switch_host,  switch_id,  sensor_host,  sensor_id,  start_time,  end_time,  temp)
			VALUES  (:switch_host, :switch_id, :sensor_host, :sensor_id, :start_time, :end_time, :temp)''',
			{"switch_host" : request.form["switch_host"], "switch_id" : request.form["switch_id"],
			"sensor_host" : request.form["sensor_host"], "sensor_id" : request.form["sensor_id"],
			"start_time" : request.form['start_time'], "end_time" : request.form['end_time'],
			"temp" : request.form['temp']})
		db.commit()
	except:
		print_exc()

	return get_rules()

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

# Rest server for monitor configuration
app.run("0.0.0.0", app.config["PORT"])
