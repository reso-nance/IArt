#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ~ import eventlet
# ~ eventlet.monkey_patch()
from datetime import datetime
import mchmm as mc
import time, numpy, mido, threading, subprocess, sys
import UI

continuousLearning = False
keysCurrentlyPressed = {}
observations = numpy.array([])
lastKeyPressed = None
lastKeyPressedTime = datetime.now()
removeSilenceFromVisualisation = True
# ~ interfaceName = 'nanoKONTROL2:nanoKONTROL2 MIDI 1 20:0' # as listed by mido.get_input_names()
interfaceName = 'VMini:VMini MIDI 1 20:0' # as listed by mido.get_input_names()
midiListenerThread = None
stopListening = False
period = 5. # in ms
playThreeshold = 1.5 # inactivity time after which the generated sequence will play (in seconds)
playBuffer = numpy.array([])
lastKeyPlayed = None
silentEnding = int(playThreeshold*1000 / period) # number of observations that corresponds to the waiting period
silentEndingRemoved = False # to avoid removing it twice
midi2notes = {12: 'C0', 13: 'C#/Db0', 14: 'D0', 15: 'D#/Eb0', 16: 'E0', 17: 'F0', 18: 'F#/Gb0', 19: 'G0', 20: 'G#/Ab0', 120: 'C9', 121: 'C#/Db9', 122: 'D9', 123: 'D#/Eb9', 124: 'E9', 125: 'F9', 126: 'F#/Gb9', 127: 'G9', 21: 'A0', 22: 'A#/Bb0', 23: 'B0', 24: 'C1', 25: 'C#/Db1', 26: 'D1', 27: 'D#/Eb1', 28: 'E1', 29: 'F1', 30: 'F#/Gb1', 31: 'G1', 32: 'G#/Ab1', 33: 'A1', 34: 'A#/Bb1', 35: 'B1', 36: 'C2', 37: 'C#/Db2', 38: 'D2', 39: 'D#/Eb2', 40: 'E2', 41: 'F2', 42: 'F#/Gb2', 43: 'G2', 44: 'G#/Ab2', 45: 'A2', 46: 'A#/Bb2', 47: 'B2', 48: 'C3', 49: 'C#/Db3', 50: 'D3', 51: 'D#/Eb3', 52: 'E3', 53: 'F3', 54: 'F#/Gb3', 55: 'G3', 56: 'G#/Ab3', 57: 'A3', 58: 'A#/Bb3', 59: 'B3', 60: 'C4', 61: 'C#/Db4', 62: 'D4', 63: 'D#/Eb4', 64: 'E4', 65: 'F4', 66: 'F#/Gb4', 67: 'G4', 68: 'G#/Ab4', 69: 'A4', 70: 'A#/Bb4', 71: 'B4', 72: 'C5', 73: 'C#/Db5', 74: 'D5', 75: 'D#/Eb5', 76: 'E5', 77: 'F5', 78: 'F#/Gb5', 79: 'G5', 80: 'G#/Ab5', 81: 'A5', 82: 'A#/Bb5', 83: 'B5', 84: 'C6', 85: 'C#/Db6', 86: 'D6', 87: 'D#/Eb6', 88: 'E6', 89: 'F6', 90: 'F#/Gb6', 91: 'G6', 92: 'G#/Ab6', 93: 'A6', 94: 'A#/Bb6', 95: 'B6', 96: 'C7', 97: 'C#/Db7', 98: 'D7', 99: 'D#/Eb7', 100: 'E7', 101: 'F7', 102: 'F#/Gb7', 103: 'G7', 104: 'G#/Ab7', 105: 'A7', 106: 'A#/Bb7', 107: 'B7', 108: 'C8', 109: 'C#/Db8', 110: 'D8', 111: 'D#/Eb8', 112: 'E8', 113: 'F8', 114: 'F#/Gb8', 115: 'G8', 116: 'G#/Ab8', 117: 'A8', 118: 'A#/Bb8', 119: 'B8'}
notes2midi = {v:k for k,v in midi2notes.items()}
audioFolder = sys.path[0]+"/static/audio/piano"
alsaSound = True # WIP


