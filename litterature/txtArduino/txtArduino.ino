static const unsigned int maxRate = 20; // in millis

struct analog {
  String name;
  unsigned int pin;
  unsigned int calibMin;
  unsigned int calibMax;
  unsigned int lastValue;
  unsigned int currentValue;
  unsigned int deadBand;
};
analog analogs[] = { {"potA", 1, 0, 1023, 0, 0, 5}, {"potB", 2, 0, 1023, 0, 0, 5}, {"potC", 3, 0, 1023, 0, 0, 5} };
unsigned int analogsCount = sizeof(analogs)/sizeof(analog);


struct digital {
  String name;
  unsigned int pin;
  bool inverted;
  bool pullup;
  bool lastState;
  unsigned int debounce;
  long lastTriggered;
};

digital digitals[] = { {"start", 3, false, true, true, 20, 0}, {"prevA", 4, true, false, false, 20, 0}, {"nextA", 5, true, false, false, 20, 0}, {"prevB", 6, true, false, false, 20, 0},
                       {"nextB", 7, true, false, false, 20, 0}, {"prevC", 8, true, false, false, 20, 0}, {"nextC", 9, true, false, false, 20, 0} };
unsigned int digitalsCount = sizeof(digitals)/sizeof(digital);

void setup() {
  // setting up the digital inputs
  for (unsigned int i=0; i<digitalsCount; i++){
    if (digitals[i].pullup) pinMode(digitals[i].pin, INPUT_PULLUP);
    else pinMode(digitals[i].pin, INPUT);
    digitals[i].lastState = digitalRead(digitals[i].pin);
  }
  // setting up the analog inputs
  for (unsigned int i=0; i<analogsCount; i++) {
    analogs[i].currentValue = analogRead(analogs[i].pin);
  }
  
  Serial.begin(115200);
  Serial.println("connected, "+String(analogsCount)+" analog inputs and "+String(digitalsCount)+" digital inputs configured");
}

void loop() {

//  Reading analog inputs
  for (unsigned int i=0; i<analogsCount; i++) {
    analogs[i].currentValue = analogRead(analogs[i].pin);
    analogs[i].currentValue = map(analogs[i].currentValue, analogs[i].calibMin,  analogs[i].calibMax, 0, 1023);
    if (analogs[i].lastValue < analogs[i].currentValue - analogs[i].deadBand || analogs[i].lastValue > analogs[i].currentValue + analogs[i].deadBand) {
      Serial.println(analogs[i].name + ":"+ String(analogs[i].currentValue));
      delay(maxRate);
    }
    analogs[i].lastValue = analogs[i].currentValue;
  }

//  Reading digital inputs
  for (unsigned int i=0; i<digitalsCount; i++) {
    bool currentState = digitalRead(digitals[i].pin);
    // input has been pulled LOW
    if (currentState == LOW && digitals[i].lastState == HIGH && millis() - digitals[i].lastTriggered > digitals[i].debounce) {
      if (!digitals[i].inverted) Serial.println(digitals[i].name+":ON");
      else Serial.println(digitals[i].name+":OFF");
      digitals[i].lastTriggered = millis();
    }
    // input has been pulled HIGH
    if (currentState == HIGH && digitals[i].lastState == LOW && millis() - digitals[i].lastTriggered > digitals[i].debounce) {
      if (!digitals[i].inverted) Serial.println(digitals[i].name+":OFF");
      else Serial.println(digitals[i].name+":ON");
      digitals[i].lastTriggered = millis();
    }
    digitals[i].lastState = currentState;
  }
  
  delay(5);
}
