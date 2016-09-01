/*GSM + RFID with flag*/

#include <SoftwareSerial.h>
#include <LiquidCrystal.h>
#include <AddicoreRFID.h>
#include <EEPROM.h>
#include <SPI.h>

/*---------------------------------------*/
#define RS A0
#define E A1
#define D4 A2
#define D5 A3
#define D6 A4
#define D7 A5
#define solePin 2
#define startButton 5
#define stopButton 6
#define GPRS_Tx 8
#define GPRS_Rx 7
#define GPRS_Pin 9
#define SCK 13
#define MISO 12
#define MOSI 11
#define chipSelectPin 10


#define timerOff TIMSK1|=(1 << OCIE1A)
#define timerOn TIMSK1=0
#define	uchar	unsigned char
#define	uint	unsigned int
/*---------------------------------------*/
LiquidCrystal lcd(RS, E, D4, D5, D6, D7);
SoftwareSerial GPRS(GPRS_Rx, GPRS_Tx);
AddicoreRFID myRFID;
/*---------------------------------------*/
int timeConsumed = 0.0;
float calibrationFactor = 7.5;
volatile long pulseCount = 0;
unsigned long totalMilliLitres = 0;
int answer = 0;
char response[100];
//long tagValue = 0;
bool flag = false;
const short maxTags = 200;
const short perCardStorage = 4;
bool quotaFlag = true;

byte flowmeterInterrupt = 1;  // 0 = digital pin 2
byte flowmeterPin       = 3;

/*------------------------------------------------------*/
void setup()
{
  delay(100);
  GPRS.begin(9600);
  lcd.begin(20, 4);
  SPI.begin();
  myRFID.AddicoreRFID_Init();
  /*-----------------------------*/
  pinMode(GPRS_Pin, OUTPUT);
  pinMode(chipSelectPin, OUTPUT);             // Set digital pin 10 as OUTPUT to connect it to the RFID /ENABLE pin
  digitalWrite(chipSelectPin, LOW);         // Activate the RFID readers
  pinMode(startButton, INPUT);
  pinMode(stopButton, INPUT);
  pinMode(solePin, OUTPUT);
  pinMode(flowmeterPin, INPUT);
  /*-----------------------------*/
  setupGPRS();
  timerSetup();
  /*-----------------------------*/
  pulseCount        = 0;
  totalMilliLitres  = 0;

  /*-----------------------------*/
  digitalWrite(flowmeterPin, HIGH);
  /*-----------------------------*/
  resetLCD();
}

/*------------------------------------------------------*/
void loop ()
{
  long tagValue = 0;
  while ( ! tagValue  )
    tagValue = readCard();
  if (authenticate(tagValue))
  {
    buttonControls();
    delay(1000);
    calculateFlow();
    Transaction(tagValue);
  }
  delay(2000);
  resetAll();
  delay(1000);
}

/*------------------------------------------------------*/
bool authenticate(long tagValue)
{
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Welcome.");
  lcd.setCursor(0, 1);
  long ATMCode = 3110333107;
  if (compareTag(tagValue))
  {
    return true;
  }
  else
  {
    quotaFlag = false;
    lcd.print("Please Wait....");
    if (authenRequest(tagValue, ATMCode))
    {
      if (quotaFlag == true)
      {
        writeTag2EEPROM(tagValue);       /*  Store Card in Local EEPROM   */
        return true;
      }
      else if (quotaFlag == false)
      {
        lcd.setCursor(0, 1);
        lcd.print("Please Recharge     ");
        lcd.setCursor(0, 2);
        lcd.print("Your Card");
        return false;
      }
    }
    else
    {
      lcd.setCursor(0, 1);
      lcd.print("Please Scan         ");
      lcd.setCursor(0, 2);
      lcd.print("Authorized Card     ");
      return false;
    }
  }
}

