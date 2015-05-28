import math, pyaudio, struct
import numpy as np

class goertzelFilter:

    def __init__(self, sample_rate, chunk_size, target_freqs):
        self.window = np.hanning(chunk_size)
        #precompute coefficients
        coeffs = []
        for target_freq in target_freqs:    
            k = int(0.5 + (chunk_size * target_freq) / sample_rate)
            omega = ((2 * math.pi) / chunk_size) * k
            #sin = math.sin(omega) # Not needed for real data
            cosine = math.cos(omega)
            coeffs.append(2 * cosine)
            
        self.coeffs = coeffs
    
    def process(self, data):
        """
        Returns a list - one float per target frequency
        Implemented by Jim from the maths
        """
        magnitudes = []
        #data *= self.window  # Windowing slows down the response something terrible.
        for coeff in self.coeffs:
        
            Q1 = Q2 = 0
            
            for sample in data:
                Q0 = coeff * Q1 - Q2 + sample
                Q2 = Q1
                Q1 = Q0
            magnitude = math.sqrt(Q1**2 + Q2**2-Q1*Q2*coeff) # Real part only
            magnitudes.append(magnitude)
            
        # Normalize and ting    
        return magnitudes

    
class realFourier:
    
    def __init__(self, fidelity, rate, chunksize, range):    
        #Precompute the frequencies of the bins that the FFT will return
        #RFFT throws away negatives; for real data they mirror positives
        #Uniless, range 0 <= f < 0.5, multiply by bitrate for Hz
        # FFTFIDELITY = 2350 # aim for nice easy 1Hz steps. Or try and map to numpixels...
        low, high = range
        freqs = (np.fft.rfftfreq(fidelity) * rate).astype(int) # Range 0 -> MAXFREQ step MAXFREQ/FFTFIDELITY
        self.fidelity = fidelity
        self.bins = np.where(np.logical_and(freqs > low, freqs <= high )) # Find the indexes of the bins of interest
        self.freqs = freqs[self.bins] # And the frequencies they represent
        
        print("Searching for {} frequencies: {} ".format(len(self.freqs), self.freqs))

        self.window = np.blackman(chunksize) # More cowbell.
        
    def process(self, samples):
        samples *= self.window
        fourier = np.abs(np.fft.rfft(samples, self.fidelity))
        
        return(fourier[self.bins]) # Grab the ones we're interested in;
                
def getsamples(stream, chunk):
    # try/catch because portIO throws an error if we're too slow.
	# We'll lose the full bugffer but should be able to continue anyway.
    try:
        data = stream.read(chunk)
    except IOError as e:
        print("Buffer Overflow")
        return 0    
    structformat = ('{}h').format(chunk) # we'll be getting n shorts at 2 bytes each
    samples = struct.unpack(structformat, data)
    return samples
