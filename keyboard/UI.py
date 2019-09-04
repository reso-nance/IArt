#!/usr/bin/env python
# -*- coding: utf-8 -*-
#  
from flask import Flask, g, render_template, redirect, request, url_for, copy_current_request_context, send_file, flash, Markup
from flask_socketio import SocketIO, emit
import os, logging, subprocess, eventlet
from datetime import datetime
eventlet.monkey_patch() # needed to make eventlet work asynchronously with socketIO

import webEvents

general_Data = {'title':"IArt keyboard"}
thread = None
maxUIupdateRate = 1.0 # in seconds
lastUIupdate = datetime.now()
mainPage = "webEvents.html"
# ~ layout = "test.js"
layout = "percussions.js"
# ~ layout = "orchestral.js"

if __name__ == '__main__':
    raise SystemExit("This UI file is not meant to be executed directly. It should be imported as a module.")

if mainPage == "webEvents.html" : general_Data.update({"layout":layout})


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
    sendDefaultMarkovDataToUI()
    return render_template(mainPage, **general_Data)
    
@app.route('/shutdown')
def rte_bye():
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

@socketio.on('keydown', namespace='/home')
def keydown(name):
    webEvents.on_keydown(name)

@socketio.on('keyup', namespace='/home')
def keyup(name):
    webEvents.on_keyup(name)
    

# --------------- FUNCTIONS ----------------

def sendMarkovDataToUI(weights):
    global lastUIupdate, maxUIupdateRate
    lastUpdate = datetime.now() - lastUIupdate
    if lastUpdate.total_seconds() >= maxUIupdateRate :
        socketio.emit("weightUpdate", weights, namespace='/home')
        lastUIupdate = datetime.now()
        print("updated UI, last update was %f seconds ago" % lastUpdate.total_seconds())
    
def sendDefaultMarkovDataToUI():
    defaultMarkovData = {"names":['--', 'do1', 'do#1', 'ré1', 'mib1', 'mi1', 'fa', 'fa#', 'sol', 'sol#', 'la', 'sib', 'si', 'do2', 'do#2', 'ré2', 'mib2', 'mi2'],
                  "weights" : [[0.5]*18]*18}
    socketio.sleep(1)
    socketio.emit("weightUpdate",defaultMarkovData , namespace='/home')

def playSound(name):
    socketio.emit("play", name, namespace="/home")

def stopSound(name):
    socketio.emit("stop", name, namespace="/home")

def genTestData(count): #FIXME debug
    import random, string
    output = []
    for i in range(count) :
        element = []
        for j in range(count): element += [round(random.random(),2)]
        output.append(element)
    print(output)
    alphabet = list(string.ascii_lowercase)
    print([alphabet[random.randrange(len(alphabet))] for i in range(count)])
        

def simulateMarkov() : #FIXME debug
    import random
    while True :
        socketio.sleep(1)
        markovWeights = [[random.random(),random.random(),random.random(),random.random(),],[random.random(),random.random(),random.random(),random.random(),],[random.random(),random.random(),random.random(),random.random(),],[random.random(),random.random(),random.random(),random.random(),]]
        markovNames = ["do","ré","mi","fa"]
        socketio.emit("weightUpdate", {"weights":markovWeights, "names":markovNames}, namespace='/home')
        print("updated markov weights :", markovWeights)
