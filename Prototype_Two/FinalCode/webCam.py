#!/usr/bin/python

from commands import *



class webCam():
	def takePic(self):
		getDate="date +\"%Y-%m-%d\""
		getTime="date +\"%H:%M:%S\""
		status, Date=getstatusoutput(getDate)
		status, Time=getstatusoutput(getTime)
		dateTime=str(Date)+"_"+str(Time)
		filePath="/home/pi/Desktop/WaterATM/WebCamPics/"+dateTime+".jpg"
		command="sudo fswebcam -s brightness=70% "+filePath
		status, text=getstatusoutput(command)
#		print status
#		print text
		return (Date, Time, filePath)
	def uploadPic(self, filePath):
		username = " wateratm@mustafanaseem.com"
		passwrd = " wateratm.net"
		directory = " /dashboard/images/"
		server = " ftp.mustafanaseem.com"
		command="ncftpput -u "+username+" -p"+passwrd+server+directory+" "+filePath
#		print command
		status, text=getstatusoutput(command)
		#print status, text
		if (text.find('kB/s') != 0):
			status, text=getstatusoutput("sudo rm -rf "+filePath )
			#print status, text
		else:
			self.uploadPic(filePath)
		
