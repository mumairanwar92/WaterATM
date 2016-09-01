#!usr/bin/python

import RPi.GPIO as GPIO
import time,sys
from commands import *
import subprocess

import LCD
import MFRC522
import webCam
import Database
import USBModem

greenButton=23
redButton=24
solePin=25
flowPin=18

greenRFIDIndic=5
redRFIDIndic=6
greenButtonIndic=13
redButtonIndic=19


mCode = "pi62244632"

LCD_ = LCD.LCD()
rfidReader = MFRC522.MFRC522()
cam = webCam.webCam()
db=Database.Database()


flow_count=0
flow_totalFlow=0
flow_startTime=0
flow_elapsedTime=0


def pinModeSetup():
    	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False)
    	GPIO.setup(greenButton, GPIO.IN)
    	GPIO.setup(redButton, GPIO.IN)    
	GPIO.setup(solePin,GPIO.OUT)
	GPIO.output(solePin,False)
	GPIO.setup(greenRFIDIndic,GPIO.OUT)
	GPIO.setup(redRFIDIndic,GPIO.OUT)
	GPIO.setup(redButtonIndic,GPIO.OUT)
	GPIO.setup(greenButtonIndic,GPIO.OUT)
	GPIO.setup(flowPin,GPIO.IN)#, pull_up_down=GPIO.PUD_DOWN)


	GPIO.output(redRFIDIndic, GPIO.LOW)
	GPIO.output(greenRFIDIndic, GPIO.LOW)
	GPIO.output(greenButtonIndic, GPIO.LOW)
	GPIO.output(redButtonIndic, GPIO.LOW)
	#sys.setrecursionlimit(5000)

def readCard():
    if GPIO.input(redButton) == 0:
        time.sleep(5)
	if GPIO.input(redButton) == 0:
		LCD_.clearLCD()
		allOn()
		LCD_.printLCD("System Shutting Down",1,1)
		LCD_.printLCD("Wait for 1 Minute",2,1)
		text, status = getstatusoutput('sudo shutdown -h now')
		time.sleep(10)
    # Scan for card
    (status,TagType) = rfidReader.MFRC522_Request(rfidReader.PICC_REQIDL)
    #print status, TagType
    # If a card is found
    if status == rfidReader.MI_OK:
        # Get the UID of the card
        (status,uid) = rfidReader.MFRC522_Anticoll()
        # If we have the UID, continue
        if status == rfidReader.MI_OK:
            CardID=(uid[0]<<(3*8))+(uid[1]<<(2*8))+(uid[2]<<(1*8))+uid[3]
            return CardID;
	else:
	    return None;
    else:
        return None;

def digitalWrite(pin, mode):
	GPIO.output(pin, mode)
	
def pulseRead():
	start=stop=time.time()
	while GPIO.input(flowPin) == 1:
		if(GPIO.input(redButton) == 0):
			return (-1);
		start = time.time()
	while GPIO.input(flowPin) == 0:
		if(GPIO.input(redButton) == 0):
			return (-1);
		stop = time.time()
	pulseWidth = (stop-start)*1000
	return (round(pulseWidth,1))

def calFlow():
	global flow_startTime, flow_totalFlow
	flow_elapsedTime = (time.time()-flow_startTime)
	flow_startTime = time.time()
	pulseWidth = round(pulseRead(),3)
	freq = 0
	if (pulseWidth > 0 and pulseWidth < 1000):
		freq = 1000/(2*pulseWidth)
	else:
		freq = 0
	if (freq > 300):
		freq = 200
	pulses = freq*flow_elapsedTime
	flowRate = round((pulses/flow_elapsedTime)*(2.11338*1000)/(7.5*60),3)
	flow_totalFlow += (flowRate)
	LCD_.printLCD("Flow: "+str((int)(flow_totalFlow/1000))+" Litres",4,1)
	print str(round(pulses,0))+" Pulses in "+str(flow_elapsedTime)+" seconds with pulseWidth: "+str(pulseWidth)+" and Freq: "+str(freq)+" flowRate: "+str(flowRate)+" totalFlow: "+str(flow_totalFlow)

