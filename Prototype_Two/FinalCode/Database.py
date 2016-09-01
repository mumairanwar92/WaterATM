#!usr/bin/python
import MySQLdb

class Database():
	db=None
	curs=None
	def __init__(self):
		self.db=MySQLdb.connect(host="localhost", user="pi", passwd="password",db="WaterATM")
		self.curs=(self.db).cursor()

	def insertTransData(self,RFID, Amount, Date, Time, FilePath):
		startSynt="INSERT INTO transData VALUES ("
		data=str(RFID)+", "+str(Amount)+", '"+str(Date)+"', '"+str(Time)+"', '"+str(FilePath)
		endSynt="');"
		command=startSynt+data+endSynt
		#print command
		(self.curs).execute(command)
		(self.db).commit()

	def insertAuthData(self, RFID, Balance):
		startSynt="INSERT INTO authData VALUES ("
		data=str(RFID)+", "+str(Balance)
		endSynt=");"
		command=startSynt+data+endSynt
		#print command
		(self.curs).execute(command)
		(self.db).commit()

	def alterAuthData(self,RFID, balance):
		startSynt="UPDATE authData SET Balance="
		middle=str(balance)+" WHERE RFID="+str(RFID)
		endSynt=";"
		command=startSynt+middle+endSynt
		#print command
		(self.curs).execute(command)
		(self.db).commit()

	def extractAuthData(self,RFID):
		syntax="SELECT * FROM authData WHERE RFID="
		command=syntax+str(RFID)+";"
		#print command
		(self.curs).execute(command)
		for row in (self.curs).fetchall():
			#print row
			if (str(RFID) == str(row[0])):
				return True, row[1];
		return False, 0;
