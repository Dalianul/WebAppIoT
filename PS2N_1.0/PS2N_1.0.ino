#include <OneWire.h>
#include <DallasTemperature.h>
#include <EEPROM.h>
#include <RTClib.h>

#define ce_pin 2  //chip enable 
#define sck_pin 5 // serial clock
#define io_pin 4  //input/output pin

#define ONE_WIRE_BUS 8 //pin pentru senzor temperatura 
#define internalLedPin 13 //pin led intern de pe placuta 
#define waterSensorPin A0 //pin pentru senzorul de temperatura 

const int waterThreshold = 200; 
bool inundatieDetectata = false;

OneWire oneWire(ONE_WIRE_BUS);

DallasTemperature sensors(&oneWire);

DS1302 rtc(ce_pin, sck_pin, io_pin);
char buf[20];

bool scheduleSet = false;
int onHour = 0;
int onMinute = 0;
int offHour = 0;
int offMinute = 0;
int currentHour = 0;
int currentMinute = 0;

const int maxMessages = 10;
const int messageSize = 2;

String messages[maxMessages]; 
int messageCount = 0;

void writeStringToEEPROM(int addrOffset, const String &strToWrite)
{
  byte len = strToWrite.length();
  EEPROM.write(addrOffset, len);

  for (int i = 0; i < len; i++)
  {
    EEPROM.write(addrOffset + 1 + i, strToWrite[i]);
  }
}

String readStringFromEEPROM(int addrOffset)
{
  int newStrLen = EEPROM.read(addrOffset);
  char data[newStrLen + 1];

  for (int i = 0; i < newStrLen; i++)
  {
    data[i] = EEPROM.read(addrOffset + 1 + i);
  }
  data[newStrLen] = '\0';

  return String(data);
}

void setup(void)
{
  Serial.begin(9600);
  sensors.begin();
  pinMode(internalLedPin, OUTPUT);
  rtc.begin();
  rtc.adjust(DateTime(F(__DATE__), F(__TIME__)));

  for (int i = 0; i < maxMessages; i++) {
    messages[i] = readStringFromEEPROM(i * messageSize);
  }

  if (messages[maxMessages - 1] == "A") {
    digitalWrite(internalLedPin, HIGH);
  }
}

void loop(void){ 
  DateTime now = rtc.now();
  currentHour = now.hour();
  currentMinute = now.minute();
  
  // Formatare minute sa inceapa cu 0 daca minutul e mai mic de 10 ( ex: in loc de timpul: 238 sa afiseze 2308)
  char formattedMinutes[3];
  sprintf(formattedMinutes, "%02d", now.minute());

  // Formatare ora să înceapă cu 0 dacă ora e mai mică de 10 și să aibă două cifre
  char formattedHour[3];
  sprintf(formattedHour, "%02d", now.hour());

  Serial.print("\n");
  Serial.print(formattedHour);
  Serial.print(formattedMinutes);
  sensors.requestTemperatures(); 
  Serial.print("\nTemperatura celsius: ");
  Serial.print(sensors.getTempCByIndex(0));
  int waterSensorValue = analogRead(waterSensorPin);
 

  if (waterSensorValue > waterThreshold && !inundatieDetectata) {
    Serial.print("\n");
    Serial.print("Inundatie detectata!");
    inundatieDetectata = true;
  }

  if (waterSensorValue < waterThreshold && inundatieDetectata) {
    inundatieDetectata = false;
  }

  if (scheduleSet) {
    if (currentHour == onHour && currentMinute == onMinute) {
      digitalWrite(internalLedPin, HIGH);
    } 
    else if (currentHour == offHour && currentMinute == offMinute) {
      digitalWrite(internalLedPin, LOW);
      scheduleSet = false;
    }
  }

  if (Serial.available() > 0) {
    String input = Serial.readStringUntil('\n');
    if (input == "A" || input == "S") {
      // Se adaugă noul mesaj la începutul listei
      for (int i = 0; i < maxMessages - 1; i++) {
        messages[i] = messages[i + 1];
      }

      messages[9] = input;

      for (int i = 0; i < maxMessages; i++) {
        writeStringToEEPROM(i * messageSize, messages[i]);
      }
    }
    if (input == "A") {
      digitalWrite(internalLedPin, HIGH);
      scheduleSet = false;
    } 
    else if (input == "S") {
      digitalWrite(internalLedPin, LOW);
      scheduleSet = false;
    }
    else if (input.startsWith("SET_SCHEDULE")) {
      input.remove(0, 12); // Elimină "SET_SCHEDULE" de la început

      onHour = input.substring(0, 2).toInt();
      onMinute = input.substring(3, 5).toInt();
      offHour = input.substring(6, 8).toInt();
      offMinute = input.substring(9, 11).toInt();

      Serial.print("\nProgram setat: Pornire la ");
      Serial.print(onHour);
      Serial.print(":");
      Serial.print(onMinute);
      Serial.print(", Stingere la ");
      Serial.print(offHour);
      Serial.print(":");
      Serial.println(offMinute);

      scheduleSet = true;
    }
  }
 delay(100);
}
