"""
Functions for controlling a strip of neopixels
Jim, 29/04/2015
Some functions taken from the ws281x library.
TODO: Either modify neopixels.py or make this a complete wrapper for it
"""

from neopixel import Color
import numpy as np
import random

REVERSED = True

BLACK = Color(0, 0, 0)
WHITE = Color(255, 255, 255)
RED = Color(255, 0, 0)

BLACK_RGB = (0, 0, 0)
WHITE_RGB = (255, 255, 255)

def wheel(position, n = 255):
    """Generate rainbow colors across n positions. Returns (R, G, B) tuple"""
    position *= int(255/n) # Scale input to the 0-255 range    
    #p = position * 3 * r
    if position < 85:
        return Color(position*3, 255 - position*3, 0)
    elif position < 170:
        position -= 85
        return Color(255 - position*3, 0, position*3)
    else:
        position -= 170
        return Color(0, position*3, 255 - position*3)

def wheel_RGB(position, n = 255):
    """Generate rainbow colors across n positions. Returns (R, G, B) tuple"""
    position *= int(255/n) # Scale input to the 0-255 range    
    #p = position * 3 * r
    if position < 85:
        return np.array([position*3, 255 - position*3, 0])
    elif position < 170:
        position -= 85
        return np.array([255 - position*3, 0, position*3])
    else:
        position -= 170
        return np.array([0, position*3, 255 - position*3])

class sarahs_colours:
    def __init__(self, n = 144):

        # Makes Sarah's rainbow with blocks of 11 leds of a colour
        # [(255, 0, 0), (255, 128, 0), (255, 255, 0), (2, 255, 0), (0, 255, 255), (0, 0, 255), (128, 0, 255), (255, 0, 128)]
        # and transitions over 8 pixess to the next block
        # this is hopelessly specific, I might as well have just prepopulated a list...
        # 
        # colours: list of colours as 24-bit
        # rgbs: list of colours as [r, g, b] ndarrays
        # n: number of points to return colours over        
        #
        self.n = n
        colours = []
        rgbs = []
        r, g, b = 255, 0, 0
        colour_px, step_px = 11, 8    
        transitions = [(0, 16, 0), (0, 15, 0), (-31, 0 , 0), (0, 0 , 31), 
                       (0, -31, 0), (15, 0, 0), (16, 0, -16)]

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
    
        # and the final colour also held
        for j in range(colour_px):
                rgbs.append(np.array([r, g, b]))
                colours.append(Color(r, g, b))

        self.colours = colours
        """
        for rgb in rgbs:
            runs = 2            
            for run in runs:
        """
            


        self.rgbs = rgbs

    def getColour(self, i):        
        return self.colours[i]

    def getRGB(self, i):
        # Returns a numpy array [r, g, b]
        return self.rgbs[int(i * 144/self.n)]

# def colour_blender(colours, numpixels):
    # Map the 

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
    
def test(strip):
    rands = [[random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)]
             for pixel in range(strip.numPixels())]
    setpixels(strip, rands)

def setpixels(strip, colours, scale = False):
    # Convenience method that sets and updates the entire strip
    # Takes a list of integers that map directly to 24-bit colour space or a list of [r,g,b] ndarrays
     
    # Check whether we have more pixels or colours
    # TODO: scaling options to always use all pixels?  YES!!
    if len(colours) > strip.numPixels() :
        for i in range(strip.numPixels()):
            if REVERSED:
                n = strip.numPixels() - i
            else:
                n = i
            try: #Simplest case; we got a list of integers that map directly to 24-bit colour space
                strip.setPixelColor(n, colours[i])
            except: #We got a list of rgb arrays TODO: but what if we didn't??
                strip.setPixelColor(n, arrayToColour(colours[i]))
    else:
        scalefactor = int(strip.numPixels()/len(colours)) if scale else 1
        for i in range(len(colours)):
            for j in range(scalefactor):
                if REVERSED:
                    n = strip.numPixels() - (i*scalefactor + j)
                else:
                    n = i*scalefactor + j
                try:
                    strip.setPixelColor(n, colours[i])
                except:
                    strip.setPixelColor(n, arrayToColour(colours[i]))
    
    strip.show()
"""
def setpixels(strip, colours):
    # Convenience method that sets and updates the entire strip
    # Takes a list of integers that map directly to 24-bit colour space or a list of [r,g,b] ndarrays
     
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
"""