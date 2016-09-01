byte sensorInterrupt = 0;  // 0 = digital pin 2
byte sensorPin       = 2;
/*
// The hall-effect flow sensor outputs approximately 4.5 pulses per second per
// litre/minute of flow.
float calibrationFactor = 7.5;
*/
volatile long pulseCount;  
/*
float flowRate;
unsigned int flowMilliLitres;
unsigned long totalMilliLitres;

unsigned long oldTime;
*/
/*--------------------------------------------------*/
void setup()
{
  Serial.begin(9600);
  pinMode(sensorPin, INPUT);
  pulseCount        = 0;
/*
  flowRate          = 0.0;
  flowMilliLitres   = 0;
  totalMilliLitres  = 0;
  oldTime           = 0;
*/
  // The Hall-effect sensor is connected to pin 2 which uses interrupt 0.
  // Configured to trigger on a FALLING state change (transition from HIGH
  // state to LOW state)
  attachInterrupt(sensorInterrupt, pulseCounter, FALLING);
}

/*--------------------------------------------------*/
void loop()
{
  if(Serial.available())
  {
    if(Serial.read() == 'Y')
    {
      Serial.println(pulseCount);
      pulseCount = 0;
    }
  }
//    detachInterrupt(sensorInterrupt);      /*Disable the interrupt for calculations*/
/*    
    // Because this loop may not complete in exactly 1 second intervals we calculate
    // the number of milliseconds that have passed since the last execution and use
    // that to scale the output. We also apply the calibrationFactor to scale the output
    // based on the number of pulses per second per units of measure (litres/minute in
    // this case) coming from the sensor.
    flowRate = ((1000.0 / (millis() - oldTime)) * pulseCount) / calibrationFactor;
    oldTime = millis();   
    
    flowMilliLitres = (flowRate / 60) * 1000;      //Converting (L/min) to (mL/sec)
    
    totalMilliLitres += flowMilliLitres;          //Total Liquid passed through the Sensor
      
    unsigned int frac;
    
    // Print the flow rate for this second in litres / minute
    Serial.print("Flow rate: ");
    Serial.print(int(flowRate));  // Print the integer part of the variable
    Serial.print(".");             // Print the decimal point
    // Determine the fractional part. The 10 multiplier gives us 1 decimal place.
    frac = (flowRate - int(flowRate)) * 10;
    Serial.print(frac, DEC) ;      // Print the fractional part of the variable
    Serial.print("L/min");
    // Print the number of litres flowed in this second
    Serial.print("  Current Liquid Flowing: ");             // Output separator
    Serial.print(flowMilliLitres);
    Serial.print("mL/Sec");

    // Print the cumulative total of litres flowed since starting
    Serial.print("  Output Liquid Quantity: ");             // Output separator
    Serial.print(totalMilliLitres);
    Serial.println("mL"); 
    */
    //if(pulseCount != 0 )
    //Serial.println(pulseCount); 
    /*Initialize Interrupt Again*/
    //pulseCount = 0;
    //attachInterrupt(sensorInterrupt, pulseCounter, FALLING);
}

/*------------------------------------------------------*/
void pulseCounter()
{
  /*Insterrupt Service Routine*/
  pulseCount++;      
}
