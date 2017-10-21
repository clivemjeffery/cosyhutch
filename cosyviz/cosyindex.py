#!/usr/bin/python
'''
A COSYHUTCH script to write an HTML file with latest temperatures.
'''
import os
import sys
import time
import csv
import argparse

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("template", help='template file to read.')
  parser.add_argument("data", help='data file to read.')
  parser.add_argument("index", help='index file to write.')
  args = parser.parse_args()

  print "Starting..."
  print "  Opening template..."
  tf = open(args.template, 'r')
  template = tf.read()
  print "  ...done."

  print "  Creating and opening reader..."
  reader = csv.DictReader(open(args.data, 'rb'), delimiter='\t', fieldnames=['time','outside','lavvy','boudoir','living'])
  print "  ...done."

  print "  Writing read rows (expecting only one) into output file..."
  print "    Opening output file for write..."
  of = open(args.index, 'w')
  print "    ...done."

  print "  Replacing tags in template..."
  for row in reader:
    template = template.replace('$time', time.ctime(float(row['time'])))
    template = template.replace('$outside', row['outside'])
    template = template.replace('$lavvy', row['lavvy'])
    template = template.replace('$boudoir', row['boudoir'])
    template = template.replace('$living', row['living'])
  print "  ...done."

  print "  Writing output file..."
  of.write(template)
  print "  ...done."

  print "Ended."

if __name__=="__main__":
  main()
