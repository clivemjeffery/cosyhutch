#!/usr/bin/python
'''
A COSYHUTCH script intended to be suitable single time call from cron.
Uses logging configured in logging.conf.
'''
import os
import sys
import time
from datetime import datetime, timedelta
import urllib            # URL functions
import urllib2           # URL functions
import subprocess
if sys.platform == 'darwin':
  from energeniesim import switch_on, switch_off
else:
  import RPi.GPIO as GPIO
  from energenie import switch_on, switch_off
import logging
from logging.handlers import RotatingFileHandler
import argparse
from sensor import Sensor

################# Default Constants #################
THINGSPEAKKEY = 'BKW4Q7PQGF3S18EG'
THINGSPEAKURL = 'https://api.thingspeak.com/update'
LOCKFILE = '/home/pi/cosyhutch/cosy.lock'
#####################################################
logger = logging.getLogger('cosylog')
logpathger = logging.getLogger('cosylogpath')

SENSORS = []

def sendData(status):
  logger.debug("TRACEIN: sendData")
  html_string = 'placeholder for response'
  if sys.platform == 'darwin':
    logger.debug(' - Placeholder for post to thingspeak.')
  else:
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

def create_logger(logpath):
  if not os.path.isdir(logpath):   # create log directory
    os.makedirs(logpath) # don't catch any errors, let them propagate
  # The above also helps out open_data_logfile, bad coupling but meh

  logger = logging.getLogger('cosylog')
  logger.setLevel(logging.ERROR)
  ch = logging.handlers.RotatingFileHandler(logpath + "/cosy.log",'a',2097152,10)
  chf = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
  ch.setFormatter(chf)
  logger.addHandler(ch)

  logger.debug("CREATED: cosylog")

def open_data_logfile(logpath):
  fn = logpath + '/data.%s.log' % datetime.utcnow().strftime('%H')
  logger.debug("Looking for log file %s", fn)
  if os.path.exists(fn):
    last_modified = datetime.fromtimestamp(os.path.getmtime(fn))
    # If the log file is less than 2 hours old ----------------V then append...
    if (datetime.utcnow() - last_modified) < timedelta(0,60*60*2): 
      f = open(fn, 'a')
      logger.debug("Appending to log file %s", fn)
    # ...otherwise overwrite, this should be OK as previous day's file should be at least 11 hours older
    else: 
      f = open(fn, 'w')
      logger.debug("Rolled over log file %s", fn)

  else:
    f = open(fn, 'w')
    logger.debug("Created log file %s", fn)
  return f

def main():

  hutch_temp = 15.0 # TODO: reset to zero, this is just to keep off during temperature tests
  status = ''
  heat_status = 'UNSET' # U=unset, L=locked off, N=switched on,F=switched off, S=left stable

  parser = argparse.ArgumentParser()
  parser.add_argument("devicepath", help="Path to sensor device files.")
  parser.add_argument("logpath", help="Path to log files.")
  parser.add_argument("-n", "--cosymin", default=8.0, type=float, help='The minimum desired hutch temperature.')
  parser.add_argument("-x", "--cosymax", default=10.0, type=float, help='The temperature at which to turn off the heater.')
  
  args = parser.parse_args()

  DEVICEPATH = args.devicepath
  create_logger(args.logpath)
  logger.debug('CosyHutch min=%.2f, max=%.2f, devicepath=%s, logpath=%s', args.cosymin, args.cosymax, args.devicepath, args.logpath)

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
      heat_status = 'LOCKED'
    elif hutch_temp >= args.cosymax:
      switch_off(1)
      status = '%s switched off %.2f > %.2f (high)' % (status, hutch_temp, args.cosymax)
      heat_status = 'OFF'
    elif hutch_temp <= args.cosymin:
      switch_on(1)
      status = '%s switched on %.2f < %.2f (low)' % (status, hutch_temp, args.cosymin)
      heat_status = 'ON'
    else:
      status = '%s stable' % status
      heat_status = 'STABLE'
    logger.info(status)
  except Exception:
    status = 'Control error'
    logger.exception(status)

  logfile = open_data_logfile(args.logpath)
  logfile.write('%s\t' % datetime.utcnow())
  for sensor in SENSORS:
    logfile.write('%.2f\t' % sensor.temperature)
  logfile.write('%s\n' % heat_status)
  logfile.close()

  try:
    sendData(status)
  except Exception:
    logger.exception('Error sending data.')

  logger.debug('...cleaning up...')
  if sys.platform != 'darwin':
    GPIO.cleanup()
  logger.debug('...done.')

if __name__=="__main__":
  main()
