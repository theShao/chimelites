import numpy as np
import lighttools, soundtools

CHIME_FREQUENCIES = np.array((439,493,521,587,655,697,781,874)) # Taken with Cleartune from the chimes.
# 440,491,521,586,655,691,780,866 short set 1
TOP_NOTE = 144
BOTTOM_NOTE = 0

TRIGGER = (8 * 10**5)**2

#
# Time domain to frequency domain energy ratios: http://www.dsprelated.com/showthread/comp.dsp/77366-1.php
# 


class RainbowFFT:
    """Colours determined by Sarah's rainbow numbers, intensity from FFT, one bin per pixel"""
    def __init__(self, bitrate, chunksize, numpixels):
        # Generate the rainbow array
        rainbow = lighttools.sarahs_colours(numpixels)
        self.colours = [rainbow.getRGB(position) for position in range(numpixels)]
        self.fft = soundtools.RealFourier(bitrate, chunksize, (BOTTOM_NOTE, TOP_NOTE), numpixels)

    def process(self, samples):
        # Do the FFT run
        cropped_fourier = self.fft.process(samples)
        # Normalize so that the quietest maps to 0 and the loudest to 1. This is not good enough.
        cropped_fourier *= (1/max(cropped_fourier))
        # Map fourier results as intensity onto rainbow colours
        ourcolours = [(rgb * intensity)
                     if intensity > 0.5 else 0 
                     for rgb, intensity in zip(self.colours, cropped_fourier)]
        
        return ourcolours

class ClusterFFT:
    """Colours determined by Sarah's rainbow numbers, intensity from FFT, one bin per cluster of pixels"""
    clusters = 32
    weightings = [1, 1, 2, 2, 2, 4, 4, 8, 8, 8, 8, 8, 8,
                  16, 16, 16, 16, 16, 16, 16, 16, 16, 16,
                  32, 32, 32, 32, 32, 64, 64, 64, 64] # "Adjust to taste..."
    def __init__(self, bitrate, chunksize, numpixels):
        # Generate the rainbow array
        self.spectrum = lighttools.sarahs_colours().rgbs
        self.spectrum = self.spectrum[::int(len(self.spectrum)/ClusterFFT.clusters)]
        #self.gfilter = soundtools.goertzelFilter(bitrate, chunksize, CHIME_FREQUENCIES)
        self.fft = soundtools.RealFourier(bitrate, chunksize, (BOTTOM_NOTE, TOP_NOTE), ClusterFFT.clusters) #numpixels

    def process(self, samples):
        # Do the FFT run
        cropped_fourier = self.fft.process(samples) * ClusterFFT.weightings
        # Normalize so that the quietest maps to 0 and the loudest to 1. This is not good enough.
        cropped_fourier *= ((1/max(cropped_fourier))) #*(len(self.spectrum)-1))
        # Map fourier results as intensity onto rainbow colours
        #print(cropped_fourier)
        # ourcolours = [self.spectrum[int(freq)] if freq > 5 else (0,0,0) for freq in cropped_fourier]
        
        ourcolours = [(rgb * intensity)
                     if intensity > 0.25 else 0 
                     for rgb, intensity in zip(self.spectrum , cropped_fourier)]
        
        return ourcolours

class ClusterFFT2:
    """Colours determined by Sarah's rainbow numbers, intensity from FFT, one bin per cluster of pixels"""
    clusters = 8
    def __init__(self, bitrate, chunksize, numpixels):
        # Generate the rainbow array
        spectrum = lighttools.sarahs_colours().rgbs
        self.spectrum =spectrum[::int(len(spectrum)/ClusterFFT.clusters)]
        #self.gfilter = soundtools.goertzelFilter(bitrate, chunksize, CHIME_FREQUENCIES)
        self.fft = soundtools.RealFourier(bitrate, chunksize, (BOTTOM_NOTE, TOP_NOTE), ClusterFFT.clusters) #numpixels

    def process(self, samples):
        # Do the FFT run
        cropped_fourier = self.fft.process(samples)
        # Normalize so that the quietest maps to 0 and the loudest to 1. This is not good enough.
        cropped_fourier *= (1/max(cropped_fourier))
        # Map fourier results as intensity onto rainbow colours
        ourcolours = [(rgb * intensity)
                     #if intensity > 0.25 else 0 
                     for rgb, intensity in zip(self.spectrum , cropped_fourier)]
        
        return ourcolours

