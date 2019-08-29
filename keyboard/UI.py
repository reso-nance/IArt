#!/usr/bin/env python
# -*- coding: utf-8 -*-
#  
from flask import Flask, g, render_template, redirect, request, url_for, copy_current_request_context, send_file, flash, Markup
from flask_socketio import SocketIO, emit
import os, logging, subprocess, eventlet
from threading import Thread #FIXME only used to debug
eventlet.monkey_patch() # needed to make eventlet work asynchronously with socketIO

import random

mainTitle = "IArt keyboard"
thread = None

if __name__ == '__main__':
    raise SystemExit("This UI file is not meant to be executed directly. It should be imported as a module.")
    
# Initialize Flask and flask-socketIO
app = Flask(__name__)
app.url_map.strict_slashes = False # don't terminate each url by / ( can mess with href='/#' )
socketio = SocketIO(app, async_mode="eventlet")
# ~ socketio = SocketIO(app, async_mode="threading", ping_timeout=36000)# set the timeout to ten hours, defaut is 60s and frequently disconnects
# disable flask debug (except errors)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# --------------- FLASK ROUTES ----------------

@app.route('/')
def rte_homePage():
    general_Data = {'title':mainTitle}
    global thread #FIXME debug
    if thread is None:
        thread = Thread(target=simulateMarkov)
        thread.start()
    return render_template('home.html', **general_Data)
    
@app.route('/shutdown')
def rte_bye():
    general_Data = {'title':mainTitle}
    return render_template('shutdown.min.html', **general_Data)    

# --------------- SOCKET IO EVENTS ----------------

@socketio.on('connect', namespace='/home')
def onConnect():
    print("client connected, session id : "+request.sid)

@socketio.on('disconnect', namespace='/home')
def onDisconnect():
    print("client disconnected")

@socketio.on('shutdown', namespace='/notifications')
def sck_shutdown():
    print("system shutdown called from frontend")
    subprocess.Popen("sleep 3; sudo shutdown now", shell=True)
    socketio.emit("redirect", "/shutdown", namespace='/notifications')

# ~ @socketio.on('midiSlider', namespace='/home')
# ~ def sck_midiSlider(data):
    # ~ if not audio.isMidiRecording :
        # ~ midi.sendCC(control=int(data["control"]), value=int(data["value"]))
 
# --------------- FUNCTIONS ----------------
def simulateMarkov() : #FIXME debug
	while True :
		socketio.sleep(1)
		markovWeights = [[random.random(),random.random(),random.random(),random.random(),],[random.random(),random.random(),random.random(),random.random(),],[random.random(),random.random(),random.random(),random.random(),],[random.random(),random.random(),random.random(),random.random(),]]
		markovNames = ["do","ré","mi","fa"]
		socketio.emit("weightUpdate", {"weights":markovWeights, "names":markovNames}, namespace='/home')
		print("updated markov weights :", markovWeights)
