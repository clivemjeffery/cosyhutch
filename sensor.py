import sys
import logging
import logging.config

if sys.platform == 'darwin':
  logging.config.fileConfig('simlog.conf')
else:
  logging.config.fileConfig('/home/pi/cosyhutch/logging.conf')
logger = logging.getLogger('cosylog')

class Sensor():
  def __init__(self, field, file):
    self.file = file
    self.filetext = ''
    self.field = field
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
      self.status = 'Error reading %s' % (self.file)

  def read_temperature(self, last_status): # need to improve to detect CRC errors and removed sensor (see log2.sh)
    self.read()
    if self.status == 'OK':
      temp = self.filetext[1].find('t=')
      if temp != -1:
        temp = self.filetext[1].strip()[temp+2:]
        self.temperature = float(temp)/1000.0
        return last_status
      else:
        self.status = 'Could not find t= key in file %s' % (self.file)
    return self.status

    
  def __repr__(self):
    return '%s : %s : %s : t=%.2f' % (self.field, self.file, self.status, self.temperature)