def readGreenButton():
    time_ = time.time()
    count = 0
    while True:
	if (time.time()- time_ > 1):
		count = count+1
		if (count%2 == 0):
			digitalWrite(greenButtonIndic, GPIO.HIGH)
			digitalWrite(redButtonIndic, GPIO.LOW)
		elif (count%2 == 1):
			digitalWrite(greenButtonIndic, GPIO.LOW)
			digitalWrite(redButtonIndic, GPIO.HIGH)
		time_ = time.time()
        if GPIO.input(greenButton) == 0:
            return 1
	if GPIO.input(redButton) == 0:
	    return 0


def readRedButton():
    global flow_startTime
    time_ = time.time()
    count = 0
    digitalWrite(greenButtonIndic, GPIO.HIGH)
    flow_startTime = time.time()
    while True:
        if GPIO.input(redButton) == 0:
            return
        else:
            if (time.time()- time_ > 1):
		count = count+1
		if (count%2 == 0):
			digitalWrite(redButtonIndic, GPIO.HIGH)
		elif (count%2 == 1):
			digitalWrite(redButtonIndic, GPIO.LOW)
		calFlow()
                time_=time.time()
            else:
                pass

def _3gOn():
	subprocess.Popen("sudo sh /home/pi/3Gconnect.sh &", shell=True)
	subprocess.Popen("sudo sh /home/pi/ssh_tunnel.sh &", shell=True)

def Authenticate(RFID):
	dbresp, balance = db.extractAuthData(RFID)
	print dbresp, balance
	if dbresp is False:
		status, text = getstatusoutput("ping -c 1 8.8.8.8")
		if (text.find('Network is unreachable') != -1):
			_3gOn()
			return -2;
		balance = 0
		status, balance = (USBModem.authRequest(RFID, mCode))
		if status == 0:
			print (status, balance)
			return -2;
		elif status == 'registered':
			print 'User Registered, Balance: '+str(balance)
			db.insertAuthData(RFID, balance)
			if float(balance) > 0:
				LCD_.printLCD("Balance: "+str(round(balance,2)),2,1)
				return 1;	# Now, Locally exists and balance is true
			else:
				return 0;
		elif status == 'unregistered':
			print 'User Unregistered'
			return -1;
		
	if dbresp is True:
		if balance > 0:
			LCD_.printLCD("Balance: "+str(round(balance,2)),2,1)
			return 1;	# Locally exist and balance is true
		else:
			status, text = getstatusoutput("ping -c 1 8.8.8.8")
	                if (text.find('Network is unreachable') != -1):
        	                print "Check GSM"
                	        return -2;
			status, balance = (USBModem.authRequest(RFID, mCode))
			print (status, balance)
			if status == 'registered':
				db.alterAuthData(RFID, balance)
				if float(balance) > 0:
					LCD_.printLCD("Balance: "+str(round(balance,2)),2,1)
					return 1;	# Now, Locally exists and balance is true
				else:
					LCD_.printLCD("Balance: "+str(round(balance,2)),2,1)
					return 0;
			elif status == 'unregistered':
				print 'User Unregistered'
				return -1;


def Transaction(RFID, Amount, Date, Time): #transRequest(RFID, Amount, Date, Time):
	status, text = getstatusoutput("ping -c 1 8.8.8.8")
        if (text.find('Network is unreachable') != -1):
		_3gOn()
		return;

	balance = 0
	balance = (USBModem.transRequest(RFID, 'pi62244632', Amount, Date, Time))
	#print balance
	LCD_.printLCD("Balance: "+str((int)(round(balance,1))),2,1)
	LCD_.printLCD("Please Wait",4,1)
	LCD_.printLCD("",4,3)
	db.alterAuthData(RFID, balance)
	
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
def resetAll():
	resetIndics()
	time.sleep(1)
	LCD_.printLCD(" ",3,1)
	LCD_.printLCD(" ",4,1)

