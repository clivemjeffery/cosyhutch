#!/usr/bin/python
'''
A COSYHUTCH script intended to be suitable single time call from cron.
Uses logging configured in logging.conf.
'''
import os
import sys
import urllib            # URL functions
import urllib2           # URL functions
import subprocess
import RPi.GPIO as GPIO
from energenie import switch_on, switch_off
import logging
import logging.config
import argparse

################# Default Constants #################
THINGSPEAKKEY = 'BKW4Q7PQGF3S18EG'
THINGSPEAKURL = 'https://api.thingspeak.com/update'
SENSPAT = '/sys/bus/w1/devices/*/w1_slave'
SENS1 = '28-011590a84eff'
SENS2 = '28-000008e748b9'
LOCKFILE = '/home/pi/cosyhutch/cosy.lock'
#####################################################
logging.config.fileConfig('/home/pi/cosyhutch/logging.conf')
logger = logging.getLogger('cosylog')

def sendData(url, key, temp1, temp2, status):
	logger.debug('TRACEIN: sendData')
	values = {'api_key' : key,'field1' : temp1, 'field2': temp2, 'status' : status}
	postdata = urllib.urlencode(values)
	req = urllib2.Request(url, postdata)
	logger.debug('Posting to thingspeak.')
	response = urllib2.urlopen(req, None, 5)
	html_string = response.read()
	response.close()
	logger.debug("TRACEOUT: sendData - thingspeak response: %s", html_string)


def sensor_raw(sensid):
	f = open(SENSPAT.replace('*',sensid,1), 'r')
	lines = f.readlines()
	f.close()
	#print lines
	return lines


def read_18b20(sensid):
	sensor_info = sensor_raw(sensid)
	sensor_temp = sensor_info[1].find('t=')
	if sensor_temp != -1:
		temp = sensor_info[1].strip()[sensor_temp+2:]
		temp_degrees = float(temp)/1000.0
		return temp_degrees


def main():

	global THINGSPEAKKEY
	global THINGSPEAKURL
	global SENSPAT
	global SENS1
	global SENS2

	outside_temp = 0.0
	hutch_temp = 0.0
	status = ''

	parser = argparse.ArgumentParser()
	parser.add_argument("-n", "--cosymin", default=8.0, type=float, help='The minimum desired hutch temperature.')
	parser.add_argument("-x", "--cosymax", default=10.0, type=float, help='The temperature at which to turn off the heater.')
	args = parser.parse_args()

	logger.debug('CosyHutch min=%.2f max=%.2f', args.cosymin, args.cosymax)

	try: # sensing
		logger.debug('Reading temperature...')
		hutch_temp = read_18b20(SENS1)
		outside_temp = read_18b20(SENS2)
		status = '%.2f C, %.2f C' % (hutch_temp, outside_temp)
		logger.debug(status)
	except Exception:
		status = 'Sensing error' 
		logger.exception(status)
		
	try: # control
		if os.path.isfile(LOCKFILE): # ensure locked off
			switch_off(1)
			status = '%s switched off in lock' % status
		elif hutch_temp >= args.cosymax:
			switch_off(1)
			status = '%s switched off at %.2f (high)' % (status, args.cosymax)
		elif hutch_temp <= args.cosymin:
			switch_on(1)
			status = '%s switched on at %.2f (low)' % (status, args.cosymin)
		else:
			status = '%s stable' % status
		logger.info(status)
	except Exception:
		status = 'Control error'
		logger.exception(status)
		
	try:
		sendData(THINGSPEAKURL, THINGSPEAKKEY, hutch_temp, outside_temp, status)
	except Exception:
		logger.exception('Error sending data.')

	logger.debug('...cleaning up...')
	GPIO.cleanup()
	logger.debug('...done.')

if __name__=="__main__":
	main()
