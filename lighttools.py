"""
Functions for controlling a strip of neopixels
Jim, 29/04/2015
Some functions taken from the ws281x library.
TODO: Either modify neopixels.py or make this a complete wrapper for it
"""

from neopixel import *
import numpy as np

BLACK = Color(0, 0, 0)
WHITE = Color(255, 255, 255)
RED = Color(255, 0, 0)

def wheel(pos, n = 255):
    """Generate rainbow colors across n positions."""
    r = 3 * int(255/n) # We always want range 0-255 for each pixel
    p = pos * 3 * r
    if pos < (n / 3):
        return Color(pos * r, n - pos * r, 0)
    elif pos < (2 * n / 3):
        pos -= int(n / 3)
        return Color(n - pos * r, 0, pos * r)
    else:
        pos -= int(2 * n / 3)
        return Color(0, pos * r, n - pos * r)

class sarahs_colours:
    def __init__(self):

        # Sarah's colours makes a spectrum of colours with blocks of continuous colours and controllable transitions
        #
	    # Returns a list of np.array objects of the form [r,g,b]
        # TODO make it work for any number of pixels /doh
	    #
        colours = []
        rgbs = []
        r, g, b = 255, 0, 0
        colour_px, step_px = 11, 8    
        transitions = [(0, 16, 0), (0, 15, 0), (-31, 0 , 0), (0, 0 , 31), (0, -31, 0), (15, 0, 0), (16, 0, -16)]

        for i in range(len(transitions)): #Notes
            r1, g1, b1 = transitions[i]
            for j in range(colour_px):
                rgbs.append(np.array([r, g, b]))
                colours.append(Color(r, g, b))
            for j in range(step_px):
                r += r1
                g += g1
                b += b1
                rgbs.append(np.array([r, g, b]))
                colours.append(Color(r, g, b))
    
        #and the final colour also held
        for j in range(colour_px):
                rgbs.append(np.array([r, g, b]))
                colours.append(Color(r, g, b))

        self.colours = colours
        self.rgbs = rgbs

    def getColour(i):
        return colours[i]

    def getRGB(i):
        return rgbs[i]

def whitelight(strip, mags):
    for i in range(len(strip.numPixels())):
        strip.setPixelColor(i, Color(mags[i], mags[i], mags[i]))
    strip.show()

def clear(strip):
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, BLACK)
    strip.show()

def arrayToColour(array):
    #Turns a 3-element array into a neopixel Color
    # Input should be scaled to 0-255
    r, g, b = int(array[0]), int(array[1]), int(array[2])
    return Color(r, g, b)
    
def setpixels(strip, colours):
    # Convenience method that sets and updates the entire strip
    # Takes a list of integers that map directly to 24-bit colour space or a list of [r,g,b] ndarrays
    # Duck typing preferred to overloading or type checking...
    # ZIP!!!
    """
    for lat, long in zip(Latitudes, Longitudes):
    print lat, long
    """
    
      
    # Check whether we have more pixels or colours
    # TODO: scaling options to always use all pixels?
    if len(colours) > strip.numPixels() :
        for i in range(strip.numPixels()):
            try: #Simplest case; we got a list of integers that map directly to 24-bit colour space
                strip.setPixelColor(i, colours[i])
            except: #We got a list of rgb arrays
                strip.setPixelColor(i, arrayToColour(colours[i]))
    else:
        for i in range(len(colours)):
            try:
                strip.setPixelColor(i, colours[i])
            except:
                strip.setPixelColor(i, arrayToColour(colours[i]))
    
    strip.show()

