#!/usr/bin/env python
# -*- coding: utf-8 -*-
#  
from flask import Flask, g, render_template, redirect, request, url_for, copy_current_request_context, send_file, flash, Markup
from flask_socketio import SocketIO, emit
import os, logging, subprocess, eventlet
eventlet.monkey_patch(os=False) # needed to make eventlet work asynchronously with socketIO, address eventlet pathlib bug https://github.com/eventlet/eventlet/issues/534

import markov

mainTitle = "IArt txt"
lastCorpusMix = None
lastDisplayedText = None

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
    return render_template('txt.html', **general_Data)
    
@app.route('/shutdown')
def rte_bye():
    general_Data = {'title':mainTitle}
    return render_template('shutdown.min.html', **general_Data)    

# --------------- SOCKET IO EVENTS ----------------

@socketio.on('connect', namespace='/home')
def onConnect():
    print("client connected, session id : "+request.sid)
    if lastCorpusMix is not None : update(lastCorpusMix)
    if lastDisplayedText is not None : displayText(lastDisplayedText)

@socketio.on('disconnect', namespace='/home')
def onDisconnect():
    print("client disconnected")

@socketio.on('shutdown', namespace='/notifications')
def sck_shutdown():
    print("system shutdown called from frontend")
    subprocess.Popen("sleep 3; sudo shutdown now", shell=True)
    socketio.emit("redirect", "/shutdown", namespace='/notifications')

@socketio.on('getAvailableCorpuses', namespace='/home')
def sendAvailableCorpuses():
    socketio.emit("availableCorpuses",availableCorpuses() , namespace='/home')

@socketio.on('corpusChanged', namespace='/home')
def changeCorpus(data):
    index, name = data["index"], data["name"]
    if markov.corpusMix[index]["name"] != name :
        markov.changeCorpus(index, name)
        sendAvailableCorpuses()

 
# --------------- FUNCTIONS ----------------

def update(corpusMix):
    global lastCorpusMix
    lastCorpusMix = corpusMix
    UIdata = [{"name":c["name"], "value":c["mix"]} for c in corpusMix]
    socketio.emit("updateUI", UIdata, namespace='/home')

def displayText(text):
    global lastDisplayedText
    lastDisplayedText = text
    socketio.emit("displayText", text, namespace='/home')

def availableCorpuses():
    names = [c["name"] for c in markov.availableCorpuses]
    selectedNames = [c["name"] for c in markov.corpusMix]
    return {"names":names, "selectedNames":selectedNames}

def navigateModal(action):
    socketio.emit("navigateCorpus", action, namespace='/home')
