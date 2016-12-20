#!/usr/bin/python
'''
A re-write of cosyhutch.py intended to be suitable single time call from cron.
That is, there's no continuous loop. Also to use logging rather than prints.
'''
import os
import sys
import urllib            # URL functions
import urllib2           # URL functions
import subprocess
from energenie import switch_on, switch_off
import logging
import logging.config

################# Default Constants #################
THINGSPEAKKEY = 'BKW4Q7PQGF3S18EG'
THINGSPEAKURL = 'https://api.thingspeak.com/update'
SENSOR = '/sys/bus/w1/devices/28-011590a84eff/w1_slave'
LOCKFILE = '/home/pi/cosyhutch/cosy.lock'
#####################################################
logging.config.fileConfig('/home/pi/cosyhutch/logging.conf')
logger = logging.getLogger('cosylog')

def sendData(url,key,temp):
	logger.debug('TRACEIN: sendData')
	values = {'api_key' : key,'field1' : temp}
	postdata = urllib.urlencode(values)
	req = urllib2.Request(url, postdata)
	logger.debug('Posting to thingspeak.')
	response = urllib2.urlopen(req, None, 5)
	html_string = response.read()
	response.close()
	logger.debug("TRACEOUT: sendData with thingspeak response %s", html_string)


def sensor_raw():
	f = open(SENSOR, 'r')
	lines = f.readlines()
	f.close()
	#print lines
	return lines


def read_18b20():
	sensor_info = sensor_raw()
	sensor_temp = sensor_info[1].find('t=')
	if sensor_temp != -1:
		temp = sensor_info[1].strip()[sensor_temp+2:]
		temp_degrees = float(temp)/1000.0
		return temp_degrees


def main():

	global THINGSPEAKKEY
	global THINGSPEAKURL
	global SENSOR

	chip_temp = 0.0
	sens_temp = 0.0

	try:
		logger.info('Reading temperature...')
		sens_temp = read_18b20()
		logger.info(' - temperature = %.2f C', sens_temp)
		if sens_temp >= 10.0:
			switch_off(1)
		elif sens_temp < 8.0:
			if os.path.isfile(LOCKFILE):
				logger.info(' - below 8.0 and locked off.')
			else:
				logger.info(' - below 8.0 and switching on.')
				switch_on(1)
		sendData(THINGSPEAKURL, THINGSPEAKKEY, sens_temp)
		
	except Exception:
		logger.exception('An error was caught, see traceback.')

	logger.info('...completed')

if __name__=="__main__":
	main()