if __name__ == '__main__':
    raise SystemExit("This keyboard file is not meant to be executed directly. It should be imported as a module.")
 

def on_keydown(midiNote):
    global keysCurrentlyPressed, lastKeyPressed, lastKeyPressedTime, playBuffer, observations, silentEndingRemoved
    if midiNote in (36, 38, 42, 46) : # clear observation on special keys
        print("resetting database")
        playBuffer = numpy.array([])
        observations = numpy.array([])
        UI.statusText("j'ai tout oublié")
        return
    midiNote = midi2notes[midiNote]
    if midiNote not in keysCurrentlyPressed : 
        keysCurrentlyPressed.update({midiNote:datetime.now()})
        lastKeyPressedTime = datetime.now()
    lastKeyPressed = midiNote
    markovData = getMarkovProbas(observations)
    if markovData : UI.sendMarkovDataToUI(markovData)
    if silentEndingRemoved : silentEndingRemoved = False
    playKey(midiNote)

def on_keyup(midiNote):
    global keysCurrentlyPressed, observations
    if midiNote in keysCurrentlyPressed : del keysCurrentlyPressed[midiNote]

def getMarkovProbas(observations) :
    global removeSilenceFromVisualisation
    if removeSilenceFromVisualisation : observations = observations[observations != "0"]
    markovChain = mc.MarkovChain().from_data(observations)
    names = [n for n in markovChain.states] # needed to convert np array into JSON-serialisable list
    weights = markovChain.observed_p_matrix.tolist()
    # ~ weights = [[round(w, 2) for w in W] for W in weights] # round floats to 3 digits
    weights = [[w for w in W] for W in weights]
    # ~ print("states :", names)
    # ~ print("probas :", weights)
    if len(names) > 1 : return {"weights":weights, "names":names}
    else : return False

def listen() :
    global observations,playBuffer, lastKeyPlayed, period, playThreeshold, lastKeyPressedTime, silentEnding, silentEndingRemoved, midiListenerThread
    midiListenerThread = threading.Thread(target = midiListener, args=(interfaceName,))
    midiListenerThread.start()
    # ~ eventlet.spawn(midiListener, (interfaceName,))
    
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
                        # ~ UI.stopSound(lastKeyPlayed)
                        # ~ print("OFF_"+lastKeyPlayed)
                        lastKeyPlayed = None
                elif playBuffer[0] != lastKeyPlayed and lastKeyPlayed is not None : # were changing from one key to another
                    # ~ UI.stopSound(lastKeyPlayed)
                    # ~ print("OFF_"+lastKeyPlayed)
                    lastKeyPlayed = playBuffer[0]
                    playKey(playBuffer[0])
                    print("ON_"+lastKeyPlayed)
                elif lastKeyPlayed is None : # we are pressing a key coming from a pause
                    lastKeyPlayed = playBuffer[0]
                    playKey(playBuffer[0])
                    print("ON_"+lastKeyPlayed)
                    
                playBuffer = numpy.delete(playBuffer, 0)
                
                
        elif len(keysCurrentlyPressed) > 0 : # record mode : a key is pressed
            observations = numpy.append(observations, lastKeyPressed)
            if len(playBuffer) > 0 : playBuffer = numpy.array([])
        else : # record mode : nothing is pressed
            observations = numpy.append(observations, '0')
        
        if len(playBuffer) > 0 : time.sleep(period/1000)
        else : time.sleep(period/1000)

def midiListener(interfaceName):
    port = mido.open_input(interfaceName)
    print("  started listening to midi events")
    with mido.open_input():
        if stopListening : return
        for msg in port :
            if msg.type == "note_on" : on_keydown(msg.note)
            elif msg.type == "note_off" : on_keyup(midi2notes[msg.note])

def playKey(midiNote):
    midiNote = int(notes2midi[midiNote])
    if midiNote in range(48, 73) : 
        if alsaSound :
            subprocess.Popen("killall aplay", shell=True)
            cmd = "/usr/bin/aplay -Nq %s/%i.wav" % (audioFolder, midiNote)
            subprocess.Popen(cmd, shell=True)
        else : UI.playSound(str(midiNote))
    else : print(midiNote, "couldn't be played : no wav file match")

