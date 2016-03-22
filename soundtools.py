import math, pyaudio, struct
import numpy as np

class GoertzelFilter:
    """
    The Goertzel algorithm is more efficient than the Fast Fourier Transform at computing an 
    n-point DFT if less than 2 log2 n DFT coefficients are required.
    This one just returns the square of the relative magnitudes for simplicity
    """

    def __init__(self, sample_rate, chunk_size, target_freqs):        
        #precompute coefficients
        coeffs = []
        for target_freq in target_freqs:    
            k = int(0.5 + (chunk_size * target_freq) / sample_rate)
            omega = ((2 * math.pi) / chunk_size) * k
            #sin = math.sin(omega) # Not needed for real data
            cosine = math.cos(omega)
            coeffs.append(2 * cosine)
            
        self.coeffs = coeffs
        self.window = np.hamming(chunk_size)
    
    def process(self, samples):
        """
        Returns a list - one float per target frequency        
        """
        magnitudes = []
        # samples *= self.window # adds lag
        for coeff in self.coeffs:
        
            Q1 = Q2 = 0
            
            for sample in samples:
                Q0 = coeff * Q1 - Q2 + sample
                Q2 = Q1
                Q1 = Q0
            
            magnitude = (Q1**2 + Q2**2-Q1*Q2*coeff) # Real part only
            magnitudes.append(magnitude)
            #There's some sort of normalization we're meant to do here I imagine...
            # ^^ not true. frequency domain power is relative to time domain power, see notes.
        return magnitudes
    
class RealFourier:
    """
    real-number FFT that returns the specified number of intensity bins spanning a given frequency range
    rate: bitrate of source, int
    chunksize: chunk size of source, int
    range: lower and upper frequency bounds, integer tuple
    bins: How many bins to return, integer
    """
    
    def __init__(self, rate, chunksize, range, bins):

        
        # Integer maths
        
        low, high = range
        maxFreq = rate // 2 # Highest frequency detectable at this sample rate, max numpy fft will look for
        ourFreqsCount = high - low
        ourFreqProp = maxFreq/ourFreqsCount
        # The number of frequencies we'll need to run the FFT over to get the right number inside the range
        self.fidelity = 2 * int(bins * ourFreqProp) # There's more to it see numpy docs rfftfreq but works for us
        # Precompute the frequencies of the bins that the FFT will return
        freqs = (np.fft.rfftfreq(self.fidelity) * rate).astype(int) # Range 0 -> MAXFREQ step MAXFREQ/FFTFIDELITY
        
        self.bins = np.where(np.logical_and(freqs >= low, freqs < high )) # Find the indexes of the bins of interest
        self.freqs = freqs[self.bins] # And the frequencies they represent
        
        print("FFT initialized with {} bins from {} to {} Hz"
              .format(len(self.freqs), min(self.freqs), max(self.freqs)))

        self.window = np.hamming(chunksize) #, 14) #
        
    def process(self, samples):
        #samples *= self.window
        fourier = np.abs(np.fft.rfft(samples, self.fidelity))
        
        return(fourier[self.bins]) # Return the ones we're interested in

class chunksampler:
    """
    Reads samples from an audio stream and returns them in tuples    
    """
    def __init__(self, stream, chunksize):
        self.fmt = ('{}h').format(chunk)
        self.stream

    def getsamples(self):
        try:
            data = stream.read(chunk)
        except IOError as e:
            print("Audio input buffer overflow. Reduce bitrate or optimize...")
            return self.getsamples() # Have another bash...
        else:            
            samples = struct.unpack(self.fmt, data)
            return samples


                
def getsamples(stream, chunk):
    # try/catch because portIO throws an error if we're too slow.
	# We'll lose the full buffer but should be able to continue anyway.
    # portaudio patch somewhere on 'noodles to keep the full buffer...
    # TODO: objectify this shizzle so we can precreate the struct as soon as we know chunksize
    try:
        data = stream.read(chunk)
    except IOError as e:
        print("Audio input buffer overflow. Reduce bitrate or optimize...")
        return getsamples(stream, chunk) # Have another bash...
    else:        
        fmt = ('{}h').format(chunk) # we'll be getting n shorts at 2 bytes each
        samples = struct.unpack(fmt, data)
        return samples