#!/usr/bin/env python
# -*- coding: utf-8 -*-
#  
import markovify, os, sys, re, spacy, glob, json

scriptPath = os.path.abspath(os.path.dirname(__file__))
corpusPath = scriptPath+"/corpus/"
availableCorpuses = None
markovModel = None
corpusMix = [1.,0.,0.]

# overriding POSifiedText to make use of spacy
nlp = spacy.load("fr_core_news_sm")
class POSifiedText(markovify.Text):
    def word_split(self, sentence):
        return ["::".join((word.orth_, word.pos_)) for word in nlp(sentence)]

    def word_join(self, words):
        sentence = " ".join(word.split("::")[0] for word in words)
        return sentence

if __name__ == '__main__':
    raise SystemExit("This arduino file is not meant to be executed directly. It should be imported as a module.")
    
def generateText(NLPmodel, sentenceLength = 280):
    return NLPmodel.make_short_sentence(sentenceLength)
    
def changeParameter(parameter):
    for name, value in parameter.items() :
        print("changed parameter {} to {}".format(name, value))

def buildModel(filename):
    if not os.path.isfile(filename) :
        print("file %s not found" % filename)
        return False
    corpus = open(filename).read()
    textModel = markovify.Text(corpus, state_size=3)
    JSONmodel = textModel.to_json()
    with open (os.path.splitext(filename)[0]+".json", "w", encoding="utf-8") as f :
        json.dump(json.loads(JSONmodel), f, ensure_ascii=False, indent=4)
        return True

def loadModelFromJson(filename):
    with open(corpusPath+filename, "rt") as f :
        JSONmodel = f.read()
    return markovify.Text.from_json(JSONmodel)

def initialiseCorpuses():
    global availableCorpuses
    availableCorpuses = []
    for filename in glob.glob(corpusPath+"*.txt") :
        filenameWithoutExt = os.path.splitext(filename)[0]
        if not os.path.isfile(filenameWithoutExt+".json") :
            print("new corpus %s found, computing model..." % filename)
            if not buildModel(filename) :
                print("ERROR computing %s model" % filename)
                break
        else : print("using precomputed corpus %s" % filename)
        availableCorpuses.append({"name":filenameWithoutExt, "model":filenameWithoutExt+".json"})
        # ~ with open(filenameWithoutExt+".json", "r", encoding="utf-8") as json_file:
            # ~ data = json.load(json_file)
        # ~ model = markovify.Text.from_json(data)
        # ~ print(model.make_short_sentence(280))
    return
            
