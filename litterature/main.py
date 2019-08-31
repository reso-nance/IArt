#!/usr/bin/env python
# -*- coding: utf-8 -*-
#  

import os, signal
from threading import Thread
import UI, arduino, markov

HTTPlisteningPort=8080 # ports numbers below 1000 are typically forbidden for non-root users
flaskBind="localhost"
arduinoThread = None

def exitCleanly():
    global arduinoThread
    if arduinoThread is not None : 
        arduinoThread.stop()
        print("exited arduino listener")
    raise SystemExit
    
if __name__ == '__main__':
    signal.signal(signal.SIGTERM, exitCleanly) # register this exitCleanly function to be called on sigterm
    arduinoThread = Thread(target=arduino.listen)
    # ~ arduinoThread.start()
    markov.initialiseCorpuses()
    print("---starting web interface on %s:%i---\n" % (flaskBind, HTTPlisteningPort))
    try: UI.socketio.run(UI.app, host=flaskBind, port=HTTPlisteningPort)  # Start the asynchronous web server (flask-socketIO)
    except KeyboardInterrupt: exitCleanly() # quit on ^C
    
