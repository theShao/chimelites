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
import threading
import pyaudio
import numpy as np
import struct # used for dealing with C-like structs such as the output from pyaudio
import time, math, random 

import soundtools, lighttools

from neopixel import *


# LED strip configuration:
LED_COUNT      = 144      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 11       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 16     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)

# Some constants for the audio input
CHUNK = 1024 # Samples
FORMAT = pyaudio.paInt16 # binary-packed 2-byte shorts
CHANNELS = 1
RATE = 11500 # Samples per second
MAXFREQ = RATE//2 # Highest freq it's possible to detect at this sample rate

GOERTZELFREQS = np.array((438,491,521,586,655,691,780,866)) # Aminor scale integers for Goertzel filter
LOWFREQ = 400
HIGHFREQ = 900
FFTFIDELITY = 6350 #magic.


# Create NeoPixel object with appropriate configuration.
strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)
# Initialize the library (must be called once before other functions).
strip.begin()

stream = pyaudio.PyAudio().open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)


rainbow = lighttools.sarahs_colours()

rainbow2 = [lighttools.wheel(n, strip.numPixels()) for n in range(strip.numPixels())]

lighttools.setpixels(strip, rainbow.colours)
time.sleep(0.5)

gfilter = soundtools.goertzelFilter(RATE, CHUNK, GOERTZELFREQS)
fft = soundtools.realFourier(FFTFIDELITY, RATE, CHUNK, (LOWFREQ, HIGHFREQ))

print("* Listening")

pixels = [0 for _ in range(strip.numPixels())]

lighttools.clear(strip)
"""
while True:
    for i in range(strip.numPixels()):
        strip.setPixelColor(i - 1, lighttools.BLACK)
        strip.setPixelColor(i, rainbow.colours[i])
        strip.show()
    for i in reversed(range(strip.numPixels())):
        strip.setPixelColor(i + 1, lighttools.BLACK)
        strip.setPixelColor(i, rainbow.colours[i])
        strip.show()
"""

previous_magnitudes = diffs = magnitudes = np.zeros(8)

while True:
    
    samples = soundtools.getsamples(stream, CHUNK)
    
    if samples == 0:
        # Buffer overflow. Just grab some more data.
        continue
    
    
    magnitudes = gfilter.process(samples)
    mn = min(magnitudes)
    mx = max(magnitudes) - mn   
    #magnitudes[:] = [int((mag - mn) * 255/mx) for mag in magnitudes] # Scale to 255 - Only for the benefit of wheel??

    dominant = magnitudes.index(max(magnitudes))
    primary = rainbow.colours[int(dominant * (strip.numPixels()/len(magnitudes)))] #if mx > (10 * mn) else lighttools.BLACK
    #pixels.insert(0, primary)
    pixels.append(primary) 
    if (len(pixels) > strip.numPixels()):
        pixels.pop(0)
    lighttools.setpixels(strip, pixels)
    

    """
    blocksize = int(strip.numPixels()/len(magnitudes))
    for i in range(len(magnitudes)):
        for j in range(blocksize):
            strip.setPixelColor(i * blocksize + j, lighttools.wheel(magnitudes[i]) if magnitudes[i] > 32 else Color(0,0,0))
    strip.show()
    """
    
    """
    # Normalize so that the quietest maps to 0 and the loudest to 1. This is not good enough.
    cropped_fourier = fft.process(samples)
    cropped_fourier *= (1/max(cropped_fourier))

    ourcolours = [(rgb * intensity) for rgb, intensity in zip(rainbow.rgbs, cropped_fourier)]
    lighttools.setpixels(strip, ourcolours)
    """
    """
    previous_magnitudes = magnitudes
    magnitudes = np.array(gfilter.process(samples))
    diffs = magnitudes - previous_magnitudes
    if max(diffs) > 10**6: # magic
        dominant = diffs.argmax()
        primary = rainbow.colours[int(dominant * (strip.numPixels()/len(magnitudes)))]
        #pixels.insert(0, primary)
        pixels.append(primary) 
        if (len(pixels) > strip.numPixels()):
            pixels.pop(0)
        lighttools.setpixels(strip, pixels)
    """

print("* done recording")   
stream.stop_stream()
stream.close()
p.terminate()