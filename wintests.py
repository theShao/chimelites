import numpy as np
import matplotlib.pyplot as plt
import soundtools as st


volume = 0.5     # range [0.0, 1.0]
fs = 44100       # sampling rate, Hz, must be integer
duration = 1   # in seconds, may be float
notes = [440] #, 520]      # sine frequency, Hz, may be float
chunksize = 2044

# generate samples, note conversion to float32 array
samples = np.zeros(fs)
for note in notes:    
    samples += ((np.sin(2*np.pi*np.arange(fs*duration)*note/fs))*1000).astype(np.int)

x = np.arange(2000)
y = samples[0:2000]
plt.plot(x, y)
plt.show

gfilter = st.GoertzelFilter(fs, chunksize, np.array([440]))



for i in range(0, fs, chunksize):
    chunk = samples[i:i+chunksize]
    #print(chunk)
    sum_of_squares = 0.0
    for sample in chunk:
        sum_of_squares += sample*sample
    
    sum_of_magnitudes = gfilter.process(chunk)
    #print("Time domain sum-of-squares: ", sum_of_squares)
    #print("Freq domain sum-of-squares: ", sum_of_magnitudes)
    print("Ratio: ", [s_o_m/sum_of_squares for s_o_m in sum_of_magnitudes])
    