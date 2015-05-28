# -*- coding: utf-8 -*-
"""
Created on Mon Mar 16 21:58:49 2015

Requires pyAudio, install the wheel from http://www.lfd.uci.edu/~gohlke/pythonlibs/
Requires PyQt
Produced in Spyder/Anaconda x64 python 2.7
@author: Jim
"""

import pyaudio
import numpy as np
import struct # used for dealing with C-like structs such as the output from pyaudio
import time, math, random 

from neopixel import *
# LED strip configuration:
LED_COUNT      = 80      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 11       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 64     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)


# Some constants for the audio input

CHUNK = 500 # Samples
FORMAT = pyaudio.paInt16 # binary-packed 2-byte shorts
CHANNELS = 1
RATE = 8000 # Samples per second
RUNTIME = 30 # seconds to capture for
MAXFREQ = RATE//2

#OURFREQS = np.array((440,494,523,587,659,698,784,880)) # A minor integers
OURFREQS = np.array(range(400,900))
BOTTOM = min(OURFREQS)
TOP = max(OURFREQS)

"""
Precompute the frequencies of the bins that the FFT will return
RFFT throws away negatives; for real data they mirror positives
Unitless, range 0 <= f < 0.5, multiply by bitrate for Hz
"""
FFTFIDELITY = 1000 # MAXFREQ # aim for nice easy 1Hz steps...
FFTFREQS = (np.fft.rfftfreq(FFTFIDELITY) * RATE).astype(int) # Range 0 -> MAXFREQ step MAXFREQ/FFTFIDELITY
print(FFTFREQS)

"""
We'll want to ignore frequencies outside the range of interest
Find the bins of interest and their indexes.
"""
# OURBINS = np.where(np.logical_and(FFTFREQS > 400, FFTFREQS < 900 ))
OURBINS = np.in1d(FFTFREQS, OURFREQS)
FFTFREQS = FFTFREQS[OURBINS]
print("Searching for frequencies: ", FFTFREQS)

# Create NeoPixel object with appropriate configuration.
strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)
# Initialize the library (must be called once before other functions).
strip.begin()

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
	
p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
				channels=CHANNELS,
				rate=RATE,
				input=True,
				frames_per_buffer=CHUNK)

print("* recording")


while True:
#for i in range(0, int(RATE / CHUNK * RUNTIME)):

	data = stream.read(CHUNK)
	structformat = ('{}h').format(CHUNK) # we'll be getting CHUNK shorts at 2 bytes each
	decoded = struct.unpack(structformat, data)

	fourier = np.abs(np.fft.rfft(decoded, FFTFIDELITY))
	cropped_fourier = fourier[OURBINS] # Grab the ones we're interested in;
	# Normalize so that the quietest maps to 0 and the loudest to 255. This is not good enough.
	cropped_fourier *= (255/max(cropped_fourier))
	#print(cropped_fourier)
	
	#if (i % 2) == 0:			
	for j in range(len(FFTFREQS)): #(strip.numPixels()):
		##print(int(fourier[j]))
		strip.setPixelColor(j, wheel(int(cropped_fourier[j]))) #Color(int(cropped_fourier[j]), 0, 0))
		#print wheel(int(Y[i]))
	strip.show()
		#print "tick"
	

print("* done recording")	
stream.stop_stream()
stream.close()
p.terminate()