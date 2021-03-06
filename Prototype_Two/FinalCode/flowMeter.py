#!/usr/bin/env python

import RPi.GPIO as GPIO
import time, sys


class flowMeter:
	flowPin=18
	count=0
	count1=0
	totalFlow=0
	startTime=0
	elapsedTime=0
	def __init__(self):
		self.pinModeSetup()

	def pinModeSetup(self):
		GPIO.setmode(GPIO.BCM)
		GPIO.setwarnings(False)
		GPIO.setup(self.flowPin,GPIO.IN)
	        
	def PulseIntrptRising(self,channel):
	        if self.count == 1:
			self.startTime=time.time()
			self.count=self.count+1
		else:
			self.count=self.count+1

	def EnablePulseInterrupt(self):
	        GPIO.add_event_detect(self.flowPin, GPIO.RISING, callback=self.PulseIntrptRising)	        
	def DisablePulseInterrupt(self):
	        GPIO.remove_event_detect(self.flowPin)	
		   
	def calFlow(self):
		'''
		pulses = 0
		self.elapsedTime = 0
	        self.elapsedTime = (float)(time.time()-self.startTime)
	        pulses=self.count
	        self.count=0
		#self.flowrate=(1000/(60*pulses*7.5*self.elapsedTime))*1000
		self.flowrate=round((pulses/self.elapsedTime)*2.11338/(7.5*60),3)
	        #self.totalFlow = self.totalFlow + (self.flowrate*.78)
		
	        print "Pulses: "+str(pulses) +" Time Elapsed: "+str(self.elapsedTime) + " Freq = " + str(pulses/self.elapsedTime) +"Hz Flowrate: "+str(self.flowrate)#+" TotalFlow: "+str(self.totalFlow)+" Time Elapsed: "+str(self.elapsedTime)
	        self.elapsedTime=0
		'''
		print "Pulses: "+str(self.count)

