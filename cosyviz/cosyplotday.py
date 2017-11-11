#!/usr/bin/python
'''
A COSYHUTCH script to write a graph from the logs
'''
from datetime import datetime
import os
import glob
import argparse
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("logpath", help='path log files named data.HH.log')
  parser.add_argument("output", help='name of output file.')
  args = parser.parse_args()

  dataspec = {'names': ('time','outside','lavvy','boudoir','living'),'formats': ('datetime64[s]', 'float32', 'float16','float16', 'float16')}

  hours = mdates.HourLocator()   
  mins = mdates.MinuteLocator(30)  
  hoursFmt = mdates.DateFormatter('%H')

  dx = ox = bx = []
  for file in glob.iglob(args.logpath + '/data.*.log'):
    d, o, l, b, v = np.loadtxt(file, delimiter='\t', dtype=dataspec, unpack=True)
    d = d.astype('O')
    if d[0].date() == datetime.today().date(): # reject yesterday's data
      dx = np.append(dx, d)
      ox = np.append(ox, o)
      bx = np.append(bx, b)

  fig, ax = plt.subplots()
  ax.plot(dx, ox, label='Outside', linewidth=2)
  ax.plot(dx, bx, 'r', label='Boudoir', linewidth=1.5)

  # format the ticks
  ax.xaxis.set_major_locator(hours)
  ax.xaxis.set_major_formatter(hoursFmt)
  ax.xaxis.set_minor_locator(mins)

  tdy = datetime.today().date()
  datemin = tdy
  datemax = datetime(tdy.year, tdy.month, tdy.day+1)
  ax.set_xlim(datemin, datemax)
  ax.set_ylim(-2, 15)

  fig.savefig(args.output)

if __name__=="__main__":
  main() 