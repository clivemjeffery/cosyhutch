#!/usr/bin/python
'''
A COSYHUTCH script intended to be suitable single time call from cron.
Uses logging configured in logging.conf.
'''
import os
import sys
import time
import urllib            # URL functions
import urllib2           # URL functions
import subprocess
import RPi.GPIO as GPIO
from energenie import switch_on, switch_off
import logging
import logging.config
import argparse
from sensor import Sensor

################# Default Constants #################
THINGSPEAKKEY = 'BKW4Q7PQGF3S18EG'
THINGSPEAKURL = 'https://api.thingspeak.com/update'
LOCKFILE = '/home/pi/cosyhutch/cosy.lock'
#####################################################
if sys.platform == 'darwin':
  DEVICEPATH = './device_sim/'
  logging.config.fileConfig('simlog.conf')
else:
  DEVICEPATH = '/sys/bus/w1/devices/'
  logging.config.fileConfig('/home/pi/cosyhutch/logging.conf')
logger = logging.getLogger('cosylog')
datalogger = logging.getLogger('cosydatalog')

SENSORS = []

def sendData(status):
  logger.debug("TRACEIN: sendData")
  
  values = {'api_key' : THINGSPEAKKEY, 'status' : status}
  temperatures = {}
  for sensor in SENSORS:
    temperatures[sensor.field] = sensor.temperature

  logger.debug("sendData - temperatures: %s", temperatures)
  values.update(temperatures)
  logger.debug("sendData - values: %s", values)
  
  postdata = urllib.urlencode(values)
  req = urllib2.Request(THINGSPEAKURL, postdata)
  logger.debug('Posting to thingspeak.')
  response = urllib2.urlopen(req, None, 5)
  html_string = response.read()
  response.close()
  logger.debug("TRACEOUT: sendData - thingspeak response: %s", html_string)


def main():

  hutch_temp = 15.0 # TODO: reset to zero, this is just to keep off during temperature tests
  status = ''

  parser = argparse.ArgumentParser()
  parser.add_argument("-n", "--cosymin", default=8.0, type=float, help='The minimum desired hutch temperature.')
  parser.add_argument("-x", "--cosymax", default=10.0, type=float, help='The temperature at which to turn off the heater.')
  args = parser.parse_args()

  logger.debug('CosyHutch min=%.2f max=%.2f', args.cosymin, args.cosymax)

  SENSORS.append(Sensor('field1', DEVICEPATH + '28-000008e748b9', 'Outside'))
  SENSORS.append(Sensor('field2', DEVICEPATH + '28-011590390dff', 'Lavatory'))
  SENSORS.append(Sensor('field3', DEVICEPATH + '28-0115909108ff', 'Boudoir'))
  SENSORS.append(Sensor('field4', DEVICEPATH + '28-011590a84eff', 'Living Room'))

  logger.debug('Reading temperatures...')
  for sensor in SENSORS:
    status = sensor.read_temperature(status)
  logger.debug(status)

  hutch_temp = SENSORS[2].temperature
  try: # control
    if os.path.isfile(LOCKFILE): # ensure locked off
      switch_off(1)
      status = '%s switched off in lock' % status
    elif hutch_temp >= args.cosymax:
      switch_off(1)
      status = '%s switched off %.2f > %.2f (high)' % (status, hutch_temp, args.cosymax)
    elif hutch_temp <= args.cosymin:
      switch_on(1)
      status = '%s switched on %.2f < %.2f (low)' % (status, hutch_temp, args.cosymin)
    else:
      status = '%s stable' % status
    logger.info(status)
  except Exception:
    status = 'Control error'
    logger.exception(status)

  datalogger.info("%f\t%.2f\t%.2f\t%.2f\t%.2f", time.time(), SENSORS[0].temperature, SENSORS[1].temperature, SENSORS[2].temperature, SENSORS[3].temperature)
    
  try:
    sendData(status)
  except Exception:
    logger.exception('Error sending data.')

  logger.debug('...cleaning up...')
  GPIO.cleanup()
  logger.debug('...done.')

if __name__=="__main__":
  main()
