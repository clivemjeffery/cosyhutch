#!/usr/bin/python
import time
import os
import sys
import urllib            # URL functions
import urllib2           # URL functions
from energenie import switch_on, switch_off
import RPi.GPIO as GPIO

INTERVAL = 10    # Delay between each check (seconds)
APIKEY = '6VYHZF359E74W3C3'
TALKBACK = 'https://api.thingspeak.com/talkbacks/5442/commands/execute'
LOCKFILE = '/home/pi/cosyhutch/cosy.lock'

def exec_next_command():
	values = {'api_key' : APIKEY }
	postdata = urllib.urlencode(values)
	req = urllib2.Request(TALKBACK, postdata)
	cmd = ''
	try:	
		response = urllib2.urlopen(req, None, 5)
		cmd = response.read()
		response.close()
	except urllib2.HTTPError, e:
		print 'Server could not fulfill the request. Error code: ' + e.code
	except urllib2.URLError, e:
		print 'Failed to reach server. '
		if isinstance(e, basestring):
			print e.reason
	except:
		print 'Unknown error'
	return cmd		


def main():

	global INTERVAL
	global APIKEY
	global TALKBACK
	global LOCKFILE

	print 'Using lockfile: ' + LOCKFILE
	print 'Entering command check loop'
	sys.stdout.flush()

	try:
		while True:
			# Fetch and execute the next command
			cmd = exec_next_command()
			if len(cmd) > 0:
				if cmd == 'ON':
					print 'Switching ON'
					os.remove(LOCKFILE)
					switch_on(1)
				elif cmd == 'OFF':
					print 'Switching OFF'
					switch_off(1)
				elif cmd == 'LOCKOFF':
					print 'Locking OFF'
					lock = open(LOCKFILE, 'w')
					lock.close()
					switch_off(1)
				else:
					print 'Ignoring: ' + cmd			
			sys.stdout.flush()
			time.sleep(INTERVAL)

	except KeyboardInterrupt:
		print 'Interruped by user at keyboard. Halting'
		GPIO.cleanup()
		sys.stdout.flush()

if __name__=="__main__":
	main()
