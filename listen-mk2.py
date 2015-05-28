# -*- coding: utf-8 -*-
"""
Created on Mon Mar 16 21:58:49 2015

Requires pyAudio, install the wheel from http://www.lfd.uci.edu/~gohlke/pythonlibs/

sudo apt-get install git
sudo git clone http://people.csail.mit.edu/hubert/git/pyaudio.git
sudo apt-get install libportaudio0 libportaudio2 libportaudiocpp0 portaudio19-dev
sudo apt-get install python3-dev python3-pip
cd pyaudio
sudo python3 setup.py install
pip-3.2 install numpy --upgrade  #takes bloody ages...

Unload snd-bcm2835 to prevent memory conflict
sudo modprobe -r snd_bcm2835

edit /etc/modules to stop it loading at all
@author: Jim
"""

import pyaudio
import numpy as np
import struct # used for dealing with C-like structs such as the output from pyaudio
import time, math, random 

from neopixel import *
# LED strip configuration:
LED_COUNT      = 144      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 11       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 32     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)


# Some constants for the audio input

CHUNK = 1000 # Samples
FORMAT = pyaudio.paInt16 # binary-packed 2-byte shorts
CHANNELS = 1
RATE = 8000 # Samples per second
RUNTIME = 30 # seconds to capture for
MAXFREQ = RATE//2

OURFREQS = np.array((440,494,523,587,659,698,784,880)) # A minor integers
#OURFREQS = np.array(range(400,900))
BOTTOM = min(OURFREQS)
TOP = max(OURFREQS)

"""
Precompute the frequencies of the bins that the FFT will return
RFFT throws away negatives; for real data they mirror positives
Unitless, range 0 <= f < 0.5, multiply by bitrate for Hz
"""
FFTFIDELITY = 2300 # MAXFREQ # aim for nice easy 1Hz steps. Or try and map to numpixels...
FFTFREQS = (np.fft.rfftfreq(FFTFIDELITY) * RATE).astype(int) # Range 0 -> MAXFREQ step MAXFREQ/FFTFIDELITY

"""
We'll want to ignore frequencies outside the range of interest
Find the bins of interest and their indexes.
"""
OURBINS = np.where(np.logical_and(FFTFREQS > 400, FFTFREQS < 900 ))
#OURBINS = np.in1d(FFTFREQS, OURFREQS)
FFTFREQS = FFTFREQS[OURBINS]
print("Searching for {} frequencies: {} ".format(len(FFTFREQS), FFTFREQS))

# Create NeoPixel object with appropriate configuration.
strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)
# Initialize the library (must be called once before other functions).
strip.begin()

#Just to test the strip
for j in range(strip.numPixels()):
    strip.setPixelColor(j, Color(255, 0, 0)) #wheel(int(Y[i])))
    #print wheel(int(Y[i]))
strip.show()
for j in range(strip.numPixels()):
    strip.setPixelColor(j, Color(0, 0, 0)) #wheel(int(Y[i])))
    #print wheel(int(Y[i]))
strip.show()

def wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
        return Color(pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return Color(255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return Color(0, pos * 3, 255 - pos * 3)

def sarahs_colours():
	# Returns a list of arrays; each array is [r, g, b]
    # TODO make it work for any number of pixels /doh
	#
    colours = []
    colour = np.array([255, 0, 0])  # Starting from RED
    colour_px, step_px = 11, 8
    
    transitions = [(0, 16, 0), (0, 15, 0), (-31, 0 , 0), (0, 0 , 31), (0, -31, 0), (15, 0, 0), (16, 0, -16)]

    for i in range(len(transitions)): #Notes
        for j in range(colour_px):
            colours.append(np.copy(colour)) 
            #print(colour)
        for j in range(step_px):
            colour += transitions[i]
            colours.append(np.copy(colour)) # Add the *value* of the array, not a reference...
            #print(colour)
    
    #and the final colour also held
    for j in range(colour_px):
        colours.append(np.copy(colour))     
    return colours

def goertzel(data, sample_rate, target_freqs):
    """
    Returns one integer per target frequency
	Implemented by Jim from the maths
    """
    out = []
    N = len(data)
    
    for target_freq in target_freqs:    
        k = int(0.5 + (N * target_freq) / sample_rate)
        omega = ((2 * math.pi) / N) * k
        #sin = math.sin(omega) # Not needed for real data
        cosine = math.cos(omega)
        coeff = 2 * cosine

        Q1 = Q2 = 0
        
        for sample in data:
            Q0 = coeff * Q1 - Q2 + sample
            Q2 = Q1
            Q1 = Q0
        magnitude = math.sqrt(Q1**2 + Q2**2-Q1*Q2*coeff) # Real part only
        out.append(magnitude)
        
    # Normalize and ting
    
    
    return out
            
p = pyaudio.PyAudio()

rainbow = sarahs_colours()
for i in range(len(rainbow)):
    #print(rainbow[i][0], int(rainbow[i][1]), int(rainbow[i][2]))
    strip.setPixelColor(i, Color(int(rainbow[i][0]), int(rainbow[i][1]), int(rainbow[i][2])))
#strip.show()
#time.sleep(3)

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

print("* recording")

def whitelight(mags):
    for i in range(len(strip.numPixels())):
        strip.setPixelColor(i, Color(mags[i], mags[i], mags[i]))
    strip.show()
        
while True:
#for i in range(0, int(RATE / CHUNK * RUNTIME)):
	# try/catch because portIO throws an error if we're too slow.
	# We'll lose the full bugffer but should be able to continue anyway.
    try:
        data = stream.read(CHUNK)
    except IOError as e:
        print("Buffer Overflow")
        continue
    structformat = ('{}h').format(CHUNK) # we'll be getting CHUNK shorts at 2 bytes each
    decoded = struct.unpack(structformat, data)
    

    
    """
    magnitudes = goertzel(decoded, RATE, OURFREQS)
    mn = min(magnitudes)
    mx = max(magnitudes) - mn   
    magnitudes[:] = [int((mag - mn) * 255/mx) for mag in magnitudes] # Scale to 255 - Only for the benefit of wheel??
    #print(magnitudes)
    
    # Repeater
    for i in range(0, strip.numPixels(), len(magnitudes)):
        for j in range(len(magnitudes)):
            #print(j, magnitudes[j])
            strip.setPixelColor(i+j, wheel(magnitudes[j]))
    strip.show()
    """
    # TODO - require notes to stay over threshold for x chunks before lighting
    #Keys
    # colours for chords increasing complexity
    # if (note-1 magnitude within specified distance from note-2)
     
    """
    for i in range(len(magnitudes)):
        for j in range(int(strip.numPixels()/len(magnitudes))):
            strip.setPixelColor(i * len(magnitudes) + j, wheel(magnitudes[i]) if magnitudes[i] > 128 else Color(0,0,0))
    strip.show()
    """
    window = np.hanning(CHUNK)
    decoded *= window
    fourier = np.abs(np.fft.rfft(decoded, FFTFIDELITY))
    cropped_fourier = fourier[OURBINS] # Grab the ones we're interested in;
    # Normalize so that the quietest maps to 0 and the loudest to 255. This is not good enough.
    cropped_fourier *= (1/max(cropped_fourier))
    #print(cropped_fourier)
    
    #if (i % 2) == 0:           
    for j in range(len(FFTFREQS)): #(strip.numPixels()):
        ##print(int(fourier[j]))
        ourcolour = rainbow[j] * cropped_fourier[j]
        r, g, b = ourcolour[0], ourcolour[1], ourcolour[2]
        strip.setPixelColor(j, Color(int(r), int(g), int(b))) #wheel(int(cropped_fourier[j]))) #
        #print wheel(int(Y[i]))
    strip.show()
    

print("* done recording")   
stream.stop_stream()
stream.close()
p.terminate()