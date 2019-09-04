#!/usr/bin/env python
# -*- coding: utf-8 -*-
#  
'''
Some info on various layers, so you know what to expect
depending on which layer you choose:

layer 1: wavy
layer 2: lines
layer 3: boxes
layer 4: circles?
layer 6: dogs, bears, cute animals.
layer 7: faces, buildings
layer 8: fish begin to appear, frogs/reptilian eyes.
layer 10: Monkies, lizards, snakes, duck

Choosing various parameters like num_iterations, rescale,
and num_repeats really varies on which layer you're doing.


We could probably come up with some sort of formula. The
deeper the layer is, the more iterations and
repeats you will want.

Layer 3: 20 iterations, 0.5 rescale, and 8 repeats is decent start
Layer 10: 40 iterations and 25 repeats is good. 
'''

from deepdreamer import model, load_image, recursive_optimize
import numpy as np
import PIL.Image, argparse, os
from datetime import datetime

# ~ fileName = "the-starry-night/the-starry-night-800x450.jpg"
# ~ num_iterations = 20
# ~ num_repeats = 8
# ~ layer = 3
parser = argparse.ArgumentParser()
parser.add_argument("filename")
parser.add_argument('--layer', default=3, type=int,
                    help='layer 1: \nlayer 2: lines\nlayer 3: boxes\nlayer 4: circles?\nlayer 6: dogs, bears, cute animals.\nlayer 7: faces, buildings\nlayer 8: fish begin to appear, frogs/reptilian eyes.\nlayer 10: Monkies, lizards, snakes, duck')         
parser.add_argument('--iter', default=20, type=int,
                    help='iteration number, should increase on deeper layers')
parser.add_argument('--repeats', default=8, type=int,
                    help='How many "passes" over the data. More passes, the more granular the gradients will be.')
parser.add_argument('--blend', default=0.2, type=float,
                    help='self explanatory')
parser.add_argument('--rescale', default=0.5, type=float,
                    help='self explanatory')
parser.add_argument('--step', default=1.0, type=float,
                    help='size of steps')
args = parser.parse_args()
fileName, layer, num_iterations, num_repeats, blend, rescale, stepSize  = args.filename, args.layer, args.iter, args.repeats, args.blend, args.rescale, args.step
print(args) 

if not os.path.isfile(fileName) :
    print("file '%s' not found" % fileName)
    raise SystemExit
startTime=datetime.now()

layer_tensor = model.layer_tensors[layer]
img_result = load_image(filename='{}'.format(fileName))

img_result = recursive_optimize(layer_tensor=layer_tensor, image=img_result,
                 # how clear is the dream vs original image        
                 num_iterations=num_iterations, step_size=stepSize, rescale_factor=rescale,
                 # How many "passes" over the data. More passes, the more granular the gradients will be.
                 num_repeats=num_repeats, blend=blend)

img_result = np.clip(img_result, 0.0, 255.0)
img_result = img_result.astype(np.uint8)
result = PIL.Image.fromarray(img_result, mode='RGB')
timeElapsed = round((datetime.now() - startTime).total_seconds())
print("finished, took %i seconds" % timeElapsed)
result.save(os.path.splitext(fileName)[0]+"_layer%i-iter%i-rep%i-scale%.02f-blend%.02f-stepS%.02f-%is.jpg" % (layer,num_iterations,num_repeats, blend, rescale, stepSize, timeElapsed))
# ~ result.show()





