#!/usr/bin/env python
# -*- coding: utf-8 -*-
#  
import markovify, os, sys, re, spacy, glob, json
import UI

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
    models = [c["model"] for c in corpusMix if c["mix"] >= 0.01] # the corpus is ignored if it's mix is below 1%
    weights = [c["mix"] for c in corpusMix if c["mix"] >= 0.01]
    # since each corpus has a different size, bigger corpuses tends to be favoritized when mixed along smaller ones
    # to prevent this behavior, we correct each weight by multiplying it by a bias factor  which is inversely prop to the size of the corpus:
    # bias (%) = (allCorpus.len - thisCorpus.len) / allCorpus.len
    # weight = weight * bias
    totalCorpusesLength = sum([c["length"] for c in corpusMix])
    lengthBias = [(totalCorpusesLength - c["length"])/totalCorpusesLength for c in corpusMix]
    weights = [weight * bias for weight,bias in zip(weights,lengthBias)]
    # ~ for i in range(3) : print(corpusMix[i]["name"],corpusMix[i]["mix"], lengthBias[i], weights[i] )
    if len (models) > 1 : markovModel = markovify.combine(models, weights)
    elif len(models) == 1 : markovModel = models[0]
    else : print("no model has a mix >= 1%")
    return markovModel
    
    
def generateText(sentenceLength = 280):
    for i in range(10):
        text = generateModel().make_short_sentence(sentenceLength)
        if text is not None : 
            UI.displayText(text)
            return
    print("unable to generate text 10 times in a row")
    
def changeParameter(parameter):
    global corpusMix
    for name, value in parameter.items() :
        # ~ print("changed parameter {} to {}".format(name, value))
        if name == "potA" : corpusMix[0]["mix"] = value
        elif name == "potB" : corpusMix[1]["mix"] = value
        elif name == "potC" : corpusMix[2]["mix"] = value
        elif name == "start" and value is True : print(generateText())
        elif ("prev" in name or "next" in name) and value is True : UI.showModal(name)
        if name in ("potA", "potB", "potC"): UI.update(corpusMix)

def changeModel(modelIndex, modelName, action="prev"):
    pass

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
    return {"model":model, "length":len(data)}

def initialiseCorpuses():
    global availableCorpuses, corpusMix
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
        model = loadModelFromJson(pathWithoutExt+".json")
        availableCorpuses.append({"name":filenameWithoutExt,"model":model["model"],"length":model["length"], "mix":.5})
        # ~ testSentence = availableCorpuses[-1]["model"].make_short_sentence(280)
        # ~ if testSentence : print(testSentence)

    if len(availableCorpuses) < 3 :
        print("\nNot enough corpuses to continue, needs %i more !" % 3-len(availableCorpuses))
        raise SystemError
    for i in range(3): corpusMix.append(availableCorpuses[i])
    generateModel()
    print("\n---corpuses initialised successfully---\n")
    # ~ print(generateText())
    UI.update(corpusMix)
    generateText()
    return

def debugText(delay=4):
    import time, random
    while True :
        time.sleep(delay)
        generateText(random.randrange(200, 800))
