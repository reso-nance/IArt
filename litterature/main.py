#!/usr/bin/env python
# -*- coding: utf-8 -*-
#  
import eventlet
eventlet.monkey_patch()
from eventlet.green import threading

import os, signal
import UI, markov

HTTPlisteningPort=8080 # ports numbers below 1000 are typically forbidden for non-root users
flaskBind="localhost"
arduinoThread = None
OSCenabled = True

if OSCenabled : import OSCserver
    
else : 
    # ~ from threading import Thread
    import arduino

def exitCleanly():
    global arduinoThread
    if not OSCenabled and arduinoThread is not None : 
        arduinoThread.stop()
        print("exited arduino listener")
    # ~ if OSCenabled and OSCserverThread is not None : 
    if OSCenabled : 
        OSCserver.server.stop()
        print("exited OSC server")
    raise SystemExit
    
if __name__ == '__main__':
    signal.signal(signal.SIGTERM, exitCleanly) # register this exitCleanly function to be called on sigterm
    markov.initialiseCorpuses()
    if OSCenabled : 
        print("--- starting OSC server ---")
        OSCserver.startListening()
    else :
        arduinoThread = threading.Thread(target=arduino.listen)
        arduinoThread.start()
        
    print("---starting web interface on %s:%i---\n" % (flaskBind, HTTPlisteningPort))
    try:
        UI.socketio.run(UI.app, host=flaskBind, port=HTTPlisteningPort)  # Start the asynchronous web server (flask-socketIO)
    except KeyboardInterrupt: exitCleanly() # quit on ^C
