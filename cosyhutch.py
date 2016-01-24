#!/usr/bin/python
import time
import os
import sys
import urllib            # URL functions
import urllib2           # URL functions
import subprocess
from energenie import switch_on, switch_off
import RPi.GPIO as GPIO

################# Default Constants #################
INTERVAL      = 2    # Delay between each reading (mins)
THINGSPEAKKEY = 'BKW4Q7PQGF3S18EG'
THINGSPEAKURL = 'https://api.thingspeak.com/update'
SENSOR = '/sys/bus/w1/devices/28-011590a84eff/w1_slave'
#####################################################

def sendData(url,key,temp1,temp2):
	values = {'api_key' : key,'field1' : temp1, 'field2' : temp2}
	postdata = urllib.urlencode(values)
	req = urllib2.Request(url, postdata)

	log = time.strftime("%d-%m-%Y\t%H:%M:%S")
	log = log + "\t{:.1f} C".format(temp1) + "\t{:.1f}C".format(temp2)
	log = log + "\t"

	try:
		# Send data to Thingspeak
		response = urllib2.urlopen(req, None, 5)
		html_string = response.read()
		response.close()
		log = log + 'thingspeak response: ' + html_string
	except urllib2.HTTPError, e:
		log = log + 'Server could not fulfill the request. Error code: ' + e.code
	except urllib2.URLError, e:
		log = log + 'Failed to reach server. '
		if isinstance(e, basestring):
			log = log  + e.reason
	except:
		log = log + 'Unknown error'
	print log


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

	global INTERVAL
	global THINGSPEAKKEY
	global THINGSPEAKURL
	global SENSOR

	print 'Loading OneWire libraries into kernel... '
	os.system('modprobe w1-gpio')
	os.system('modprobe w1-therm')
	print '...done.'

	chip_temp = 0.0
	sens_temp = 0.0

	print 'Entering monitor loop'
	print "Date\tTime\tChip\tSensor\tthingspeak response"
	sys.stdout.flush()

	try:
		while True:
			output = subprocess.check_output(['/opt/vc/bin/vcgencmd', 'measure_temp'])
			chip_temp = float(output[5:9])
			#print "Measured chip temperature {:.1f} C".format(chip_temp)
			sens_temp = read_18b20()
			#print "Measured 18b20 temperature {:.1f} C".format(sens_temp)
			if sens_temp >= 10:
				switch_off(1)
			else:
				switch_on(1)
			#print "Sending data..."
			sys.stdout.flush()
			sendData(THINGSPEAKURL,THINGSPEAKKEY,chip_temp,sens_temp)
			#print "...sent."
			sys.stdout.flush()
			time.sleep(INTERVAL*60)

	except KeyboardInterrupt:
		GPIO.cleanup()
		sys.stdout.flush()


if __name__=="__main__":
	main()
