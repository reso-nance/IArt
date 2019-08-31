#!/usr/bin/env python
# -*- coding: utf-8 -*-
#  
import markovify, os, sys, re, spacy, glob, json

scriptPath = os.path.abspath(os.path.dirname(__file__))
corpusPath = scriptPath+"/corpus/"
availableCorpuses = None
markovModel = None
corpusMix = []

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
    
def generateModel():
    global markovModel, corpusMix
    models = [c["model"] for c in corpusMix]
    weights = [c["mix"] for c in corpusMix]
    markovModel = markovify.combine(models, weights)
    return markovModel
    
    
def generateText(sentenceLength = 280):
    return generateModel().make_short_sentence(sentenceLength)
    
def changeParameter(parameter):
    global corpusMix
    for name, value in parameter.items() :
        print("changed parameter {} to {}".format(name, value))
        if name == "potA" : corpusMix[0]["mix"] = value
        elif name == "potB" : corpusMix[1]["mix"] = value
        elif name == "potC" : corpusMix[2]["mix"] = value
        elif name == "start" and value is True : print(generateText())

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

def loadModelFromJson(path):
    with open(path, "r", encoding="utf-8") as json_file:
        data = json.dumps(json.load(json_file))
    model = markovify.Text.from_json(data)
    return model

def initialiseCorpuses():
    global availableCorpuses
    availableCorpuses = []
    for path in glob.glob(corpusPath+"*.txt") :
        pathWithoutExt = os.path.splitext(path)[0]
        filename, filenameWithoutExt = os.path.basename(path), os.path.splitext(os.path.basename(path))[0]
        if not os.path.isfile(pathWithoutExt+".json") :
            print("new corpus %s found, computing model..." % filename)
            if not buildModel(path) :
                print("ERROR computing %s model" % filename)
                break
        else : print("using precomputed corpus %s" % filenameWithoutExt)
        # ~ availableCorpuses.append({"name":filenameWithoutExt, "file":pathWithoutExt+".json", "model":None, "mix":1.})
        availableCorpuses.append({"name":filenameWithoutExt, "model":loadModelFromJson(pathWithoutExt+".json"), "mix":1.})
        # ~ testSentence = availableCorpuses[-1]["model"].make_short_sentence(280)
        # ~ if testSentence : print(testSentence)

    if len(availableCorpuses) < 3 :
        print("\nNot enough corpuses to continue, needs %i more !" % 3-len(availableCorpuses))
        raise SystemError
    for i in range(3): corpusMix.append(availableCorpuses[i])
    generateModel()
    print("\n---corpuses initialised successfully---\n")
    # ~ print(generateText())
    return
            
