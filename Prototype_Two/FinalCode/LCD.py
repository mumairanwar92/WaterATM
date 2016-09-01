#!/usr/bin/env python

# The wiring for the LCD is as follows:
# 1 : GND
# 2 : 5V
# 3 : Contrast (0-5V)*
# 4 : RS (Register Select)
# 5 : R/W (Read Write)       - GROUND THIS PIN
# 6 : Enable or Strobe
# 7 : Data Bit 0             - NOT USED
# 8 : Data Bit 1             - NOT USED
# 9 : Data Bit 2             - NOT USED
# 10: Data Bit 3             - NOT USED
# 11: Data Bit 4
# 12: Data Bit 5
# 13: Data Bit 6
# 14: Data Bit 7
# 15: LCD Backlight +5V**
# 16: LCD Backlight GND
 
#import
import RPi.GPIO as GPIO
import time


class LCD:
    # Define GPIO to LCD mapping
    LCD_RS = 2
    LCD_E  = 3
    LCD_D4 = 4
    LCD_D5 = 17
    LCD_D6 = 27
    LCD_D7 = 22

    # Define some device constants
    LCD_WIDTH = 20    # Maximum characters per line
    LCD_CHR = True
    LCD_CMD = False
     
    LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
    LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line
    LCD_LINE_3 = 0x94 # LCD RAM address for the 3rd line
    LCD_LINE_4 = 0xD4 # LCD RAM address for the 4th line
     
    # Timing constants
    E_PULSE = 0.0005
    E_DELAY = 0.0005


    def __init__(self):
        GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False)
        GPIO.setup(self.LCD_E, GPIO.OUT)  # E
        GPIO.setup(self.LCD_RS, GPIO.OUT) # RS
        GPIO.setup(self.LCD_D4, GPIO.OUT) # DB4
        GPIO.setup(self.LCD_D5, GPIO.OUT) # DB5
        GPIO.setup(self.LCD_D6, GPIO.OUT) # DB6
        GPIO.setup(self.LCD_D7, GPIO.OUT) # DB7
        self.lcd_init()
        self.lcd_byte(0x01, self.LCD_CMD)
        time.sleep(1)
    def clearLCD(self):
	self.printLCD("",1,3)
	self.printLCD("",2,3)
	self.printLCD("",3,3)
	self.printLCD("",4,3)

    def printLCD(self,text,lineNum,justify):
        if lineNum == 1:
            self.lcd_string(text,self.LCD_LINE_1,justify)
        elif lineNum == 2:
            self.lcd_string(text,self.LCD_LINE_2,justify)
        elif lineNum == 3:
            self.lcd_string(text,self.LCD_LINE_3,justify)
        elif lineNum == 4:
            self.lcd_string(text,self.LCD_LINE_4,justify)
    def lcd_init(self):
        self.lcd_byte(0x33,self.LCD_CMD) # 110011 Initialise
        self.lcd_byte(0x32,self.LCD_CMD) # 110010 Initialise
        self.lcd_byte(0x06,self.LCD_CMD) # 000110 Cursor move direction
        self.lcd_byte(0x0C,self.LCD_CMD) # 001100 Display On,Cursor Off, Blink Off
        self.lcd_byte(0x28,self.LCD_CMD) # 101000 Data length, number of lines, font size
        self.lcd_byte(0x01,self.LCD_CMD) # 000001 Clear display
        time.sleep(self.E_DELAY)
     
    def lcd_byte(self, bits, mode):
	GPIO.output(self.LCD_RS, mode) # RS
     
	# High bits
	GPIO.output(self.LCD_D4, False)
	GPIO.output(self.LCD_D5, False)
	GPIO.output(self.LCD_D6, False)
	GPIO.output(self.LCD_D7, False)
	if bits&0x10==0x10:
		GPIO.output(self.LCD_D4, True)
	if bits&0x20==0x20:
		GPIO.output(self.LCD_D5, True)
	if bits&0x40==0x40:
		GPIO.output(self.LCD_D6, True)
	if bits&0x80==0x80:
		GPIO.output(self.LCD_D7, True)
     
	#Toggle 'Enable' pin
	self.lcd_toggle_enable()
     
	#Low bits
	GPIO.output(self.LCD_D4, False)
	GPIO.output(self.LCD_D5, False)
	GPIO.output(self.LCD_D6, False)
	GPIO.output(self.LCD_D7, False)
	if bits&0x01==0x01:
		GPIO.output(self.LCD_D4, True)
	if bits&0x02==0x02:
		GPIO.output(self.LCD_D5, True)
	if bits&0x04==0x04:
		GPIO.output(self.LCD_D6, True)
	if bits&0x08==0x08:
		GPIO.output(self.LCD_D7, True)
     
	#Toggle 'Enable' pin
	self.lcd_toggle_enable()
     
    def lcd_toggle_enable(self):
	#Toggle enable
	time.sleep(self.E_DELAY)
	GPIO.output(self.LCD_E, True)
	time.sleep(self.E_PULSE)
	GPIO.output(self.LCD_E, False)
	time.sleep(self.E_DELAY)
     
    def lcd_string(self,message,line,style):
	#Send string to display
	#style=1 Left justified
	#style=2 Centred
	#style=3 Right justified
     
	if style==1:
		message = message.ljust(self.LCD_WIDTH," ")
	elif style==2:
		message = message.center(self.LCD_WIDTH," ")
	elif style==3:
		message = message.rjust(self.LCD_WIDTH," ")
     
	self.lcd_byte(line, self.LCD_CMD)
     
	for i in range(self.LCD_WIDTH):
		self.lcd_byte(ord(message[i]),self.LCD_CHR)

