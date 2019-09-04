#!/usr/bin/env python
# -*- coding: utf-8 -*-
#  
import subprocess
testFile = "mathieu.jpg"

for layer in range(1,10):
	for iterations in (20, 30, 40):
		for blend in (.1, .2, .5, .8) :
			for repeats in (1,8):
				for step in(0.5,1):
					rescale = 0.1
					returnCode = 1
					while returnCode != 0 :
						rescale +=.1
						if rescale > 1 : raise SystemError
						cmd = "python3 dream_image.py %s --layer=%i --iter=%i --repeats=%i --blend=%.02f --rescale=%.02f --step=%.02f" % (testFile, layer, iterations, repeats, blend, rescale, step)
						returnCode = subprocess.call(cmd, shell=True)
