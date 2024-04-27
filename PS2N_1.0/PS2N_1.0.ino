#include <OneWire.h>
#include <DallasTemperature.h>
#include <EEPROM.h>
#include <RTClib.h>

#define ce_pin 2
#define sck_pin 5
#define io_pin 4

#define ONE_WIRE_BUS 8
#define internalLedPin 13
#define waterSensorPin A0

const int waterThreshold = 400; 
bool inundatieDetectata = false;

OneWire oneWire(ONE_WIRE_BUS);

DallasTemperature sensors(&oneWire);

DS1302 rtc(ce_pin, sck_pin, io_pin);
char buf[20];

bool scheduleSet = false; // Variabilă de stare pentru programul setat
int onHour = 0;
int onMinute = 0;
int offHour = 0;
int offMinute = 0;
int currentHour = 0;
int currentMinute = 0;

const int maxMessages = 10;
const int messageSize = 2; // Dimensiunea fiecărui mesaj (A sau S)

String messages[maxMessages]; // Array pentru stocarea mesajelor
int messageCount = 0; // Contor pentru numărul de mesaje stocate

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
 //digitalWrite(internalLedPin, LOW);
  rtc.begin();
  rtc.adjust(DateTime(F(__DATE__), F(__TIME__)));

  for (int i = 0; i < maxMessages; i++) {
    messages[i] = readStringFromEEPROM(i * messageSize);
    // Serial.print("Message ");
    // Serial.print(i);
    // Serial.print(": ");
    // Serial.println(messages[i]);
  }

  // // Se afișează ultimul mesaj pentru a fi tratat ca stare inițială a LED-ului
  // Serial.print("Last Message: ");
  // Serial.println(messages[maxMessages - 1]);

  if (messages[maxMessages - 1] == "A") {
    digitalWrite(internalLedPin, HIGH);
  }
}

void loop(void){ 
  DateTime now = rtc.now();
  currentHour = now.hour();
  
   // Formatare minute sa inceapa cu 0 daca minutul e mai mic de 10 ( ex: in loc de timpul: 238 sa afiseze 2308)
  char formattedMinutes[3];
  sprintf(formattedMinutes, "%02d", now.minute());

  Serial.print("\n");
  Serial.print(currentHour);
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

  // Verificarea ciclică a programului setat
  if (scheduleSet) {
    // Verificăm dacă este momentul de aprindere
    if (currentHour == onHour && currentMinute == onMinute) {
      digitalWrite(internalLedPin, HIGH);
      //Serial.println("LED-ul a fost aprins.");
    } 
    // Verificăm dacă este momentul de stingere
    else if (currentHour == offHour && currentMinute == offMinute) {
      digitalWrite(internalLedPin, LOW);
      //Serial.println("LED-ul a fost stins.");
      scheduleSet = false;
    }
  }

  // Verificăm dacă există date disponibile pe portul serial
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

      // Actualizăm variabilele globale pentru programul setat
      onHour = input.substring(0, 2).toInt();
      onMinute = input.substring(3, 5).toInt();
      offHour = input.substring(6, 8).toInt();
      offMinute = input.substring(9, 11).toInt();

      // Afișăm programul setat în consola serială
      Serial.print("\nProgram setat: Pornire la ");
      Serial.print(onHour);
      Serial.print(":");
      Serial.print(onMinute);
      Serial.print(", Stingere la ");
      Serial.print(offHour);
      Serial.print(":");
      Serial.println(offMinute);

      scheduleSet = true; // Setăm variabila de stare la true
    }
  }
 delay(100);
}
