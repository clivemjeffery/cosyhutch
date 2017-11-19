#!/usr/bin/python
'''
A COSYHUTCH script to write an HTML file with latest temperatures.
'''
import os
import glob
import sys
import time
import csv
import argparse
from datetime import datetime

def svg_rect(x, y, w, h, radius=0, stroke_width=2, stroke='black', fill='white'):
  svg = '<rect x="%i" y="%i" width="%i" height="%i" rx="%i" ry="%i" stroke-width="%i" stroke="%s" fill="%s" />' % (x, y, w, h, radius, radius, stroke_width, stroke, fill)
  return svg

def svg_text_in_rect(caption, x, y, w, h, radius=0, stroke_width=2, stroke='black', fill='white'):
  svg = svg_rect(x, y, w, h, radius, stroke_width, stroke, fill)
  svg = '%s\n<text x="%i" y="%i" font-family="arial" font-size="32" fill="black" text-anchor="middle" alignment-baseline="central">%s</text>' % (svg, x+w/2, y+h/2, caption)
  return svg

def txt_text_in_rect(caption, x, y, w, h, radius=0, stroke_width=2, stroke='black', fill='white'):
  txt = '<span style="color:%s;">%s</span>' % (stroke, caption)
  return txt 

def svg_temperature(x, y, caption, temperature, stroke='blue'):
  svg = svg_rect(x, y, 100, 50, 5, 5, stroke, 'black')
  svg = '%s\n<text x="%i" y="%i" font-family="arial" font-size="18" fill="%s">%s</text>' % (svg, x, y-5, stroke, caption)
  svg = '%s\n<text x="%i" y="%i" font-family="arial" font-size="32" fill="white" text-anchor="middle" alignment-baseline="central">%.1f</text>' % (svg, x+50, y+25, temperature)
  return svg

def txt_temperature(x, y, caption, temperature, stroke='blue'):
  txt = '<span style="color:%s;">%.1f</span>' % (stroke, temperature)
  return txt
  
def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("template", help='template file to read.')
  parser.add_argument("logpath", help='path to log files.')
  parser.add_argument("index", help='index file to write.')
  args = parser.parse_args()

  print "Starting..."
  print "  Opening template..."
  tf = open(args.template, 'r')
  template = tf.read()
  print "  ...done."

  # stop after the file named for the current hour
  stopfile = '%s/data.%s.log' % (args.logpath, datetime.utcnow().strftime('%H'))
  print stopfile
  stopfileseen = False

  # collect data for the day's graph's series
  gd_outside = ""
  gd_lavvy = ""
  gd_living = ""
  gd_boudoir = ""

  print "  Reading data files in %s..." % args.logpath

  files = glob.glob(args.logpath + '/data.*.log')
  files.sort(key=os.path.getmtime)  
  for file in files:
    if not stopfileseen:
      reader = csv.DictReader(open(file, 'rb'), delimiter='\t', fieldnames=['time','outside','lavvy','boudoir','living','status'])
      print "  Opened %s" % file
      rows = 0
      print "     Reading..."
      for row in reader:
        rows = rows + 1
        datatime = datetime.strptime(row['time'],'%Y-%m-%d %H:%M:%S.%f')
        outside = float(row['outside'])
        lavvy = float(row['lavvy'])
        living = float(row['living'])
        boudoir = float(row['boudoir'])
        status = row['status']
        gd_outside = "%s\t{x: new Date('%s'), y: %.2f},\n" % (gd_outside, datatime.strftime('%Y-%m-%dT%H:%M:%S.%fZ'), outside)
        gd_lavvy = "%s\t{x: new Date('%s'), y: %.2f},\n" % (gd_lavvy, datatime.strftime('%Y-%m-%dT%H:%M:%S.%fZ'), lavvy)
        gd_living = "%s\t{x: new Date('%s'), y: %.2f},\n" % (gd_living, datatime.strftime('%Y-%m-%dT%H:%M:%S.%fZ'), living)
        gd_boudoir = "%s\t{x: new Date('%s'), y: %.2f},\n" % (gd_boudoir, datatime.strftime('%Y-%m-%dT%H:%M:%S.%fZ'), boudoir)
      print "     ...read %i rows." % rows
      stopfileseen = (file == stopfile)
    print stopfileseen

  print "    Opening output file for write..."
  of = open(args.index, 'w')
  print "    ...done."

  print "  Replacing tags in template..."
  template = template.replace('$time', txt_text_in_rect(datatime.strftime("%I:%M %p"),615,5,180,50,5,5))
  template = template.replace('$outside', txt_temperature(50, 250, 'Outside', outside, 'orange'))
  template = template.replace('$lavvy', txt_temperature(75, 100, 'Lavatory', lavvy, 'dodgerblue'))
  template = template.replace('$living', txt_temperature(260, 80, 'Lounge', living, 'mediumseagreen'))
  template = template.replace('$boudoir', txt_temperature(625, 90, 'Boudoir', boudoir, 'orchid'))
  template = template.replace('$status', txt_text_in_rect(status,550,220,180,50,5,5,'red'))
  print "  ...done."

  gd_outside = gd_outside[:-2] # remove last comma and newline
  template = template.replace('$graph_series_outside', gd_outside)
  gd_outside = gd_boudoir[:-2]
  template = template.replace('$graph_series_boudoir', gd_boudoir)
  gd_outside = gd_boudoir[:-2]
  template = template.replace('$graph_series_lavvy', gd_lavvy)
  gd_outside = gd_boudoir[:-2]
  template = template.replace('$graph_series_living', gd_living)

  print "  Writing output file..."
  of.write(template)
  print "  ...done."

  print "Ended."

if __name__=="__main__":
  main()
