static const unsigned int maxRate = 20; // in millis

struct potentiometer {
  String name;
  unsigned int pin;
  unsigned int lastValue;
  unsigned int currentValue;
  unsigned int deadBand;
};
potentiometer allPots[] = {{"potA", 1, 0, 0, 5}, {"potB", 2, 0, 0, 5}, {"potC", 3, 0, 0, 5}};
unsigned int potCount = sizeof(allPots)/sizeof(potentiometer);


struct button {
  String name;
  unsigned int pin;
  bool lastState;
  unsigned int debounce;
  long lastTriggered;
};

button allButtons[] = {{"start", 2, true, 20, 0}, {"prevA", 3, true, 20, 0}, {"nextA", 4, true, 20, 0}, {"prevB", 5, true, 20, 0},
                        {"nextB", 6, true, 20, 0}, {"prevC", 7, true, 20, 0}, {"nextC", 8, true, 20, 0}};
unsigned int buttonCount = sizeof(allButtons)/sizeof(button);

void setup() {
  // setting up the buttons
  for (unsigned int i=0; i<buttonCount; i++){
    pinMode(allButtons[i].pin, INPUT_PULLUP);
    allButtons[i].lastState = digitalRead(allButtons[i].pin);
  }
  // setting up the potentiometers
  for (unsigned int i=0; i<potCount; i++) {
    allPots[i].currentValue = analogRead(allPots[i].pin);
  }
  
  Serial.begin(115200);
  Serial.println("connected, "+String(potCount)+" potentiometers and "+String(buttonCount)+" buttons connected");
}

void loop() {

//  Reading potentiometers
  for (unsigned int i=0; i<potCount; i++) {
    allPots[i].currentValue = analogRead(allPots[i].pin);
    if (allPots[i].lastValue < allPots[i].currentValue - allPots[i].deadBand || allPots[i].lastValue > allPots[i].currentValue + allPots[i].deadBand) {
      Serial.println(allPots[i].name + ":"+ String(allPots[i].currentValue));
      delay(maxRate);
    }
    allPots[i].lastValue = allPots[i].currentValue;
  }

//  Reading buttons
  for (unsigned int i=0; i<buttonCount; i++) {
    bool buttonState = digitalRead(allButtons[i].pin);
    // button has been pulled LOW
    if (buttonState == LOW && allButtons[i].lastState == HIGH && millis() - allButtons[i].lastTriggered > allButtons[i].debounce) {
      Serial.println(allButtons[i].name+":ON");
      allButtons[i].lastTriggered = millis();
    }
    // button has been pulled HIGH
    if (buttonState == HIGH && allButtons[i].lastState == LOW && millis() - allButtons[i].lastTriggered > allButtons[i].debounce) {
      Serial.println(allButtons[i].name+":OFF");
      allButtons[i].lastTriggered = millis();
    }
    allButtons[i].lastState = buttonState;
  }
  
  delay(5);
}
