#!/usr/bin/python
import os
import sys
import urllib            # URL functions
import urllib2           # URL functions
from energenie import switch_on, switch_off
import RPi.GPIO as GPIO
import logging
import logging.config

##### Default constants
APIKEY = '6VYHZF359E74W3C3'
TALKBACK = 'https://api.thingspeak.com/talkbacks/5442/commands/execute'
LOCKFILE = '/home/pi/cosyhutch/cosy.lock'
#####
logging.config.fileConfig('/home/pi/cosyhutch/logging.conf')
logger = logging.getLogger('cosycmd')

def get_next_command():
	logger.debug('TRACEIN: get_next_command')
	values = {'api_key' : APIKEY }
	cmd = ''
	postdata = urllib.urlencode(values)
	req = urllib2.Request(TALKBACK, postdata)
	logger.debug('Requesting command from Thingspeak')	
	response = urllib2.urlopen(req, None, 5)
	cmd = response.read()
	response.close()
	logger.debug('TRACEOUT: Response was %s', cmd)
	return cmd		


def main():

	global APIKEY
	global TALKBACK
	global LOCKFILE

	logger.info("Using lockfile: %s", LOCKFILE)
	
	try:
		# Fetch and execute the next command
		cmd = get_next_command()
		if len(cmd) > 0:
			if cmd == 'ON':
				logger.info('Switching ON')
				if os.path.isfile(LOCKFILE):
					logger.info('Removing lockfile %s', LOCKFILE)
					os.remove(LOCKFILE)
				switch_on(1)
			elif cmd == 'OFF':
				logger.info('Switching OFF')
				switch_off(1)
			elif cmd == 'LOCKOFF':
				logger.info('Locking OFF')
				lock = open(LOCKFILE, 'w')
				lock.close()
				switch_off(1)
			else:
				logger.info('Ignoring unrecognised command: %s', cmd)			
	
	except Exception:
		logger.exception('An error was caught, see traceback.')
		GPIO.cleanup()

	GPIO.cleanup()
		
if __name__=="__main__":
	main()
