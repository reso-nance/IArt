static const unsigned int startButtonPin = 2;
static const unsigned int maxRate = 20; // in millis

struct potentiometer {
  String name;
  unsigned int pin;
  unsigned int lastValue;
  unsigned int currentValue;
  unsigned int deadBand;
};

potentiometer pot1 = {"potA", 1, 0, 0, 5};
potentiometer pot2 = {"potB", 2, 0, 0, 5};
potentiometer pot3 = {"potC", 3, 0, 0, 5};

potentiometer allPots[] = {pot1, pot2, pot3};
unsigned int potCount = sizeof(allPots)/sizeof(potentiometer);
bool startButtonStatus;

void setup() {
  pinMode(startButtonPin, INPUT_PULLUP);
  for (unsigned int i=0; i<potCount; i++) {
    allPots[i].currentValue = analogRead(allPots[i].pin);
  }
  startButtonStatus = digitalRead(startButtonPin);
  
  Serial.begin(115200);
  Serial.println("connected, "+String(potCount)+" potentiometers connected");
}

void loop() {
  
  for (unsigned int i=0; i<potCount; i++) {
    allPots[i].currentValue = analogRead(allPots[i].pin);
    if (allPots[i].lastValue < allPots[i].currentValue - allPots[i].deadBand || allPots[i].lastValue > allPots[i].currentValue + allPots[i].deadBand) {
      Serial.println(allPots[i].name + ":"+ String(allPots[i].currentValue));
      delay(maxRate);
    }
    allPots[i].lastValue = allPots[i].currentValue;
  }

  bool currentStartButtonStatus = digitalRead(startButtonPin);
  if ( currentStartButtonStatus == LOW && startButtonStatus == HIGH) {
    Serial.println("start");
    startButtonStatus = currentStartButtonStatus;
    delay(maxRate);
  }
  
  delay(5);
}