/*---------------------------------------*/
void Transaction(long tagValue)
{
  if (totalMilliLitres > 100 )
  {
    sendTransaction(tagValue, (long)3110333107, totalMilliLitres);
    if (quotaFlag == false)
      deleteTagFromEEPROM(tagValue);
  }
}

/*---------------------------------------*/
void calculateFlow()
{
  timerOff;
  detachInterrupt(flowmeterPin);
  readFlowmeter();
  totalMilliLitres = totalMilliLitres + (totalMilliLitres * 0.18);
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Total Water :");
  lcd.print(totalMilliLitres);
  lcd.setCursor(0, 1);
  lcd.print("Uploading Data......");
}

void readFlowmeter()
{
  float flowRate = pulseCount / calibrationFactor;
  pulseCount = 0;
  unsigned int flowMilliLitres = (flowRate / 60) * 1000;      /*Converting (L/min) to (mL/sec)*/
  totalMilliLitres += flowMilliLitres;          /*Total Liquid passed through the Sensor*/
/*
  lcd.setCursor(0,3);
  lcd.print("Amount: ");
  lcd.print(totalMilliLitres);
  */
    // Print the cumulative total of litres flowed since starting
}

/*---------------------------------------*/
void buttonControls()
{
  lcd.clear();
  lcd.print("Card Registered.    ");
  lcd.setCursor(0, 1);
  lcd.print("Press Green Button  ");
  lcd.setCursor(0, 2);
  lcd.print("To Start.           ");

  while (digitalRead(startButton));
  attachInterrupt(flowmeterInterrupt, pulseCounter, FALLING);
  timerOn;
  Solenoid(true);
  delay(100);
  lcd.setCursor(0, 1);
  lcd.print("Press RED Button.   ");
  lcd.setCursor(0, 2);
  lcd.print("To STOP.            ");
  while (digitalRead(stopButton));
  Solenoid(false);
}

/*---------------------------------------*/
void Solenoid(bool state)
{
  if (state == true)
    digitalWrite(solePin, HIGH);
  else if (state == false)
    digitalWrite(solePin, LOW);
  delay(200);
}

/*---------------------------------------*/
void timerSetup()
{
  // initialize timer1
  //  noInterrupts();           // disable all interrupts
  TCCR1A = 0;// set entire TCCR1A register to 0
  TCCR1B = 0;// same for TCCR1B
  TCNT1  = 0;//initialize counter value to 0
  // set compare match register for 1hz increments
  OCR1A = 15624;                          // = (16*10^6) / (time*1024) - 1 (must be <65536)
  //  OCR1A = 7812;
  TCCR1B |= (1 << WGM12);                 //turn on CTC mode
  TCCR1B |= (1 << CS12) | (1 << CS10);    //Set CS12 and CS10 bits for 1024 prescaler
  //TIMSK1 |= (1 << OCIE1A);                //enable timer compare interrupt
}

/*---------------------------------------*/
long readCard()
{

  long Value;
  uchar status;
  uchar str[16];
  str[1] = 0x4400;
  //Find tags, return tag type
  status = myRFID.AddicoreRFID_Request(PICC_REQIDL, str);
  if (! (status == MI_OK))
    return 0;
  status = myRFID.AddicoreRFID_Anticoll(str);
  if (status == MI_OK)
  {
    Value = 0;
    for (byte i = 0; i < 4; i++) {
      Value = (Value << 8) + str[i];
    }
    return Value;
  }
  else
    return 0;
  //  myRFID.AddicoreRFID_Halt();		   //Command tag into hibernation
}

bool compareTag(long tagValue)
{
  for (int i = 0; i < maxTags; i++)
  {
    if (tagValue == readTagFromEEPROM(i))
      return true;
  }
  return false;
}

/*---------------------------------------*/
void deleteTagFromEEPROM(long tagValue)
{
  for (int i = 0; i < maxTags; i++)
  {
    if (tagValue == readTagFromEEPROM(i))
    {
      for (int j = 0; j < perCardStorage ; j++)
        EEPROM.write( i + j, 255);
      return;
    }
  }
}

