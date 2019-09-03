#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#   
#  Copyright 2019 Reso-nance Numérique <laurent@reso-nance.org>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  
mode = None
# ~ mode = "keystrokes" # comment this line to switch to webEvents

import os, signal
from threading import Thread
import UI
if mode == "keystrokes" : import keyboard
else : import webEvents

scriptPath = os.path.abspath(os.path.dirname(__file__))
HTTPlisteningPort=8080 # ports numbers below 1000 are typically forbidden for non-root users
flaskBind="localhost"
if mode == "keystrokes" : keyboardThread = None

def exitCleanly():
    if mode == "keystrokes" : 
        global keyboardThread
        if keyboardThread is not None : 
            keyboardThread.stop()
            print("exited keyboard listener")
    raise SystemExit
    
if __name__ == '__main__':
    signal.signal(signal.SIGTERM, exitCleanly) # register this exitCleanly function to be called on sigterm
    if mode == "keystrokes" : 
        keyboardThread = Thread(target=keyboard.listen)
        keyboardThread.start()
        UI.mainPage = "keyboard.html"
    else : 
        Thread(target=webEvents.listen).start()
    print("starting up webserver on %s:%i..." %(flaskBind, HTTPlisteningPort))
    try: UI.socketio.run(UI.app, host=flaskBind, port=HTTPlisteningPort)  # Start the asynchronous web server (flask-socketIO)
    except KeyboardInterrupt: exitCleanly() # quit on ^C
    
