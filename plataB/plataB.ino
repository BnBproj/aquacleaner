#include <TroykaCurrent.h>
#include <Wire.h>                  //импорт библиотек
ACS712 sensorA(A0);                //создание объекта сенсора
float pump = 0;
float delit = 0;                   //создание переменных
int req = 8;
int rec = 0;
long i = 0;
unsigned long Time;
void setup() {
  Serial.begin(9600);
  pinMode(9, OUTPUT);  //задача режима пина на реле
  Wire.begin(0x18);
  Wire.onRequest(requestEvent);
  Wire.onReceive(receiveEvent);    //открытие порта I2C
}
void requestEvent() {           //функция ответа на запрос
  Wire.write(req);
//  Serial.println(req);
}

void receiveEvent() {             //функция для приема данных
  rec = Wire.read();
  Serial.println(rec);
}

void loop() {                                             //цикл сравнивания команд и их выполнения
  pump = sensorA.readCurrentDC();
  delit = analogRead(A1) * 5 * (131.6 / 32.5) / 1024;
  if (pump < 0.8) {
    i = i + 0.1;
  }
  else {
    i = 0;
  }
  if (delit < 12.3) {
    req = 3;
    digitalWrite(9, 0);
  }
  if (i > 1000) {
    req = 2;
    digitalWrite(9, 0);
  }
  if (i < 1000 and delit > 12.3) {
    req = 8;
  }
  if (rec == 1) {
    digitalWrite(9, 1);
    rec = 0;
  }
  if (rec == 4) {
    digitalWrite(9, 0);
    rec = 0;
  }
  
}
