from commands import *

while True:
	status, text=getstatusoutput("sudo killall python")
	status, text=getstatusoutput("sudo python /home/pi/Desktop/WaterATM/FinalCode/main.py")
	print text
	time.sleep(30*60)