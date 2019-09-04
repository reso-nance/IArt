#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime
import mchmm as mc
import time, numpy
import UI

continuousLearning = False
keysCurrentlyPressed = {}
observations = numpy.array([])
lastKeyPressed = None
lastKeyPressedTime = datetime.now()
removeSilenceFromVisualisation = True
period = 10. # in ms
playThreeshold = 1.5 # inactivity time after which the generated sequence will play (in seconds)
playBuffer = numpy.array([])
lastKeyPlayed = None
silentEnding = int(playThreeshold*1000 / period) # number of observations that corresponds to the waiting period
silentEndingRemoved = False # to avoid removing it twice

if __name__ == '__main__':
    raise SystemExit("This keyboard file is not meant to be executed directly. It should be imported as a module.")
 

def on_keydown(key):
    print("keydown :", key)
    global keysCurrentlyPressed, lastKeyPressed, lastKeyPressedTime, playBuffer, observations, silentEndingRemoved
    if key == "reset": # clear observation on special keys
        playBuffer = numpy.array([])
        observations = numpy.array([])
        return
    if key not in keysCurrentlyPressed : 
        keysCurrentlyPressed.update({key:datetime.now()})
        lastKeyPressedTime = datetime.now()
    lastKeyPressed = key
    markovData = getMarkovProbas(observations)
    if markovData : UI.sendMarkovDataToUI(markovData)
    if silentEndingRemoved : silentEndingRemoved = False

def on_keyup(key):
    global keysCurrentlyPressed, observations
    if key in keysCurrentlyPressed : del keysCurrentlyPressed[key]

def getMarkovProbas(observations) :
    global removeSilenceFromVisualisation
    if removeSilenceFromVisualisation : observations = observations[observations != "0"]
    markovChain = mc.MarkovChain().from_data(observations)
    names = [n for n in markovChain.states] # needed to convert np array into JSON-serialisable list
    weights = markovChain.observed_p_matrix.tolist()
    # ~ weights = [[round(w, 2) for w in W] for W in weights] # round floats to 3 digits
    weights = [[w for w in W] for W in weights]
    print("states :", names)
    print("probas :", weights)
    if len(names) > 1 : return {"weights":weights, "names":names}
    else : return False

def listen() :
    global observations,playBuffer, lastKeyPlayed, period, playThreeshold, lastKeyPressedTime, silentEnding, silentEndingRemoved
    print("started listening to web events")
    while True :
        
        timeElapsedSinceKeyboard = datetime.now() - lastKeyPressedTime
        if timeElapsedSinceKeyboard.seconds > playThreeshold : # play mode, uninterrupted
            if len(playBuffer) == 0 : # nothing to play yet
                if not silentEndingRemoved : 
                    observations = observations[:-silentEnding]
                    silentEndingRemoved = True
                if len(observations) > 500 :
                    # ~ print(observations)
                    markovChain = mc.MarkovChain().from_data(observations)
                    samplesToPlay = min(int(len(observations)/2), int(10000/period)) # will play longer on stronger databases, 10s max
                    # ~ ids, playBuffer = markovChain.simulate(samplesToPlay, start=lastKeyPressed)
                    ids, playBuffer = markovChain.simulate(10000, start=lastKeyPressed)
            else : # we are continuing to play previously computed predictions
                if not continuousLearning and len(observations) > 0 : observations = numpy.array([]) #clear database when playing
                if playBuffer[0] == "0" : # this is a pause
                    print("PAUSE")
                    if lastKeyPlayed is not None : # we've pressed a key
                        UI.stopSound(lastKeyPlayed)
                        print("OFF_"+lastKeyPlayed)
                        lastKeyPlayed = None
                elif playBuffer[0] != lastKeyPlayed and lastKeyPlayed is not None : # were changing from one key to another
                    UI.stopSound(lastKeyPlayed)
                    print("OFF_"+lastKeyPlayed)
                    lastKeyPlayed = playBuffer[0]
                    UI.playSound(playBuffer[0])
                    print("ON_"+lastKeyPlayed)
                elif lastKeyPlayed is None : # we are pressing a key coming from a pause
                    lastKeyPlayed = playBuffer[0]
                    UI.playSound(playBuffer[0])
                    print("ON_"+lastKeyPlayed)
                    
                playBuffer = numpy.delete(playBuffer, 0)
                
                
        elif len(keysCurrentlyPressed) > 0 : # record mode : a key is pressed
            observations = numpy.append(observations, lastKeyPressed)
            if len(playBuffer) > 0 : playBuffer = numpy.array([])
        else : # record mode : nothing is pressed
            observations = numpy.append(observations, '0')
        
        if len(playBuffer) > 0 : time.sleep(period/1000)
        else : time.sleep(period/1000)

