import sys
import logging
import logging.config

if sys.platform == 'darwin':
  logging.config.fileConfig('simlog.conf')
else:
  logging.config.fileConfig('/home/pi/cosyhutch/logging.conf')
logger = logging.getLogger('cosylog')

class Sensor():
  def __init__(self, field, file, physical):
    self.file = file
    self.filetext = ''
    self.field = field
    self.physical = physical
    self.temperature = 0.0
    self.crc = ''
    self.status = 'NEW'

  def read(self):
    try:
      f = open(self.file + '/w1_slave', 'r')
      self.filetext = f.readlines()
      f.close()
      self.status = 'OK'
    except Exception:
      self.status = 'read error'

  def read_temperature(self, status_accumulator): # need to improve to detect CRC errors and removed sensor (see log2.sh)
    self.read()
    if self.status == 'OK':
      temp = self.filetext[1].find('t=')
      if temp != -1:
        temp = self.filetext[1].strip()[temp+2:]
        self.temperature = float(temp)/1000.0
        return "%s - %s (%.2f)" % (status_accumulator, self.physical, self.temperature)
      else:
        self.status = 'No t= key in file' % (self.file)
    return "%s - %s (%s)" % (status_accumulator, self.physical, self.status)

    
  def __repr__(self):
    return '%s : %s : %s : %s : t=%.2f' % (self.physical, self.field, self.file, self.status, self.temperature)