#!/usr/bin/env python
# -*- coding: utf-8 -*-
#  
from flask import Flask, g, render_template, redirect, request, url_for, copy_current_request_context, send_file, flash, Markup, Response
from flask_socketio import SocketIO, emit
import os, logging, subprocess, eventlet, cv2
eventlet.monkey_patch() # needed to make eventlet work asynchronously with socketIO, 

mainTitle = "IArt img"
webcamScale = 1
lastFrame = None

if __name__ == '__main__':
    raise SystemExit("This UI file is not meant to be executed directly. It should be imported as a module.")

for i in range(10):
    try : camera = cv2.VideoCapture(i)
    except : continue
    print("using camera #%i" % i)
    break
else : 
    print("unable to find any camera on this device")
    raise SystemError
camera = cv2.VideoCapture(2) # FIXME : debug

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
    return render_template('img.html', **general_Data)

@app.route('/video_feed')
def video_feed():
    return Response(getImage(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/shutdown')
def rte_bye():
    general_Data = {'title':mainTitle}
    return render_template('shutdown.min.html', **general_Data)    

@app.route('/onlineTracker<ID>.jpg')
def rte_trk(ID):
    filePath = os.path.abspath(os.path.dirname(__file__)) + "/static/trk.jpg"
    return send_file(filePath, mimetype='image/jpg')
    
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
 
# --------------- FUNCTIONS ----------------

def getImage():
    global lastFrame
    while True:
        try :
            _, frame = camera.read()
            if webcamScale != 1.0 :
                frame = cv2.resize(frame, (0,0), fx=webcamScale, fy=webcamScale) 
            _, jpg = cv2.imencode('.jpg', frame)
            lastFrame = jpg.tobytes()
        except KeyboardInterrupt : raise
        except: pass
        yield (b'--frame\r\n'
                   # ~ b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                   b'Content-Type: image/jpeg\r\n\r\n' + lastFrame + b'\r\n')