class FastProgress:
    # Repeats the colour of the last detected note, moves at bitrate/chunk leds per second
    def __init__(self, bitrate, chunksize, numpixels):
        # Generate the rainbow array
        self.rainbow = lighttools.sarahs_colours()        
        self.gfilter = soundtools.GoertzelFilter(bitrate, chunksize, CHIME_FREQUENCIES)
        #self.fft = soundtools.realFourier(bitrate, chunksize, (BOTTOM_NOTE, TOP_NOTE), numpixels)
        self.magnitudes = np.zeros(8)
        self.primary = lighttools.BLACK # Initial colour before detections
        self.pixels = [0 for _ in range(numpixels)] # Prepopulate

    def process(self, samples):
        previous_magnitudes = self.magnitudes    
        self.magnitudes = np.array(self.gfilter.process(samples))
        deltas = self.magnitudes - previous_magnitudes
        if max(deltas) > TRIGGER:
            dominant = deltas.argmax()
            self.primary = self.rainbow.getRGB(int(dominant * (len(self.pixels)/len(self.magnitudes))))

        self.pixels.insert(0, self.primary)
        self.piDSxels.pop()
        return self.pixels

class Tracer:
    """ Adds a colour if a note's over the threshold, otherwise add a black pixel
    """
    def __init__(self, bitrate, chunksize, numpixels):
        self.colours = [np.array(rgb) for rgb in [(255, 0, 0), (255, 128, 0), (255, 255, 0), (2, 255, 0), (0, 255, 255), (0, 0, 255), (128, 0, 255), (255, 0, 128)]]
        self.gfilter = soundtools.GoertzelFilter(bitrate, chunksize, CHIME_FREQUENCIES)
        self.pixels = [0 for _ in range(numpixels)] # Prepopulate

    def process(self, samples):
        magnitudes = np.array(self.gfilter.process(samples))
        amp_power = sum(sample**2 for sample in samples)        
        freq_powers = [int(freq_power/amp_power) for freq_power in magnitudes]

        primary = (lighttools.BLACK_RGB if max(freq_powers) < 20
                   else self.colours[np.argmax(freq_powers)])

        self.pixels.insert(0, primary)
        self.pixels.pop()
        return self.pixels

class Filler:
    """ Adds a colour if a note's over the threshold
    """
    def __init__(self, bitrate, chunksize, numpixels):
        self.colours = [np.array(rgb) for rgb in [(255, 0, 0), (255, 128, 0), (255, 255, 0), (2, 255, 0), (0, 255, 255), (0, 0, 255), (128, 0, 255), (255, 0, 128)]]
        self.gfilter = soundtools.GoertzelFilter(bitrate, chunksize, CHIME_FREQUENCIES)
        self.pixels = [0 for _ in range(numpixels)] # Prepopulate

    def process(self, samples):
        magnitudes = np.array(self.gfilter.process(samples))
        amp_power = sum(sample**2 for sample in samples)        
        freq_powers = [int(freq_power/amp_power) for freq_power in magnitudes]
        max_power = max(freq_powers)
        max_index = np.argmax(freq_powers)
        
        primary = (self.colours[max_index]  * (max_power/500) if max_power < 500
                    else self.colours[max_index])
        self.pixels.insert(0, primary)
        self.pixels.pop()

        return self.pixels

"""
class SlowProgress:
    # Adds an LED of the note's colour on each detection
    def __init__(self, bitrate, chunksize, numpixels):
        # Generate the rainbow array
        self.rainbow = lighttools.sarahs_colours()        
        self.gfilter = soundtools.GoertzelFilter(bitrate, chunksize, CHIME_FREQUENCIES)
        #self.fft = soundtools.realFourier(bitrate, chunksize, (BOTTOM_NOTE, TOP_NOTE), numpixels)
        self.magnitudes = np.zeros(8)
        self.pixels = [0 for _ in range(numpixels)] # Prepopulate

    def process(self, samples):
        previous_magnitudes = self.magnitudes    
        self.magnitudes = np.array(self.gfilter.process(samples))
        deltas = self.magnitudes - previous_magnitudes
        if max(deltas) > TRIGGER:
            dominant = deltas.argmax()
            primary = self.rainbow.colours[int(dominant * (len(self.pixels)/len(self.magnitudes)))]
            self.pixels.insert(0, primary)
            self.pixels.pop()
        return self.pixels
"""

