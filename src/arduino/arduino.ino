/*
Copyright (c) 2025, John Simonis
This code was written by John Simonis for the GreyGoo research project at The Ohio State University.
See LICENSE.txt for more information.
*/

#include <QMC5883LCompass.h>
#include <CheapStepper.h>
#include <EEPROM.h>

QMC5883LCompass compass;
CheapStepper stepper(8, 9, 10, 11);

const int SAMPLE_COUNT = 1000;
const int STEPS_PER_REV = 4096;
const int STEP_OFFSET = 150;  // tuning offset for mechanical error
const int DEGREE_STEPS = STEPS_PER_REV / 360;

long B_X0 = 0, B_Y0 = 0, B_Z0 = 0;

void saveCalibration() {
  EEPROM.put(0, B_X0);
  EEPROM.put(4, B_Y0);
  EEPROM.put(8, B_Z0);
  Serial.println("Calibration saved to EEPROM.");
}

void loadCalibration() {
  EEPROM.get(0, B_X0);
  EEPROM.get(4, B_Y0);
  EEPROM.get(8, B_Z0);
  Serial.print("Loaded calibration: ");
  Serial.print(B_X0); Serial.print(" ");
  Serial.print(B_Y0); Serial.print(" ");
  Serial.println(B_Z0);
}

void calibrate() {
  long sumX = 0, sumY = 0, sumZ = 0;

  Serial.println("Calibrating...");
  for (int i = 0; i < SAMPLE_COUNT; ++i) {
    compass.read();
    sumX += compass.getX();
    sumY += compass.getY();
    sumZ += compass.getZ();
    delay(10);
  }

  B_X0 = sumX / SAMPLE_COUNT;
  B_Y0 = sumY / SAMPLE_COUNT;
  B_Z0 = sumZ / SAMPLE_COUNT;

  Serial.print("Baseline: ");
  Serial.print(B_X0); Serial.print(" ");
  Serial.print(B_Y0); Serial.print(" ");
  Serial.println(B_Z0);

  saveCalibration();
}

void runMeasurement() {
  for (int i = 0; i < 360; ++i) {
    compass.read();

    int dx = compass.getX() - B_X0;
    int dy = compass.getY() - B_Y0;
    int dz = compass.getZ() - B_Z0;

    float mag = sqrt((long)dx * dx + (long)dy * dy + (long)dz * dz);

    Serial.print(i);
    Serial.print(" | ");
    Serial.print(dx); Serial.print(" ");
    Serial.print(dy); Serial.print(" ");
    Serial.print(dz); Serial.print(" | ");
    Serial.println(mag, 2);

    for (int j = 0; j < DEGREE_STEPS; ++j)
      stepper.step(1);
    delay(100);
  }

  Serial.print("Adding step offset: ");
  Serial.println(STEP_OFFSET);
  for (int j = 0; j < STEP_OFFSET; ++j)
    stepper.step(1);
}

void setup() {
  Serial.begin(9600);
  compass.init();
  stepper.setRpm(20);
  delay(500);

  loadCalibration();

  Serial.println("Ready. Send 'c' to calibrate, 'r' to run measurement.");
}

void loop() {
  if (Serial.available()) {
    char cmd = Serial.read();
    if (cmd == 'c') {
      calibrate();
    } else if (cmd == 'r') {
      runMeasurement();
    }
  }
}

