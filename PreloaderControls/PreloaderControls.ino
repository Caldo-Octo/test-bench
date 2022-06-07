char inputChar;
const int enaPin = 2; 
const int stepPin = 4; 
const int dirPin = 3; 

const int enaPin2 = 11; 
const int stepPin2 = 13; 
const int dirPin2 = 12; 

const int relay1 = 8; 
const int relay2 = 9; 
int speedconst = 20; 
long int timeconst = 10000; 

#include "HX711.h"

#define DOUT  6
#define CLK  7

HX711 scale;

float calibration_factor = 450; 
void setup() {
  // put your setup code here, to run once:
   Serial.begin(9600);
   pinMode(relay1, OUTPUT);
   pinMode(relay2, OUTPUT);
   pinMode(stepPin, OUTPUT); //pulse
   pinMode(dirPin, OUTPUT); //direction
   pinMode(enaPin, OUTPUT); //ena
   pinMode(stepPin2, OUTPUT); //pulse
   pinMode(dirPin2, OUTPUT); //direction
   pinMode(enaPin2, OUTPUT); //ena

   scale.begin(DOUT, CLK);
   scale.set_scale();
   scale.tare(); //Reset the scale to 0
   long zero_factor = scale.read_average(); //Get a baseline reading

}

void loop() {
  // put your main code here, to run repeatedly:
  if (Serial.available() > 0) {
    inputChar = Serial.read();
  }
  delay(100);
    switch (inputChar) {
      case 0:
        /* No new data was recieved */
        break;
      case 'z':
        //Loadcell Read
        Serial.print(scale.get_units(), 1);
      case 'x':
        //Dispense X amount 
        //Slider Close
        digitalWrite(relay1,HIGH);
        digitalWrite(relay2,LOW);
        scale.tare();
        if (scale.read_average(20) < 112) {
          step_forward(42, dirPin2, enaPin2, stepPin2, 5000);
        }
        //Sldier Open
        digitalWrite(relay1,HIGH);
        digitalWrite(relay2,LOW);
        delay(200);
        //Slider Close
        digitalWrite(relay1,HIGH);
        digitalWrite(relay2,LOW);
        
        break;
      case 'd':
        //Double auger move
        double_step(speedconst, dirPin, enaPin, stepPin,dirPin2, enaPin2, stepPin2, timeconst);
        break;
      case '-':
        //Decrease speed by 5
        speedconst = speedconst + 5;
        Serial.println(" SPEED IS NOW ");
        Serial.println(speedconst);
        break;
      case '+':
        //Increase speed by 5
        speedconst = speedconst - 5;
        Serial.println(" SPEED IS NOW ");
        Serial.println(speedconst);
        break;
      case 'n':
        //INCREASE SPIN TIME BY 1 sec
        timeconst = timeconst + 10000;
        Serial.println(" SPIN TIME IS NOW ");
        Serial.println(timeconst);
        break;
      case 'm':
        //DECREASE SPIN TIME BY 1 sec
        timeconst = timeconst - 10000;
        Serial.println(" SPIN TIME IS NOW ");
        Serial.println(timeconst);
        break;
      case 'q':
        //Motor dispense 1s
        //20 is a good speed
        step_forward(speedconst, dirPin2, enaPin2, stepPin2, timeconst);
        break;
      case 'r':
      //Motor reverse 1s
        step_backward(speedconst, dirPin2, enaPin2, stepPin2, timeconst);
        break;
      case 'c':
      //spin 2s then slider open close open close
        step_forward(speedconst, dirPin, enaPin, stepPin, timeconst);
        digitalWrite(relay2,HIGH);
        digitalWrite(relay1,LOW);
        delay(500);
        digitalWrite(relay1,HIGH);
        digitalWrite(relay2,LOW);
        delay(500);
        digitalWrite(relay2,HIGH);
        digitalWrite(relay1,LOW);
        delay(500);
        digitalWrite(relay1,HIGH);
        digitalWrite(relay2,LOW);
        break;
      case 'p':
         //slider open close open close
        digitalWrite(relay2,HIGH);
        digitalWrite(relay1,LOW);
        delay(500);
        digitalWrite(relay1,HIGH);
        digitalWrite(relay2,LOW);
      case 'f':
       //slider to the front
        digitalWrite(relay1,HIGH);
        digitalWrite(relay2,LOW);
        break;
      case 'g':
       //slider to the back
        digitalWrite(relay2,HIGH);
        digitalWrite(relay1,LOW);
        break;
      case 'o':
       //Both relays on (turns suction off)
        digitalWrite(relay2,HIGH);
        digitalWrite(relay1,HIGH);
        break;
      case 'l':
      //Both relays off (turns suction on)
        digitalWrite(relay2,LOW);
        digitalWrite(relay1,LOW);
        break;
      case 't':
      //slider open then spin 2s then slider close
        digitalWrite(relay2,HIGH);
        digitalWrite(relay1,LOW);
        delay(300);
        step_forward(speedconst, dirPin, enaPin, stepPin, timeconst);
        delay(300);
        digitalWrite(relay1,HIGH);
        digitalWrite(relay2,LOW);
        break;
    }
    
}

void step_forward(int spe, int dir, int ena, int pul, long int num ) {
  digitalWrite(dir,HIGH);
  digitalWrite(ena,LOW);
  for (long int i = 0; i < num; i++)
  {
    digitalWrite(pul,HIGH); 
    delayMicroseconds(spe); 
    digitalWrite(pul,LOW); 
    delayMicroseconds(spe); 
  }
   
   Serial.println(" Stepped Forward ");

}

void double_step(int spe, int dir, int ena, int pul,int dir2, int ena2, int pul2, long int num ) {
  digitalWrite(dir,LOW);
  digitalWrite(ena,LOW);
  digitalWrite(dir2,LOW);
  digitalWrite(ena,LOW);
  for (long int i = 0; i < num; i++)
  {
    digitalWrite(pul,HIGH);
    digitalWrite(pul2,HIGH);  
    delayMicroseconds(spe); 
    digitalWrite(pul,LOW);
    digitalWrite(pul2,LOW);  
    delayMicroseconds(spe); 
  }
   

}

void step_backward(int spe, int dir, int ena, int pul, long int num ) {
  digitalWrite(dir,LOW);
  digitalWrite(ena,LOW);
  for (int i = 0; i < num; i++)
  {
    digitalWrite(pul,LOW); 
    delayMicroseconds(spe); 
    digitalWrite(pul,HIGH); 
    delayMicroseconds(spe); 
  }
  // digitalWrite(ena,HIGH); 
   Serial.println(" Stepped Back ");
} 
