#!/usr/bin/env python
# -*- coding: utf-8 -*-
#  


if __name__ == '__main__':
    raise SystemExit("This arduino file is not meant to be executed directly. It should be imported as a module.")
    
def generateText():
    pass
    
def changeParameter(parameter):
    for name, value in parameter.items() :
        print("changed parameter %s to %s" % (name, value))
        if value == "ON" : value = True
        elif value == "OFF" : value = False
        else value = int(value)
    pass
