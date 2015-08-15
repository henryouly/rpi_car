#!/usr/bin/env python
from os import popen
import RPi.GPIO as gpio
import re 
import time

s = re.compile('[ :]')

gpio.setmode(gpio.BOARD)
PINS = [11, 12, 13, 15]
map(gpio.setup, PINS, [gpio.OUT] * 4)

def event_stream(deadzone=0,scale=32768):
  subprocess = popen('nohup xboxdrv','r',65536)
  while True:
    line = subprocess.readline()
    if 'Error' in line:
      raise ValueError(line)
    data = filter(bool,s.split(line[:-1]))
    if len(data)==42:
      # Break input string into a data dict
      data = { data[x]:int(data[x+1]) for x in range(0,len(data),2) }
      yield data 

def annotate(data):
  if data['RT'] != 0:
    if data['X1'] < 0:
      yield 'ForwardLeft'
    elif data['X1'] > 0:
      yield 'ForwardRight'
    else:
      yield 'Forward'
  elif data['LT'] != 0:
    if data['X1'] < 0:
      yield 'BackwardLeft'
    elif data['X1'] > 0:
      yield 'BackwardRight'
    else:
      yield 'Backward'
  elif data['X1'] < 0:
    yield 'SpinLeft'
  elif data['X1'] > 0:
    yield 'SpinRight'
  yield 'Stop'


_action_table = {
  'Stop': [True, True, True, True],
  'Forward': [True, False, True, False],
  'Backward': [False, True, False, True],
  'SpinLeft': [True, False, False, True],
  'SpinRight': [False, True, True, False],
  'ForwardLeft': [True, True, True, False],
  'ForwardRight': [True, False, True, True],
  'BackwardLeft': [True, True, False, True],
  'BackwardRight': [False, True, True, True],
}

def perform(action):
  action = next(action)
  print action
  map(gpio.output, PINS, _action_table[action]) 

for data in event_stream():
  perform(annotate(data))
