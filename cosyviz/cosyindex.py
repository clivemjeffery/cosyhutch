#!/usr/bin/python
'''
A COSYHUTCH script to write an HTML file with latest temperatures.
'''
import os
import sys
import time
import csv
import argparse

def svg_rect(x, y, w, h, radius=0, stroke_width=2, stroke='black', fill='white'):
  svg = '<rect x="%i" y="%i" width="%i" height="%i" rx="%i" ry="%i" stroke-width="%i" stroke="%s" fill="%s" />' % (x, y, w, h, radius, radius, stroke_width, stroke, fill)
  return svg

def svg_text_in_rect(caption, x, y, w, h, radius=0, stroke_width=2, stroke='black', fill='white'):
  svg = svg_rect(x, y, w, h, radius, stroke_width, stroke, fill)
  svg = '%s\n<text x="%i" y="%i" font-family="arial" font-size="32" fill="black" text-anchor="middle" alignment-baseline="central">%s</text>' % (svg, x+w/2, y+h/2, caption)
  return svg

def svg_temperature(x, y, caption, temperature, stroke='blue'):
  svg = svg_rect(x, y, 100, 50, 5, 5, stroke, 'black')
  svg = '%s\n<text x="%i" y="%i" font-family="arial" font-size="18" fill="%s">%s</text>' % (svg, x, y-5, stroke, caption)
  svg = '%s\n<text x="%i" y="%i" font-family="arial" font-size="32" fill="white" text-anchor="middle" alignment-baseline="central">%.1f</text>' % (svg, x+50, y+25, temperature)
  return svg
  
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
    timestr = time.strftime("%I:%M %p", time.gmtime(float(row['time'])))
    template = template.replace('$time', svg_text_in_rect(timestr,615,5,180,50,5,5))
    template = template.replace('$outside', svg_temperature(50, 250, 'Outside', float(row['outside']), 'cyan'))
    template = template.replace('$lavvy', svg_temperature(75, 100, 'Lavatory', float(row['lavvy']), 'blue'))
    template = template.replace('$living', svg_temperature(260, 80, 'Lounge', float(row['living']), 'wheat'))
    template = template.replace('$boudoir', svg_temperature(625, 90, 'Boudoir', float(row['living']), 'green'))
  print "  ...done."

  print "  Writing output file..."
  of.write(template)
  print "  ...done."

  print "Ended."

if __name__=="__main__":
  main()