/*---------------------------------------*/
void printEEPROM()
{
  for (int i = 0; i < 250 ; i++);
  //Serial.println(readTagFromEEPROM(i), HEX);
}
/*---------------------------------------*/
long readTagFromEEPROM(int address)
{
  long tagValue = 0;
  int j = 0;
  for (j = 0; j < perCardStorage; j++)
  {
    tagValue = (tagValue << 8) + EEPROM.read(j + (address * perCardStorage));
  }
  return tagValue;
}

/*---------------------------------------*/
void writeTag2EEPROM(long tagValue)
{
  int address = checkEmptyEEPROMAddress();
  int j = 0;
  if (address == -1)
    return;
  for (int i = ((address * perCardStorage) + 3); i >= address * perCardStorage; i--)
  {
    EEPROM.write( i, (tagValue >> (j * 8)) & 255);
    j++;
  }
}

/*---------------------------------------*/
int memoryEEPROM()
{
  int Stored = 0;
  long value = 0;
  int i = 0, j = 0;
  for (i = 0; i < maxTags; i++)
  {
    readTagFromEEPROM(i);
    if (value != 0xFFFFFFFF)
    {
      Stored++;
    }
  }
  return Stored;
}

/*---------------------------------------*/
int checkEmptyEEPROMAddress()
{
  long value = 0;
  int i = 0, j = 0;
  for (i = 0; i < maxTags; i++)
  {
    for (j = 0; j < perCardStorage; j++)
    {
      value = (value << 8) + EEPROM.read(j + (i * perCardStorage));
    }
    if (value == 0xFFFFFFFF)
    {
      return (i);
    }
  }
  return -1;
}

/*---------------------------------------*/
void resetAll()
{
  detachInterrupt(flowmeterInterrupt);
  timerOff;
  timeConsumed = 0;
  pulseCount = 0;
  totalMilliLitres = 0;
  quotaFlag = true;
  flag = false;
  resetLCD();
}

/*---------------------------------------*/
void resetLCD()
{
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Welcome.");
  lcd.setCursor(0, 1);
  lcd.print("Please Scan Card.");
}

/*---------------------------------------*/
void setupGPRS()
{
  lcd.clear();
  lcd.print("Please Wait.");
  lcd.setCursor(0, 1);
  lcd.print("Configuring.");
  powerOn();
  while (sendATcommand("AT", "Call Ready", 20000) == 0);
  //sendATcommand("", "Call Ready", 5000);
  sendATcommand("ATE0", "OK", 1000);
  sendATcommand("AT+IPR=9600", "OK", 1000);
  sendATcommand("AT+CMGF=1", "OK", 100);
  while (sendATcommand("AT+CSTT=\"ntnet\"", "OK", 2000) == 0 );
  while (sendATcommand("AT+CIICR", "OK", 5000) == 0);
  sendATcommand("AT+CIFSR", ".", 2000);
  sendATcommand("AT+CIFSR=?", "OK", 2000);
  sendATcommand("AT+CDNSCFG=\"8.8.8.8\",\"8.8.4.4\"", "OK", 2000);
  sendATcommand("AT+CGATT=1", "OK", 5000);
  sendATcommand("AT+SAPBR=3,1,\"CONTYPE\",\"GPRS\"", "OK", 2000);
  sendATcommand("AT+SAPBR=3,1,\"APN\",\"ntnet\"", "OK", 2000);
  sendATcommand("AT+SAPBR=1,1", "OK", 5000);
  sendATcommand("AT+HTTPINIT", "OK", 4000);
}

