# -*- coding: utf-8 -*-
# *****************************************************************************
# /////////////////////////////////////////////////////////////////////////////
# header begin-----------------------------------------------------------------
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
# *****************************************************************************
#
# __::((odmkSigGen1.py))::__
#
# Python Signal Generator
# optional CSV output
# optional .wav output
# optonal Spectral Plotting
#
# *****************************************************************************
# /////////////////////////////////////////////////////////////////////////////
# header end-------------------------------------------------------------------
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
# *****************************************************************************

import os
import csv
import wave
import numpy as np
import scipy as sp
import matplotlib.pyplot as plt

from odmkClear import *

# temp python debugger - use >>>pdb.set_trace() to set break
import pdb

# // *---------------------------------------------------------------------* //
clear_all()

# // *---------------------------------------------------------------------* //

print('// //////////////////////////////////////////////////////////////// //')
print('// *--------------------------------------------------------------* //')
print('// *---::ODMK Fourier Transforms::---*')
print('// *--------------------------------------------------------------* //')
print('// \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\ //')


# // *---------------------------------------------------------------------* //

print('\n')
print('// *--------------------------------------------------------------* //')
print('// *---::Basic Python/Scipy FFT test::---*')
print('// *--------------------------------------------------------------* //')


# Sampling Freq
Fs = 44100.0
# Number of sample points
N = 1024
# sample period
T = 1.0 / Fs

freqs = [5000.0, 7000.0]

# create composite sin source
x = np.linspace(0.0, N*T, N)
y = np.sin(freqs[0] * 2.0*np.pi*x) + 0.5*np.sin(freqs[1] * 2.0*np.pi*x)