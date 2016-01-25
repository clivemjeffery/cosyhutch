#!/usr/bin/python
import time
import os
import sys
import urllib            # URL functions
import urllib2           # URL functions
from energenie import switch_on, switch_off

INTERVAL = 10    # Delay between each check (seconds)
APIKEY = '6VYHZF359E74W3C3'
TALKBACK = 'https://api.thingspeak.com/talkbacks/5442/commands/execute'

def exec_next_command():
	values = {'api_key' : APIKEY }
	postdata = urllib.urlencode(values)
	req = urllib2.Request(TABLKBACK, postdata)
	try:	
		response = urllib2.urlopen(req, None, 5)
		cmd = response.read()
		response.close()
		return cmd		
	except urllib2.HTTPError, e:
		log = log + 'Server could not fulfill the request. Error code: ' + e.code
	except urllib2.URLError, e:
		log = log + 'Failed to reach server. '
		if isinstance(e, basestring):
			log = log  + e.reason
	except:
		log = log + 'Unknown error'
	print log

def main():

	global INTERVAL
	global APIKEY
	global TALKBACK

	print 'Entering command check loop'
	sys.stdout.flush()

	try:
		while True:
			# Fetch and execute the next command
			cmd = exec_next_command()
			if len(cmd) > 0:
			if cmd == 'ON':
				print 'Switching ON'
				switch_on(1)
			elif cmd == 'OFF':
				print 'Switching OFF'
				switch_off(1)
			elif cmd == 'LOCKOFF'
				print 'Locking OFF'
				
			else:
				print 'Ignoring: ' + cmd			
			sys.stdout.flush()
			time.sleep(INTERVAL)

	except KeyboardInterrupt:
		#GPIO.cleanup()
		sys.stdout.flush()


if __name__=="__main__":
	main()