/*---------------------------------------*/
bool authenRequest(long tagValue, long ATMCode)
{
  sendATcommand("AT+SAPBR=1,1", "OK", 5000);
  sendATcommand("AT+HTTPINIT", "OK", 4000);
  bool flag = false;
  char URL[] = "http://immunization.ipal.itu.edu.pk/index.php/ApiEngine/Auth?";
  httpSetParameter(URL, tagValue, ATMCode, 0);
  sendATcommand("AT+HTTPACTION=0", "+HTTPACTION:0,200,", 30000);
  delay(1000);
  sendATcommand("AT+HTTPREAD=0,100", "OK", 15000);
  if (strstr(response, "registered") != NULL)
  {
    if (strstr(response, "true") != NULL)
      quotaFlag = true;
    else if (strstr(response, "false") != NULL)
      quotaFlag = false;

    return true;
  }
  else if (strstr(response, "unregistered") != NULL)
  {
    return false;
  }
}

/*---------------------------------------*/
void sendTransaction(long tagValue, long ATMCode, long waterAmount)
{
  sendATcommand("AT+SAPBR=1,1", "OK", 2000);
  sendATcommand("AT+HTTPINIT", "OK", 2000);
  char URL[] = "http://immunization.ipal.itu.edu.pk/index.php/ApiEngine/IPushdata?";
  httpSetParameter(URL, tagValue, ATMCode, waterAmount);
  sendATcommand("AT+HTTPACTION=0", "+HTTPACTION:0,200,", 30000);
  sendATcommand("AT+HTTPREAD=0,100", "OK", 10000);
  if (strstr(response, "\"balance\":false") != NULL)
  {
    quotaFlag = false;
  }
  else if(strstr(response, "\"balance\":true") != NULL)
  {
    quotaFlag = true;
  }
}

/*---------------------------------------*/
void httpSetParameter(char URL[], long tagValue, long ATMCode, long waterAmount)
{
  char command[300];
  sprintf(command, "AT+HTTPPARA=\"URL\",\"%srfid=%lu&mcode=0%lu&amount=%i\"", URL, tagValue, ATMCode, waterAmount);
  sendATcommand(command, "OK", 1000);
}

/*---------------------------------------*/
void powerOn()
{
  digitalWrite(GPRS_Pin, LOW);
  delay(1000);
  digitalWrite(GPRS_Pin, HIGH);
  delay(2000);
  digitalWrite(GPRS_Pin, LOW);
  delay(2000);
}

/*---------------------------------------*/
void powerDown()
{
  sendATcommand("AT+CPOWD=1", "NORMAL POWER DOWN", 5000);
}

/*---------------------------------------*/
int sendATcommand(char* ATcommand, char* expected_answer1, unsigned int timeout)
{
  //  GPRS.begin(9600);
  unsigned int x = 0;
  answer = 0;
  unsigned long previous;
  memset(response, '\0', 100);    // Initialize the string
  delay(1000);
  while ( GPRS.available() > 0) GPRS.read();   // Clean the input buffer
  GPRS.write(ATcommand);    // Send the AT command
  GPRS.println();
  previous = millis();
  do {
    if (GPRS.available() != 0) {
      while (GPRS.available())
      {
        response[x] = GPRS.read();
        x++;
      }
    }
    if (strstr(response, expected_answer1) != NULL)
    {
      answer = 1;
    }
    else
      answer = 0;
  }
  while ((answer == 0) && ((millis() - previous) < timeout));
  if((millis() - previous) > timeout)
    answer= 2;
  if (GPRS.available())
  {
    while (GPRS.available())
    {
      response[x] = GPRS.read();
      x++;
    }
  }
  return answer;
}


/*-------------------| Interrups Routine Functions |----------------------*/

ISR(TIMER1_COMPA_vect)          // timer compare interrupt service routine
{
  //    digitalWrite(ledPin, digitalRead(ledPin) ^ 1);   // toggle LED pin
  //    flowRate = ((1000.0 / (millis() - oldTime)) * pulseCounter) / calibrationFactor;
  readFlowmeter();
  /*Initialize Interrupt Again*/
}

/*------------------------------------------------------*/
void pulseCounter()
{
  /*Insterrupt Service Routine*/
  pulseCount++;
}
