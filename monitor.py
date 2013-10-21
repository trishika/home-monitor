#!/usr/bin/env python2.7
# -*- encoding: utf-8 -*-
"""
    Home-monitor
    ~~~~~~~~~~~~

    :copyright: (c) 2013 by Aurélien Chabot <aurelien@chabot.fr>
    :license: GPLv3, see COPYING for more details.
"""
try:
	import threading
	import sys, os, time, datetime
	import json
	import urllib2
	from ConfigParser import SafeConfigParser
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


class FakeSecHead(object):
	def __init__(self, fp):
		self.fp = fp
		self.sechead = '[default]\n'

	def readline(self):
		if self.sechead:
			try: return self.sechead
			finally: self.sechead = None
		else: return self.fp.readline()

if len(sys.argv) > 1:
	config = SafeConfigParser()
	config.readfp(FakeSecHead(open(sys.argv[1])))
else:
	print("You need to provide a configuration")
	exit(1)



class Monitor(threading.Thread):

	def __init__(self):
		threading.Thread.__init__(self)

	def get_rules(self):
		data = {}
		try:
			url = urllib2.urlopen("http://localhost:%(port)d/rules/" % { "port" : config.getint('default', 'PORT') })
			data = json.loads(url.read())
		except:
			print("Failed to get rules")
			print_exc()
		finally:
			return data

	def run(self):

		while True:

			rules = self.get_rules()
			for rule in rules:
				now = datetime.datetime.now().timetuple()

				if int(now[3]) > int(rule["start_time"]) or int(now[3]) < int(rule["end_time"]):

					switch = { 'host' : "http://" + rule['switch_host'], 'id' : rule['switch_id']}
					sensor = { 'host' : "http://" + rule['sensor_host'], 'id' : rule['sensor_id']}
					update_sensor(sensor)

					if sensor['value'] < (rule['temp'] - 0.5):
						print("Set heater on, current temp is %s, target is %s" % (str(sensor['value']), str(rule['temp'])))
						set_switch(switch, 1)
					if sensor['value'] > (rule['temp'] + 0.5):
						print("Set heater off, current temp is %s, target is %s" % (str(sensor['value']), str(rule['temp'])))
						set_switch(switch, 0)

			time.sleep(5)

# Launch monitor
monitor = Monitor()
monitor.start()