def resetIndics():
	digitalWrite(redRFIDIndic, GPIO.LOW)
        digitalWrite(greenRFIDIndic, GPIO.LOW)
        digitalWrite(redButtonIndic, GPIO.LOW)
        digitalWrite(greenButtonIndic, GPIO.LOW)

def allOn():
	digitalWrite(greenRFIDIndic, GPIO.HIGH)
        digitalWrite(redButtonIndic, GPIO.HIGH)
        digitalWrite(greenButtonIndic, GPIO.HIGH)

def main():
    global flow_count, flow_elapsedTime, flow_startTime, flow_totalFlow
    time_1 = time.time()
    count_ = 0
    pinModeSetup()
    LCD_.clearLCD()
#    LCD_.printLCD("System Booting Up",1,1)
#    LCD_.printLCD("Please Wait....",2,1)
#    time.sleep(40)
    while True:
	#flow_totalFlow = 0
        getTime="date +\"%H:%M:%S\""
        status, Time=getstatusoutput(getTime)
        LCD_.printLCD("SPLASH NEPAL",1,2)
        #LCD_.printLCD("Time  "+str(Time),2,2)
        LCD_.printLCD("Please Scan Card.",2,1)
	if (time.time()- time_1 > 1):
		count_=count_+1
		if (count_%2 == 0):
			digitalWrite(greenRFIDIndic, GPIO.HIGH)
		elif (count_%2 == 1):
			digitalWrite(greenRFIDIndic, GPIO.LOW)
		time_1 = time.time()
	cardNum=readCard()
#	print cardNum
	if cardNum is not None:
		LCD_.clearLCD()
		LCD_.printLCD("Card No :"+str(cardNum),1,1)
		authFlag = Authenticate(cardNum)
		if authFlag == 1:
			digitalWrite(greenRFIDIndic, GPIO.HIGH)
			LCD_.printLCD("GREEN = Start",3,1)
			LCD_.printLCD("RED = Cancel",4,1)
			startFlag = readGreenButton()
			if startFlag == 0:
				LCD_.clearLCD()
				resetAll()
				continue;
			elif startFlag == 1:
				flow_startTime = time.time()
				Date, Time, filePath = cam.takePic()
				flow_count = 0
				time.sleep(2)
				GPIO.output(solePin,True)
				LCD_.printLCD("RED = Cancel",3,1)
				LCD_.printLCD("Flow: 0 Litres",4,1)
				readRedButton()
				flow_totalFlow = round(flow_totalFlow,0)
				LCD_.printLCD("Water: "+str((round((flow_totalFlow/1000),1)))+" Ltrs",3,1)
				LCD_.printLCD("Please Wait",4,1)
				GPIO.output(solePin,False)    
				time.sleep(1)
				if flow_totalFlow > 100:
					Transaction(cardNum, (int)(flow_totalFlow), Date,Time)
					resetIndics()
					cam.uploadPic(filePath)
					#db.insertTransData(cardNum, flow_totalFlow, Date,Time,filePath)
				
		elif authFlag == 0:
			digitalWrite(greenRFIDIndic, GPIO.LOW)
			digitalWrite(redRFIDIndic, GPIO.HIGH)
			LCD_.printLCD("Please Recharge",3,1)
			LCD_.printLCD("Your Card",4,1)
		elif authFlag == -1:
			digitalWrite(greenRFIDIndic, GPIO.LOW)
			digitalWrite(redRFIDIndic, GPIO.HIGH)
			LCD_.printLCD("Please Register Your",3,1)
			LCD_.printLCD("Card From Vendor",4,1)
		elif authFlag == -2:
			digitalWrite(greenRFIDIndic, GPIO.LOW)
			digitalWrite(redRFIDIndic, GPIO.HIGH)
			LCD_.printLCD("Please Connect To", 3, 1)
			LCD_.printLCD("Internet", 4, 1)
		time.sleep(3)
		resetAll()


if __name__ == '__main__':
        try:
                main()
        except KeyboardInterrupt:
                pass
        finally:
                GPIO.cleanup()
                sys.exit()