class Flasher:
    # Adds an LED of the note's colour on each detection  and flashes the colour
    def __init__(self, bitrate, chunksize, numpixels):
        # Generate the rainbow array
        self.rainbow = lighttools.sarahs_colours()        
        self.gfilter = soundtools.GoertzelFilter(bitrate, chunksize, CHIME_FREQUENCIES)
        #self.fft = soundtools.realFourier(bitrate, chunksize, (BOTTOM_NOTE, TOP_NOTE), numpixels)
        self.magnitudes = np.zeros(8)
        self.pixels = [0 for _ in range(numpixels)] # Prepopulate

    def process(self, samples):
        previous_magnitudes = self.magnitudes    
        self.magnitudes = np.array(self.gfilter.process(samples))
        deltas = self.magnitudes - previous_magnitudes
        if max(deltas) > TRIGGER:
            dominant = deltas.argmax()
            primary = self.rainbow.colours[int(dominant * (len(self.pixels)/len(self.magnitudes)))]
            #self.pixels.insert(0, primary)
            #self.pixels.pop()
            return [primary] * len(self.pixels)
        return self.pixels

class ColourBlocks:
    # Split strip into n chunks, n = number of notes. Colours are on or off.
    def __init__(self, bitrate, chunksize, numpixels):
        
        self.rainbow = lighttools.sarahs_colours()  # Generate the rainbow array
        self.gfilter = soundtools.GoertzelFilter(bitrate, chunksize, CHIME_FREQUENCIES) # Initialize the filter
        self.magnitudes = np.zeros(len(CHIME_FREQUENCIES)) # Keep this as an instance variable so we can track deltas
        self.blocksize = int(numpixels/len(CHIME_FREQUENCIES)) # Only doing this so we can find the colour, duplicates effort

    def process(self, samples):
        previous_magnitudes = self.magnitudes    
        self.magnitudes = np.array(self.gfilter.process(samples))
        deltas = self.magnitudes - previous_magnitudes
        colours = [self.rainbow.getColour(index * self.blocksize) 
                       if delta > TRIGGER else lighttools.BLACK
                       for index, delta in enumerate(deltas)]
        return colours



class DO_TestG:
    """ Adds a colour if a note's over the threshold, otherwise add a black pixel"""
    def __init__(self, bitrate, chunksize, numpixels):
        # Generate the rainbow array
        #self.colours = [lighttools.wheel_RGB(freq, len(CHIME_FREQUENCIES)) for freq in range(len(CHIME_FREQUENCIES))]
        self.rainbow = lighttools.sarahs_colours(numpixels)
        blocksize = int(numpixels/len(CHIME_FREQUENCIES)) # Only doing this so we can find the colour, duplicates effort    
        self.colours = [self.rainbow.getRGB(freq*blocksize) for freq in range(len(CHIME_FREQUENCIES))]
        self.gfilter = soundtools.GoertzelFilter(bitrate, chunksize, CHIME_FREQUENCIES)        

    def process(self, samples):     
        self.magnitudes = np.array(self.gfilter.process(samples))

        amp_power = sum(sample**2 for sample in samples)
        #freq_power = sum(self.magnitudes)
        #print("amplitudes: ", amp_power)
        #print("frequencies: ", freq_power)
        #print(self.magnitudes)
        relative_powers = [int(freq_p/amp_power) for freq_p in self.magnitudes]
        #print(relative_powers)
        #print(self.colours)
        colours = [lighttools.BLACK if power < 35 
                   else self.colours[index] * (power/500) if power < 500 
                   else self.colours[index]
                for index, power in enumerate(relative_powers)]
        return colours

class TestG2:
    """ Adds a colour if a note's over the threshold, otherwise add a black pixel"""
    def __init__(self, bitrate, chunksize, numpixels):
        # Generate the rainbow array
        self.rainbow = lighttools.sarahs_colours(numpixels)
        self.clustersize = int(numpixels/len(CHIME_FREQUENCIES))
        self.gfilter = soundtools.GoertzelFilter(bitrate, chunksize, CHIME_FREQUENCIES)        

    def process(self, samples):     
        self.magnitudes = np.array(self.gfilter.process(samples))

        amp_power = sum(sample**2 for sample in samples)
        relative_powers = [int(freq_p/amp_power) for freq_p in self.magnitudes]
        
        colours = []
        i = 0
        for power in relative_powers:
            j = 0
            for led in range(self.clustersize):
                index = i * self.clustersize + j
                colour = (lighttools.BLACK if power < 35 
                       else self.rainbow.getRGB(index) * (power/500) if power < 500 
                       else self.rainbow.getRGB(index))           
                colours.append(colour)          
                j += 1
            i += 1      
        return colours

class testcolours:
    def __init__(self, bitrate, chunksize, numpixels):
        pass

    def process(self, samples):
        return([lighttools.Color(100, 10, 10)])


