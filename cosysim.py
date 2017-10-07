#!/usr/bin/python
'''
COSYHUTCH simulator prototype.
Idea is to run under macOS to test and speed up development.
'''
import sys
import logging
import logging.config
import time
import urllib            # URL functions
import urllib2           # URL functions
from sensor import Sensor

if sys.platform == 'darwin':
  DEVICEPATH = './device_sim/'
  logging.config.fileConfig('simlog.conf')
else:
  logging.config.fileConfig('/home/pi/cosyhutch/logging.conf')
logger = logging.getLogger('cosylog')


################# Default Constants #################
THINGSPEAKURL = 'https://api.thingspeak.com/update'
THINGSPEAKKEY = 'BKW4Q7PQGF3S18EG'
#####################################################

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
  print('Getting platform')
  print(sys.platform)
  logger.info(sys.platform)

  SENSORS.append(Sensor('field1', DEVICEPATH + '28-000008e748b9'))
  SENSORS.append(Sensor('field2', DEVICEPATH + '28-011590390dff'))
  SENSORS.append(Sensor('field3', DEVICEPATH + '28-0115909108ff'))
  SENSORS.append(Sensor('field4', DEVICEPATH + '28-011590a84eff'))
  
  status = ''
  for sensor in SENSORS:
    print(sensor)
    status = sensor.read_temperature(status)
    print(sensor)

  sendData(status)

if __name__=="__main__":
  main()