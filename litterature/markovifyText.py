#!/usr/bin/env python
# -*- coding: utf-8 -*-
import markovify, os, sys

if "--spacy" in " ".join(sys.argv[2:]) :
    import re
    import spacy
    print("\n------------- using spacy ------------\n\n")
    nlp = spacy.load("fr_core_news_sm")
    class POSifiedText(markovify.Text):
        def word_split(self, sentence):
            return ["::".join((word.orth_, word.pos_)) for word in nlp(sentence)]

        def word_join(self, words):
            sentence = " ".join(word.split("::")[0] for word in words)
            return sentence
 
elif "--nltk" in " ".join(sys.argv[2:]) :
    import nltk
    import re
    print("\n------------- using NLTK ------------\n\n")
    class POSifiedText(markovify.Text):
        def word_split(self, sentence):
            words = re.split(self.word_split_pattern, sentence)
            words = [ "::".join(tag) for tag in nltk.pos_tag(words) ]
            return words

        def word_join(self, words):
            sentence = " ".join(word.split("::")[0] for word in words)
            return sentence

else : print("\n------------- using default markovify model ------------\n\n")
    

try : corpusFilename = sys.argv[1]
except IndexError :
    print("usage : python3 markovifyText.py <corpus filename>.txt [ --nltk || --spacy ]")
    raise SystemExit

if not os.path.isfile(corpusFilename) :
    print("file '%s' not found" % corpusFilename)
    raise SystemExit

# Get raw text as string.
with open(corpusFilename) as f:
    text = f.read()

# Build the model.
text_model = markovify.Text(text)

# Print five randomly-generated sentences
for i in range(5):
    print(text_model.make_sentence()+"\n")

print()

# Print three randomly-generated sentences of no more than 500 characters
for i in range(3):
    print(text_model.make_short_sentence(500)+"\n")
