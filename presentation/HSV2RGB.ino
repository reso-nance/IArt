int RGB[3];
int redPin = 9;
int greenPin = 10;
int bluePin = 11;

void setup() {
  Serial.begin(9600);
  pinMode(redPin, OUTPUT);
  pinMode(greenPin, OUTPUT);
  pinMode(bluePin, OUTPUT);
  sendHSV(0, 0, 0); // luminosité de 0 = éteint les LEDs

}

void loop() {

  // Merci pour l'artiste, je passerais avec un chapeau à la pause
  Serial.println("Fondu en ouverture");
  for (int luminosite = 0; luminosite < 256; luminosite++) { // fade in
    sendHSV(0, 255, luminosite);
    delay(5);
  }
  delay(1000); Serial.println("cycle couleurs");
  for (int teinte = 0; teinte < 256; teinte++) { // cycle les couleurs
    sendHSV(teinte, 255, 255);
    delay(10);
  }
  delay(1000); Serial.println("désature");
  for (int saturation = 255; saturation > 0; saturation--) { // désature
    sendHSV(255, saturation, 255);
    delay(5);
  }
  delay(800); Serial.println("fade out");
  for (int luminosite = 255; luminosite >= 0; luminosite--) { // fade out rapide
    sendHSV(255, 0, luminosite);
    delay(1);
  }
  delay(1500); Serial.println("blitz");
  for (int compteur = 20; compteur >= 0; compteur--) {
    sendHSV(25 * compteur, 255, 25 * compteur);
    delay(10 * compteur);
    sendHSV(25 * compteur, 255, 0);
    delay(30 * compteur);
  }
  delay(3000);

}

void sendHSV(int hue, int sat, int val) {
  hue = map(hue, 0,255,0,259);
  setRGB(hue, sat, val, RGB);
  Serial.print("R="); Serial.print(RGB[0], DEC); Serial.print(" G="); Serial.print(RGB[1], DEC); Serial.print(" B="); Serial.println(RGB[2], DEC);
  analogWrite(redPin, 255-RGB[0]);
  analogWrite(greenPin,255- RGB[1]);
  analogWrite(bluePin, 255-RGB[2]);
}

void setRGB(int hue, int sat, int val, int colors[3]) {
  // hue: 0-259, sat: 0-255, val (lightness): 0-255
  int r, g, b, base;
  if (sat == 0) { // Achromatic color (gray).
    colors[0] = val;
    colors[1] = val;
    colors[2] = val;
  } else  {
    base = ((255 - sat) * val) >> 8;
    switch (hue / 60) {
      case 0:
        r = val;
        g = (((val - base) * hue) / 60) + base;
        b = base;
        break;
      case 1:
        r = (((val - base) * (60 - (hue % 60))) / 60) + base;
        g = val;
        b = base;
        break;
      case 2:
        r = base;
        g = val;
        b = (((val - base) * (hue % 60)) / 60) + base;
        break;
      case 3:
        r = base;
        g = (((val - base) * (60 - (hue % 60))) / 60) + base;
        b = val;
        break;
      case 4:
        r = (((val - base) * (hue % 60)) / 60) + base;
        g = base;
        b = val;
        break;
      case 5:
        r = val;
        g = base;
        b = (((val - base) * (60 - (hue % 60))) / 60) + base;
        break;
    }
    colors[0] = r;
    colors[1] = g;
    colors[2] = b;
  }
}
