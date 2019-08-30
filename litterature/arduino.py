#!/usr/bin/env python
# -*- coding: utf-8 -*-
#  

import serial
import markovify

arduinoPort='/dev/ttyUSB1' # udevadm info --query=all --name=/dev/ttyUSB0
baudrate=115200

if __name__ == '__main__':
    raise SystemExit("This arduino file is not meant to be executed directly. It should be imported as a module.")
    
def listen():
    arduino = serial.Serial(arduinoPort,baudrate)
    while True:
        line = arduino.readline();
        if line:
            line = line.decode("utf-8","ignore").replace("\r\n", "")
            print (line)
            if "pot" in line : name, value = line.split(":")
            elif "start" in line : name, value = "start", True
            markovify.changeParameter({name:value})
