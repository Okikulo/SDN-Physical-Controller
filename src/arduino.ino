/*
 * SDN Controller - Arduino Side
 * Group 5 - Advanced Computer Networks
 *
 * Hardware:
 * - Button: Pin 2
 * - Joystick VRx: Pin A0
 * - Joystick VRy: Pin A1
 * - LED h1: Pin 5 (un solo LED)
 * - LED h2: Pin 6 (un solo LED)
 * - LED3 (RGB - switch): Pins 8(R), 9(G), 10(B)
 */

// ============ PIN DEFINITIONS ============
const int BUTTON1_PIN = 2;
const int JOY_SW_PIN = 4;

const int JOY_X_PIN = A0;
const int JOY_Y_PIN = A1;

// LEDs simples para hosts
const int LED_H1 = 5;
const int LED_H2 = 6;

// LED RGB para switch
const int LED3_RED = 11;
const int LED3_GREEN = 9;
const int LED3_BLUE = 10;

// ============ STATE VARIABLES ============
int lastButton1 = HIGH;
int lastJoyState = 0;           // 0=center, 1=up, 2=down, 3=left, 4=right
unsigned long lastTempRead = 0; // ADD THIS LINE
unsigned long debounceDelay = 50;

// Joystick thresholds
const int JOY_THRESHOLD_LOW = 400;
const int JOY_THRESHOLD_HIGH = 600;

// ============ SETUP ============
void setup() {
  Serial.begin(9600);

  pinMode(BUTTON1_PIN, INPUT_PULLUP);

  // LEDs simples
  pinMode(LED_H1, OUTPUT);
  pinMode(LED_H2, OUTPUT);

  // LED RGB
  pinMode(LED3_RED, OUTPUT);
  pinMode(LED3_GREEN, OUTPUT);
  pinMode(LED3_BLUE, OUTPUT);

  // Inicializar LEDs
  // h1 y h2 ON (conectados)
  digitalWrite(LED_H1, HIGH);
  digitalWrite(LED_H2, HIGH);

  // Switch verde (normal)
  setLED3(0, 255, 0);

  pinMode(JOY_SW_PIN, INPUT_PULLUP);

  Serial.println("READY");
}

// ============ MAIN LOOP ============
void loop() {
  readButton();
  readJoystick();
  readTemperature(); // Uncomment this
  readCommands();
  delay(10);
}

// ============ READ FUNCTIONS ============
void readTemperature() {
  if (millis() - lastTempRead > 2000) {
    // Simulated temperature between 23-27°C
    float tempC = 25.0 + random(-200, 200) / 100.0;

    Serial.print("TEMP:");
    Serial.println(tempC);

    lastTempRead = millis();
  }
}

void readButton() {
  int button1 = digitalRead(BUTTON1_PIN);
  if (button1 == LOW && lastButton1 == HIGH) {
    delay(debounceDelay);
    if (digitalRead(BUTTON1_PIN) == LOW) {
      Serial.println("BUTTON");
    }
  }
  lastButton1 = button1;
}

void readJoystick() {
  int xValue = analogRead(JOY_X_PIN);
  int yValue = analogRead(JOY_Y_PIN);

  int currentState = 0;

  // Detectar dirección
  if (yValue > JOY_THRESHOLD_HIGH) {
    currentState = 1; // UP
  } else if (yValue < JOY_THRESHOLD_LOW) {
    currentState = 2; // DOWN
  } else if (xValue < JOY_THRESHOLD_LOW) {
    currentState = 4; // LEFT
  } else if (xValue > JOY_THRESHOLD_HIGH) {
    currentState = 3; // RIGHT
  }

  // Solo enviar cuando cambia de estado
  if (currentState != lastJoyState) {
    if (currentState == 1) {
      Serial.println("JOY_UP");
    } else if (currentState == 2) {
      Serial.println("JOY_DOWN");
    } else if (currentState == 3) {
      Serial.println("JOY_LEFT");
    } else if (currentState == 4) {
      Serial.println("JOY_RIGHT");
    }
    lastJoyState = currentState;
  }
}

void readCommands() {
  if (Serial.available() > 0) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();

    // Comandos para LED h1 (pin 5)
    if (cmd == "LED1:RED") {
      // Rojo = desconectado = LED OFF (o parpadeo)
      digitalWrite(LED_H1, LOW);
    } else if (cmd == "LED1:GREEN") {
      // Verde = conectado = LED ON
      digitalWrite(LED_H1, HIGH);
    }

    // Comandos para LED h2 (pin 6)
    else if (cmd == "LED2:RED") {
      // Rojo = desconectado = LED OFF
      digitalWrite(LED_H2, LOW);
    } else if (cmd == "LED2:GREEN") {
      // Verde = conectado = LED ON
      digitalWrite(LED_H2, HIGH);
    }

    // Comandos para LED3 (RGB - switch)
    else if (cmd == "LED3:GREEN") {
      setLED3(0, 255, 0);
    } else if (cmd == "LED3:RED") {
      setLED3(255, 0, 0);
    } else if (cmd == "LED3:BLUE") {
      setLED3(0, 0, 255);
    }
  }
}

// ============ LED CONTROL FUNCTIONS ============

void setLED3(int r, int g, int b) {
  // LED3 es RGB (todos los colores)
  // Reducir brillo para no quemar
  int adjustedR = r * 0.3;
  int adjustedG = g * 0.5;
  int adjustedB = b * 0.5;

  analogWrite(LED3_RED, adjustedR);
  analogWrite(LED3_GREEN, adjustedG);
  analogWrite(LED3_BLUE, adjustedB);
}
