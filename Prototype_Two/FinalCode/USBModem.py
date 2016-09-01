#!usr/bin/python
import urllib2

def authRequest(RFID, mCode):
	url='http://www.wateratm.net/dashboard/index.php/ApiEngine/Auth?rfid='
	compURL=url+str(RFID)+'&mcode='+mCode
	urlresp = 0
	print compURL
	urlresp = urllib2.urlopen(compURL, timeout=5).read()
	if urlresp is not 0:
		firstEnd = (urlresp.find(',"'))
		status = urlresp[(firstEnd+11):(urlresp.find('"}'))]
		balance = urlresp[11:firstEnd]
		return status, float(balance)
	else:
		return 0, 0
		
def transRequest(RFID, mCode, Amount, Date, Time):
	url='http://www.wateratm.net/dashboard/index.php/ApiEngine/IPushdata?rfid='
	compURL=url+str(RFID)+'&mcode='+mCode+'&amount='+str(Amount)+'&td='+str(Date)+'_'+str(Time)
	urlresp = 0
	print compURL
	urlresp = urllib2.urlopen(compURL, timeout=5).read()
	if urlresp is not 0:
		firstEnd = (urlresp.find('}'))
		balance = urlresp[11:firstEnd]
		return float(balance)
	else:
		return 0
