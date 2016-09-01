#!usr/bin/python

import RPi.GPIO as GPIO
import time,sys
from commands import *
import subprocess

import flowMeter

flow=flowMeter.flowMeter()

def roundOff(value):
#	if value > 25000:
#		return (25000);
	if value > 18000 and value < 25000:
		return (20000);
	elif value > 13000 and value < 18000:
		return (15000);
	elif value > 8000 and value < 13000:
		return (10000);
	elif value > 3000 and value < 8000:
		return (5000);
	else:
		return (value);

def main():
    flow.EnablePulseInterrupt()
    while True:
	flow.calFlow()
	time.sleep(1)
				

if __name__ == '__main__':
        try:
                main()
        except KeyboardInterrupt:
                pass
        finally:
                GPIO.cleanup()
                sys.exit()

