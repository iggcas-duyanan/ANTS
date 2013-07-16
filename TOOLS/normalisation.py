import os as os
import numpy as np
import scipy as sp
from obspy.core import read
from obspy.core import trace
import obspy.signal as obs
import matplotlib.pyplot as plt

#==================================================================================================
# ONE-BIT NORMALISATION
#==================================================================================================

def onebit(data,verbose):

	"""
	Perform one-bit normalisation.
	"""

	if verbose==True: print '* one-bit normalisation'
	data.data=np.copysign(1, data.data)
	return data


#==================================================================================================
# RMS CLIPPING
#==================================================================================================

def clip(data,verbose):

	"""
	Clip data at their rms value.
	"""

	if verbose==True: print '* rms clipping'
	rms_amp=np.sqrt(np.mean(data.data*data.data))
	data.data=np.clip(data.data, -rms_amp, rms_amp )
	return data
    

#==================================================================================================
# MOVING AVERAGE NORMALISATION
#==================================================================================================

def ram_normal(data,window_length,verbose):

	"""
	Running average normalisation with window length in seconds. Divide data by running average.
	"""

	if verbose==True: print '* running average with '+str(window_length)+' s window'

	#- number of samples in the window, as a multiple of 2
	N=np.round(window_length/data.stats.delta)
	N=2*np.round(float(N)/2.0)

	#- make weighting array
	weightarray=np.convolve(abs(data.data), np.ones((window_length,))/window_length)
	weightarray=weightarray[(N/2-1):(N/2-1)+len(data.data)]

	#- normalise
	data.data=data.data/weightarray

	return data


#==================================================================================================
# MOVING AVERAGE NORMALISATION
#==================================================================================================

def waterlevel(data,level,verbose):

	"""
	Waterlevel normalisation. Iteratively clip data at a multiple of their rms value. 
	Continues until all data points are below that multiple of the rms amplitude.
	"""

	if verbose==True: print '* iterative clipping at '+str(level)+' times the rms value'

	rms_amp=np.sqrt(np.mean(data.data*data.data))
	while max(np.abs(data.data)) >= level*rms_amp:
		new_rms_amp=np.sqrt(np.mean(data.data*data.data))
		data.data=np.clip(data.data, -new_rms_amp, new_rms_amp )

	return data


#==================================================================================================
# SPECTRAL WHITENING
#==================================================================================================

def whiten(data,smoothing,verbose):

	"""
	Perform spectral whitening. The amplitude spectrum can be smoothed.
	"""

	if verbose==True: print '* spectral whitening'

	datarrayft=sp.fftpack.fft(data.data)
	datarrayft_smooth=obs.util.smooth(abs(datarrayft),smoothing)
	datarrayft=datarrayft/datarrayft_smooth
	data.data=np.real(sp.fftpack.ifft(datarrayft))

	return data


    

