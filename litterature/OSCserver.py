#!/usr/bin/env python
# -*- coding: utf-8 -*-
#  
# ~ import eventlet
# ~ eventlet.monkey_patch() 
import liblo
# ~ eventlet.import_patched("liblo")
from datetime import datetime
import markov

listenPort = 9002
server = None
jerkThreeshold = 30 # magic number determined experimentally
maxJerk = 250 # idem
jerkData = None
lastJerk = datetime.now()
debounce = .5 # min delay between two swings (in seconds)

def unknownOSC(path, args, types, src):
    print("got unknown message '%s' from '%s'" % (path, src.url))
    for a, t in zip(args, types):
        print ("  argument of type '%s': %s" % (t, a))
        
def averageAcc(OSCaddress, OSCparams):
    global jerkData, orientation, lastJerk
    jerk = sum([abs(x) for x in OSCparams])
    # ~ print("jerk", jerk)
    if jerk > jerkThreeshold :
        if jerkData is None : jerkData = []
        jerkData.append(jerk)
    else :
        if jerkData and (datetime.now() - lastJerk).total_seconds()>debounce :
            jerk = max(jerkData)
            # ~ print("max ACC :", jerk)
            jerk = (jerk-jerkThreeshold)/(maxJerk-jerkThreeshold) # map to 0~1
            corpusMix = getCorpusPercentages(jerk)
            markov.changeParameter({"potA":corpusMix[0]}) 
            markov.changeParameter({"potB":corpusMix[1]}) 
            markov.changeParameter({"potC":corpusMix[2]}) 
            corpusMix = [int(c*100) for c in corpusMix]
            print("swing detected : %.02f -> low %i, mid %i, high %i" % (jerk*100,corpusMix[0], corpusMix[1], corpusMix[2] ))
            # ~ print("X:",OSCparams[0], " Y:", OSCparams[1], "Z:", OSCparams[2],"\n")
            # ~ markov.changeParameter({"start":True})
            markov.generateText()
            jerkData = None
            lastJerk = datetime.now()
        else : return

def getCorpusPercentages(value):
    if value > 0.33 : return [0, max(1-value,0), min(value,1)]
    else : return [max(1-value, 0), min(value,1), 0]

def startListening():
    global server
    try:
        server = liblo.ServerThread(listenPort)
        print("  listening to incoming OSC on port %i" % listenPort)
    except liblo.ServerError as e:
        print(e)
        raise SystemError
        
    server.add_method("/generateText", None, markov.OSCgenerateText)
    server.add_method("/setCorpuses", None, markov.OSCsetCorpuses)
    server.add_method("/accelerometer", None, averageAcc)
    server.add_method(None, None, unknownOSC)
    server.start()
    
if __name__ == '__main__':
    print("this file is made to be imported as a module, not executed")
    raise SystemError
