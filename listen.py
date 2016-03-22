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
import threading, itertools, time, inspect
import pyaudio
# import BrickPi # Communication with Lego NXT and EV3 sensors and motors
import soundtools, lighttools, programs
from neopixel import * # TODO: Get shot of this...
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)

GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Set up the pin we'll be using for the pushswitch


RUNNING = True

# LED strip configuration:
LED_COUNT      = 72     # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 11      # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 128      # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)

# pyAudio configuration.
CHUNK = 756             # Samples
FORMAT = pyaudio.paInt16 # binary-packed 2-byte shorts
CHANNELS = 1
RATE = 22100             # Samples per second
MAXFREQ = RATE//2        # Highest freq it's possible to detect at this sample rate
MINFREQ = RATE/CHUNK # simply not true... 

# Set up audio stream first; ALSA spams the output
stream = pyaudio.PyAudio().open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

"""
# BrickPi setup for lego sensors
BrickPi.BrickPiSetup()  # setup the serial port for communication
BrickPi.BrickPi.SensorType[BrickPi.PORT_1] = BrickPi.TYPE_SENSOR_TOUCH   #Set the type of sensor at PORT_1
BrickPi.BrickPiSetupSensors()   #Send the properties of sensors to BrickPi
"""

# Set up LED strip
print("Seting up LED strip with {} LEDs".format(LED_COUNT))
strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)
strip.begin()

# Flash some colours to show it's working
lighttools.test(strip)
time.sleep(0.5)
lighttools.clear(strip)

# Find and initialize all the classes in the programs module
print("Initializing programs")
programs = [program(RATE, CHUNK, LED_COUNT) 
            for name, program in inspect.getmembers(programs) 
            if inspect.isclass(program)
            and name[:3] == "DO_"]
program_cycle = itertools.cycle(programs) # Loop through them forever
current_program = next(program_cycle)

# Thread listening for button press
print("Starting button listener thread")
def button_listener(button_pressed):
    while RUNNING:
        if not GPIO.input(26):
            button_pressed.append(None)
            time.sleep(0.5)
        """
        if not button_pressed: # Don't queue them up.
            result = BrickPi.BrickPiUpdateValues() # Returns 0 on success
            if not result:
                if BrickPi.BrickPi.Sensor[BrickPi.PORT_1]: # True if button is pressed
                    button_pressed.append(None)
                    time.sleep(0.5)
        """
        time.sleep(0.1)

button_pressed = []
listener_thread = threading.Thread(target=button_listener, args = (button_pressed,))
listener_thread.start()

print("Listening...")

while True:
    try:
        if button_pressed: # Move on to the next program
            button_pressed.pop()
            print("Tick")
            current_program = next(program_cycle)
        
        samples = soundtools.getsamples(stream, CHUNK) # Grab a chunk
        pixels = current_program.process(samples) # As the programs what pixels to show
        lighttools.setpixels(strip, pixels, True) # Send them to the led manager
    except KeyboardInterrupt as e:
        print("Closing...")
        RUNNING = False 
        stream.stop_stream()
        stream.close()
        break