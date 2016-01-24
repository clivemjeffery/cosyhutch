#!/usr/bin/python
import time
import os
import sys
import urllib            # URL functions
import urllib2           # URL functions
from energenie import switch_on, switch_off


def main():

	INTERVAL = 10    # Delay between each check (seconds)
	APIKEY = '6VYHZF359E74W3C3'
	TABLKBACK = 'https://api.thingspeak.com/talkbacks/5442/commands/execute'

	print 'Entering command check loop'
	sys.stdout.flush()

	try:
		while True:
			# Fetch and execute the next command
			values = {'api_key' : APIKEY }
			postdata = urllib.urlencode(values)
			req = urllib2.Request(TABLKBACK, postdata)
			
			response = urllib2.urlopen(req, None, 5)
			html_string = response.read()
			response.close()
			if len(html_string) > 0:
				if html_string == 'ON':
					print 'Switching ON'
					switch_on(1)
				elif html_string == 'OFF':
					print 'Switching OFF'
					switch_off(1)
				else:
					print 'Ignoring: ' + html_string
			sys.stdout.flush()
			time.sleep(INTERVAL)

	except KeyboardInterrupt:
		#GPIO.cleanup()
		sys.stdout.flush()


if __name__=="__main__":
	main()
