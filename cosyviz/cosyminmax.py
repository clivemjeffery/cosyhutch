#!/usr/bin/python
'''
A COSYHUTCH script to update min and max temperatures
'''
import os
import glob
import sys
import time
import csv
import argparse
from datetime import datetime

class MinMax:
  min = 100.00
  minTime = datetime.now()
  max = -100.00
  maxTime = datetime.now()
  def update(self,  newTemp, newTime):
    if newTemp > self.max:
      self.max = newTemp
      self.maxTime = newTime
    if newTemp < self.min:
      self.min = newTemp
      self.minTime = newTime

  def to_s(self):
    return "     %f (%s) - %f (%s)" % (self.max, self.maxTime.strftime('%Y-%m-%dT%H:%M:%S.%fZ'), self.min, self.minTime.strftime('%Y-%m-%dT%H:%M:%S.%fZ'))

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("logpath", help='path to cosyhutch log files.')
  parser.add_argument("outfile", help='output file to write.')
  args = parser.parse_args()

  print "Starting..."

  # stop after the file named for the current hour
  stopfile = '%s/data.%s.log' % (args.logpath, datetime.utcnow().strftime('%H'))
  print "  Stopfile is %s" % stopfile
  stopfileseen = False

  # outside temperature range over the 24 hour period
  range24Hour = MinMax()

  print "  Reading data files in %s..." % args.logpath

  files = glob.glob(args.logpath + '/data.*.log')
  files.sort(key=os.path.getmtime)
  for file in files:
    if not stopfileseen:
      reader = csv.DictReader(open(file, 'rb'), delimiter='\t', fieldnames=['time','outside','lavvy','boudoir','living','status'])
      print "  Opened %s" % file
      rows = 0
      print "     Reading..."

      # local file (hour) temperature range
      rangeHour = MinMax()

      try:
        for row in reader:
          rows = rows + 1
          datatime = datetime.strptime(row['time'],'%Y-%m-%d %H:%M:%S.%f')
          tempNow = float(row['outside'])

          rangeHour.update(tempNow, datatime)
          range24Hour.update(tempNow, datatime)

      except csv.Error:
        print('      csv choked on row %i' % (rows))
      print "      ...read %i rows." % rows
      stopfileseen = (file == stopfile)

    print "    File range is %s" % rangeHour.to_s()
    print "    Stopfile seen? %s" % stopfileseen

  print "  24 hour range is %s" % range24Hour.to_s()

  print "    Opening output file for write..."
  of = open(args.outfile, 'w')
  print "    ...opened."

  of.write("something")
  print "  ...wrote something."

  print "Ended."

if __name__=="__main__":
  main()
