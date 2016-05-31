# -*- coding: utf-8 -*-
# *****************************************************************************
# /////////////////////////////////////////////////////////////////////////////
# header begin-----------------------------------------------------------------
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
# *****************************************************************************
#
# __::((odmkPVx1_tb.py))::__
#
# Python testbench for odmkClocks, odmkSigGen1 objects
# required lib:
# odmkClocks ; odmkSigGen1
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

import odmkClocks as clks
import odmkSigGen1 as sigGen

# temp python debugger - use >>>pdb.set_trace() to set break
import pdb

# // *---------------------------------------------------------------------* //
clear_all()

# // *---------------------------------------------------------------------* //

print('// //////////////////////////////////////////////////////////////// //')
print('// *--------------------------------------------------------------* //')
print('// *---::ODMK Signal Generator 1::---*')
print('// *--------------------------------------------------------------* //')
print('// \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\ //')


# // *---------------------------------------------------------------------* //

# /////////////////////////////////////////////////////////////////////////////
# #############################################################################
# begin : function definitions
# #############################################################################
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\


# // *---------------------------------------------------------------------* //
# // *--Math Functions--*
# // *---------------------------------------------------------------------* //

def cyclicZn(n):
    ''' calculates the Zn roots of unity '''
    cZn = np.zeros((n, 1))*(0+0j)    # column vector of zero complex values
    for k in range(n):
        # z(k) = e^(((k)*2*pi*1j)/n)        # Define cyclic group Zn points
        cZn[k] = np.cos(((k)*2*np.pi)/n) + np.sin(((k)*2*np.pi)/n)*1j   # Euler's identity

    return cZn


# // *---------------------------------------------------------------------* //
# // *--Plot Functions--*
# // *---------------------------------------------------------------------* //

def odmkPlot1D(fnum, sig, xLin, pltTitle, pltXlabel, pltYlabel, lncolor='red', lnstyle='-', lnwidth=1.00, pltGrid=True, pltBgColor='black'):
    ''' ODMK 1D Matplotlib plot
        required inputs:
        fnum => unique plot number
        sig => signal to plot
        xLin => linear space to define x-axis (0 to max x-axis length-1)
        pltTitle => text string for plot title
        pltXlabel => text string for x-axis
        pltYlabel => text string for y-axis
        optional inputs:
        lncolor => line color (default = red ; html color names, html color codes??)
        lnstyle => line style (default = plain line ; * ; o ; etc..)
        lnwidth => line width
        pltGrid => use grid : default = True ; <True;False>
        pltBgColor => backgroud color (default = black) '''

    # Input signal
    plt.figure(num=fnum, facecolor='silver', edgecolor='k')
    # check if xLin is < than or = to sig
    if len(xLin) > len(sig):
        print('ERROR: length of xLin x-axis longer than signal length')
        return 1
    elif len(xLin) == len(sig):
        odmkMatPlt = plt.plot(xLin, sig)
    else:
        odmkMatPlt = plt.plot(xLin, sig[0:len(xLen)])

    plt.setp(odmkMatPlt, color=lncolor, ls=lnstyle, linewidth=lnwidth)
    plt.xlabel(pltXlabel)
    plt.ylabel(pltYlabel)
    plt.title(pltTitle)
    plt.grid(color='c', linestyle=':', linewidth=.5)
    plt.grid(pltGrid)
    # plt.xticks(np.linspace(0, Fs/2, 10))
    ax = plt.gca()
    ax.set_axis_bgcolor(pltBgColor)

    return 0
    
def odmkMultiPlot1D(fnum, sigArray, xLin, pltTitle, pltXlabel, pltYlabel, colorMp='gnuplot', lnstyle='-', lnwidth=1.00, pltGrid=True, pltBgColor='black'):
    ''' ODMK 1D Matplotlib multi-plot
        required inputs:
        fnum => unique plot number
        sig => signal to plot : 2D Numpy array
        xLin => linear space to define x-axis (0 to max x-axis length-1)
        pltTitle => text string for plot title
        pltXlabel => text string for x-axis
        pltYlabel => text string for y-axis
        optional inputs:
        lncolor => line color (default = red ; html color names, html color codes??)
        lnstyle => line style (default = plain line ; * ; o ; etc..)
        lnwidth => line width
        pltGrid => use grid : default = True ; <True;False>
        pltBgColor => backgroud color (default = black) '''

    # define the color map
    try:
        cmap = plt.cm.get_cmap(colorMp)
    except ValueError as e:
        print('ValueError: ', e)
    colors = cmap(np.linspace(0.0, 1.0, len(sigArray[0, :])))

    # Input signal
    plt.figure(num=fnum, facecolor='silver', edgecolor='k')
    # check if xLin is < than or = to sig
    if len(xLin) > len(sigArray[:, 0]):
        print('ERROR: length of xLin x-axis longer than signal length')
        return 1
    else:
        if len(xLin) == len(sigArray[:, 0]):
            # odmkMatPlt = []
            for i in range(len(sinArray[0, :])):
                plt.plot(xLin, sigArray[:, i], color=colors[i], ls=lnstyle, linewidth=lnwidth)
        else:
            # odmkMatPlt = []
            for i in range(len(sinArray[0, :])):
                plt.plot(xLin, sigArray[0:len(xLin), i], color=colors[i], ls=lnstyle, linewidth=lnwidth)

        plt.xlabel(pltXlabel)
        plt.ylabel(pltYlabel)
        plt.title(pltTitle)
        plt.grid(color='c', linestyle=':', linewidth=.5)
        plt.grid(pltGrid)
        # plt.xticks(np.linspace(0, Fs/2, 10))
        ax = plt.gca()
        ax.set_axis_bgcolor(pltBgColor)

    return 0


# // *---------------------------------------------------------------------* //
# // *--Phase Vocoder Functions--*
# // *---------------------------------------------------------------------* //

def odmkPVA(PVAin, SLength, Awin, NFFT, Ra, Fs):
    ''' odmk phase vocoder Analysis
        PVAin -> wave file / signal source in
        Awin -> phase vocoder analysis window (default = cos)
        PVAout -> phase vocoder output array <rows = bins, cols = frames>
        NFFT -> fft length
        Ra -> Analysis sample hop
        fs -> sampling frequency '''    
    
    print('\noriginal input signal length = '+str(SLength))
    # calculate zero-padded internal result buffer
    if SLength % Ra == 0:
        sigZpLength = 0
    else:
        sigZpLength = Ra - (SLength % Ra)    
    for k in range(sigZpLength):
        PVAin = np.append(PVAin, 0)

    newLength = len(PVAin)
    print('Zero padded signal length = '+str(newLength))        
    numFrame = int((newLength - (newLength % Ra))/Ra)
    print('Number of STFT output frames = '+str(numFrame)+'\n')

    # int posin, posout, i, k, mod;
    # float *sigframe, *specframe, *lastph;
    # float fac, scal, phi, mag, delta

    # input signal (real-only)
    sigframe = np.zeros(NFFT)
    # fft output spectrum (complex)
    specframe = np.zeros(NFFT)
    # array to hold phases from previous frame
    lastph = np.zeros(NFFT/2)

    specframe_mag = np.zeros(NFFT/2)
    specframe_ph = np.zeros(NFFT/2)

    fac = Fs / (Ra * 2*np.pi)
    scal = 2*np.pi * Ra/NFFT

    # PVAout = np.arange(2*NFFT/2*numFrame).reshape(2, NFFT/2, numFrame)
    PVAout = np.zeros((2,numFrame,NFFT/2))

    print('generating output PVAout, with dimensions: '+str(PVAout.shape)+'\n')

    frameIdx = 0
    # for(posin=posout=0; posin < input_size; posin+=hopsize):
    for j in range(0, newLength, Ra):
        mod = j % NFFT
        # window & rotate a signal frame
        for i in range(NFFT):
            if (j+i < newLength):
                sigframe[(i + mod) % NFFT] = PVAin[j + i] * Awin[i]
            else:
                sigframe[(i + mod) % NFFT] = 0

        # transform it
        specframe = sp.fft(sigframe)

        # convert to PV output (rectangular to polar)
        # specframe_mag[0] = dc (0 - phase)
        specframe_mag[0] = np.abs(specframe[0].real)
        # specframe_ph[0] = Nyquist (0 - phase)
        specframe_ph[0] = np.abs(specframe[int(NFFT/2)].real)
        for k in range(1, int(NFFT/2)):

            mag = sp.sqrt(specframe[k].real*specframe[k].real + specframe[k].imag*specframe[k].imag)
            phi = np.arctan2(specframe[k].imag, specframe[k].real)
            # phase diffs
            delta = phi - lastph[k]
            lastph[k] = phi

            # unwrap the difference, so it lies between -pi and pi
            while (delta > np.pi):
                delta -= 2 * np.pi
            while (delta < -np.pi):
                delta += 2 * np.pi

            # construct the amplitude-frequency pairs
            specframe_mag[k] = mag
            specframe_ph[k] = (delta + k * scal) * fac

        # pdb.set_trace()
        PVAout[0, frameIdx, :] = specframe_mag
        PVAout[1, frameIdx, :] = specframe_ph
        # PVAout[0][frameIdx] = specframe_mag
        # PVAout[1][frameIdx] = specframe_ph
        frameIdx += 1

    return PVAout


def odmkPVS(PVSin, SLength, Swin, NFFT, Rs, Fs):
    ''' odmk phase vocoder Synthesis
        PVSin -> PV formatted input data << np.array[2, numFrames, NFFT/2] >>
        Slength -> length of final output signal (matches original source)
        Swin -> phase vocoder synthesis window
        PVSout -> phase vocoder re-synthesized signal <time-domain>
        NFFT -> fft length
        Rs -> Synthesis sample hop
        fs -> sampling frequency '''

    # internal specframe length
    ILength = len(PVSin[0, 0, :])

    # input signal (real-only)
    sigframe = np.zeros(NFFT)
    # fft output spectrum (complex)
    specframe = np.zeros(NFFT, dtype=complex)
    # array to hold phases from previous frame
    lastph = np.zeros(NFFT/2)

    specframe_mag = np.zeros(NFFT/2)
    specframe_ph = np.zeros(NFFT/2)

    fac = Rs * 2*np.pi
    scal = Fs / NFFT
    
    PVSout = np.zeros((SLength))    # real only out

    frameIdx = 0
    # for(posin=posout=0; posin < input_size; posin+=hopsize):
    for j in range(0, ILength, Rs):
        # load in a spectral frame from input
        specframe_mag = PVSin[0, frameIdx, :]
        specframe_ph = PVSin[1, frameIdx, :]

        # convert from PV input to DFT coordinates

        specframe[0] = specframe_mag[0]
        specframe[NFFT/2] = specframe_ph[0]
        for k in range(1, int(NFFT/2)):

            delta = (specframe_ph[k] - k * scal) * fac
            phi = lastph[k] + delta
            lastph[k] = phi
            mag = specframe_mag[k]
            # polar-to-rectangular conversion (positive freqs)
            cmplxReal = mag * np.cos(phi)
            cmplxImag = mag * np.sin(phi)
            specframe[k] = np.complex(cmplxReal, cmplxImag)
            # re-construct negative frequencies
            specframe[NFFT-k] = np.complex(cmplxReal, -cmplxImag)

        # inverse-transform it
        sigframe = sp.ifft(specframe)

        # pdb.set_trace()

        # unrotate and window it and overlap-add it
        mod = j % NFFT
        for i in range(NFFT):
            if j + i < SLength:
                PVSout[j + i] += sigframe[(i + mod) % NFFT].real * Swin[i]

    return PVSout


#int pva(float *input, float *window, float *output, 
#        int input_size, int fftsize, int hopsize, float sr){
#
#int posin, posout, i, k, mod;
#float *sigframe, *specframe, *lastph;
#float fac, scal, phi, mag, delta, pi = (float)twopi/2;
#
#sigframe = new float[fftsize];
#specframe = new float[fftsize];
#lastph = new float[fftsize/2];
#memset(lastph, 0, sizeof(float)*fftsize/2);
#
#fac = (float) (sr/(hopsize*twopi));
#scal = (float) (twopi*hopsize/fftsize);
#
#for(posin=posout=0; posin < input_size; posin+=hopsize){
#      mod = posin%fftsize;
#	// window & rotate a signal frame
#      for(i=0; i < fftsize; i++) 
#          if(posin+i < input_size)
#            sigframe[(i+mod)%fftsize]
#                     = input[posin+i]*window[i];
#           else sigframe[(i+mod)%fftsize] = 0;
#
#      // transform it
#      fft(sigframe, specframe, fftsize);
#
#      // convert to PV output
#      for(i=2,k=1; i < fftsize; i+=2, k++){
#
#      // rectangular to polar
#      mag = (float) sqrt(specframe[i]*specframe[i] + 
#                        specframe[i+1]*specframe[i+1]);  
#      phi = (float) atan2(specframe[i+1], specframe[i]);
#      // phase diffs
#      delta = phi - lastph[k];
#      lastph[k] = phi;
#         
#      // unwrap the difference, so it lies between -pi and pi
#      while(delta > pi) delta -= (float) twopi;
#      while(delta < -pi) delta += (float) twopi;
#
#      // construct the amplitude-frequency pairs
#      specframe[i] = mag;
#	  specframe[i+1] = (delta + k*scal)*fac;
#
#      }
#      // output it
#      for(i=0; i < fftsize; i++, posout++)
#			  output[posout] = specframe[i];
#		  
#}
#delete[] sigframe;
#delete[] specframe;
#delete[] lastph;
#
#return posout;
#}


#int pvs(float* input, float* window, float* output,
#          int input_size, int fftsize, int hopsize, float sr){
#
#int posin, posout, k, i, output_size, mod;
#float *sigframe, *specframe, *lastph;
#float fac, scal, phi, mag, delta;
#
#sigframe = new float[fftsize];
#specframe = new float[fftsize];
#lastph = new float[fftsize/2];
#memset(lastph, 0, sizeof(float)*fftsize/2);
#
#output_size = input_size*hopsize/fftsize;
#
#fac = (float) (hopsize*twopi/sr);
#scal = sr/fftsize;
#
#for(posout=posin=0; posout < output_size; posout+=hopsize){ 
#
#   // load in a spectral frame from input 
#   for(i=0; i < fftsize; i++, posin++)
#        specframe[i] = input[posin];
#	
# // convert from PV input to DFT coordinates
# for(i=2,k=1; i < fftsize; i+=2, k++){
#   delta = (specframe[i+1] - k*scal)*fac;
#   phi = lastph[k]+delta;
#   lastph[k] = phi;
#   mag = specframe[i];
#  
#  specframe[i] = (float) (mag*cos(phi));
#  specframe[i+1] = (float) (mag*sin(phi)); 
#  
#}
#   // inverse-transform it
#   ifft(specframe, sigframe, fftsize);
#
#   // unrotate and window it and overlap-add it
#   mod = posout%fftsize;
#   for(i=0; i < fftsize; i++)
#       if(posout+i < output_size)
#          output[posout+i] += sigframe[(i+mod)%fftsize]*window[i];
#}
#delete[] sigframe;
#delete[] specframe;
#delete[] lastph;
#
#return output_size;
#}



# /////////////////////////////////////////////////////////////////////////////
# #############################################################################
# end : function definitions
# #############################################################################
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\


# /////////////////////////////////////////////////////////////////////////////
# #############################################################################
# begin : Loading & Formatting img and sound files
# #############################################################################
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\


rootDir = 'C:/usr/eschei/odmkPython/odmk/werk/'


print('\n')
print('// *--------------------------------------------------------------* //')
print('// *---::Set Master Parameters for output::---*')
print('// *--------------------------------------------------------------* //')


# // *---------------------------------------------------------------------* //
# // *--Primary parameters--*
# // *---------------------------------------------------------------------* //

# length of x in seconds:
xLength = 1

# audio sample rate:
fs = 44100.0

# sample period
T = 1.0 / fs

# audio sample bit width
bWidth = 24

# video frames per second:
framesPerSec = 30.0

bpm = 133.0

# time signature: 0 = 4/4; 1 = 3/4
timeSig = 0


print('\n')
print('// *--------------------------------------------------------------* //')
print('// *---::Instantiate clock & signal Generator objects::---*')
print('// *--------------------------------------------------------------* //')

tbClocks = clks.odmkClocks(xLength, fs, bpm, framesPerSec)

numSamples = tbClocks.totalSamples

tbSigGen = sigGen.odmkSigGen1(numSamples, fs)

# // *---------------------------------------------------------------------* //

tbQtrBar = tbClocks.clkQtrBar()
tbQtrBar5 = tbClocks.clkQtrBar(nBar=5)


print('\n')
print('// *--------------------------------------------------------------* //')
print('// *---::Generate source waveforms::---*')
print('// *--------------------------------------------------------------* //')


print('\n::Mono Sine waves::')
print('generated mono sin signals @ 2.5K and 5K Hz')
# generate simple mono sin waves
testFreq1 = 2500.0
testFreq2 = 5000.0

sin2_5K = tbSigGen.monosin(testFreq1)
sin5K = tbSigGen.monosin(testFreq2)

# // *---------------------------------------------------------------------* //

print('\n::Multi Sine source::')
print('generated array of sin signals "sinArray"')
testFreqs = [666.0, 777.7, 2300.0, 6000.0, 15600.0]
numFreq = len(testFreqs)

print('Frequency Array (Hz):')
print(testFreqs)

sinArray = np.array([])
for freq in testFreqs:
    sinArray = np.concatenate((sinArray, tbSigGen.monosin(freq)))
sinArray = sinArray.reshape((numFreq, numSamples))
sinArray = sinArray.transpose()

# // *---------------------------------------------------------------------* //

# generate a set of orthogonal frequencies

print('\n::Orthogonal Multi Sine source::')
print('generated array of orthogonal sin signals "orthoSinArray"')

# for n freqs, use 2n+1 => skip DC and negative freqs!
# ex. for cyclicZn(15), we want to use czn[1, 2, 3, ... 7]

numOrthoFreq = 7
czn = cyclicZn(2*numOrthoFreq + 1)

orthoFreqArray = np.array([])
for c in range(1, numOrthoFreq+1):
    cznph = np.arctan2(czn[c].imag, czn[c].real)
    cznFreq = (fs*cznph)/(2*np.pi)
    orthoFreqArray = np.append(orthoFreqArray, cznFreq)

print('Orthogonal Frequency Array (Hz):')
print(orthoFreqArray)

orthoSinArray = np.array([])
for freq in orthoFreqArray:
    orthoSinArray = np.concatenate((orthoSinArray, tbSigGen.monosin(freq)))
orthoSinArray = orthoSinArray.reshape((numOrthoFreq, numSamples))
orthoSinArray = orthoSinArray.transpose()


# // *---------------------------------------------------------------------* //

print('\n')
print('// *--------------------------------------------------------------* //')
print('// *---::Check source waveform spectrum::---*')
print('// *--------------------------------------------------------------* //')

# FFT length for source waveform spectral analysis (tb, unrelated to PV)
N = 2048

# // *---------------------------------------------------------------------* //

y1 = sin2_5K[0:10000]
y2 = sin5K[0:10000]

# forward FFT
y1_FFT = sp.fft(y1[0:N])
y1_Mag = np.abs(y1_FFT)
y1_Phase = np.arctan2(y1_FFT.imag, y1_FFT.real)
# scale and format FFT out for plotting
y1_FFTscale = 2.0/N * np.abs(y1_FFT[0:N/2])

y2_FFT = sp.fft(y2[0:N])
y2_Mag = np.abs(y2_FFT)
y2_Phase = np.arctan2(y2_FFT.imag, y2_FFT.real)
# scale and format FFT out for plotting
y2_FFTscale = 2.0/N * np.abs(y2_FFT[0:N/2])

# inverse FFT
y1_IFFT = sp.ifft(y1_FFT)

y2_IFFT = sp.ifft(y2_FFT)

# check
yDiff = y2_IFFT - y2[0:N]

# // *---------------------------------------------------------------------* //

# ::sinArray::

yArray = np.array([])
yMagArray = np.array([])
yPhaseArray = np.array([])
yScaleArray = np.array([])
# for h in range(len(sinArray[0, :])):
for h in range(numFreq):    
    yFFT = sp.fft(sinArray[0:N, h])
    yArray = np.concatenate((yArray, yFFT))
    yScaleArray = np.concatenate((yScaleArray, 2.0/N * np.abs(yFFT[0:N/2])))
#    yMagArray = np.concatenate((yMagArray, np.abs(yFFT)))    
#    yPhaseArray = np.concatenate((yPhaseArray, np.arctan2(yFFT.imag, yFFT.real)))

yArray = yArray.reshape((numFreq, N))
yArray = yArray.transpose()

yScaleArray = yScaleArray.reshape((numFreq, N/2))
yScaleArray = yScaleArray.transpose()

# yMagArray = yMagArray.reshape((numFreqs, N))
# yMagArray = yMagArray.transpose()

# yPhaseArray = yPhaseArray.reshape((numFreqs, N))
# yPhaseArray = yPhaseArray.transpose()

# // *---------------------------------------------------------------------* //

# ::orthoSinArray::

yOrthoArray = np.array([])
yOrthoMagArray = np.array([])
yOrthoPhaseArray = np.array([])
yOrthoScaleArray = np.array([])
# for h in range(len(sinArray[0, :])):
for h in range(numOrthoFreq):
    yOrthoFFT = sp.fft(orthoSinArray[0:N, h])
    yOrthoArray = np.concatenate((yOrthoArray, yOrthoFFT))
    yOrthoScaleArray = np.concatenate((yOrthoScaleArray, 2.0/N * np.abs(yOrthoFFT[0:N/2])))

yOrthoArray = yOrthoArray.reshape((numOrthoFreq, N))
yOrthoArray = yOrthoArray.transpose()

yOrthoScaleArray = yOrthoScaleArray.reshape((numOrthoFreq, N/2))
yOrthoScaleArray = yOrthoScaleArray.transpose()

# // *---------------------------------------------------------------------* //

print('\n')
print('// *--------------------------------------------------------------* //')
print('// *---::Main - Phase Vocoder Begin::---*')
print('// *--------------------------------------------------------------* //')

sigLength = 4096

NFFT = 64

Ra = int(NFFT/4)
Rs = int(NFFT/4)

PVAin = y2[0:sigLength]

Awin = np.blackman(NFFT)
Swin = np.blackman(NFFT)

print('\nodmkPVA function call using the following parameters:')
print('PV NFFT = '+str(NFFT))
print('PV Analysis Hop = '+str(Ra)+' (samples)\n')

PVAout = odmkPVA(PVAin, sigLength, Awin, NFFT, Ra, fs)

PVSout = odmkPVS(PVAout, sigLength, Swin, NFFT, Rs, fs)



# // *---------------------------------------------------------------------* //

# // *---------------------------------------------------------------------* //
# // *---Mono FFT plots---*
# // *---------------------------------------------------------------------* //

# define a sub-range for wave plot visibility
tLen = 50

fnum = 1
pltTitle = 'Input Signal y1 (first '+str(tLen)+' samples)'
pltXlabel = 'y1: '+str(testFreq1)+' Hz'
pltYlabel = 'Magnitude'


sig = y1[0:tLen]
# define a linear space from 0 to 1/2 Fs for x-axis:
xaxis = np.linspace(0, tLen, tLen)


odmkPlot1D(fnum, sig, xaxis, pltTitle, pltXlabel, pltYlabel)


fnum = 2
pltTitle = 'Scipy FFT Mag: y1_FFTscale '+str(testFreq1)+' Hz'
pltXlabel = 'Frequency: 0 - '+str(fs / 2)+' Hz'
pltYlabel = 'Magnitude (scaled by 2/N)'

# sig <= direct

# define a linear space from 0 to 1/2 Fs for x-axis:
xfnyq = np.linspace(0.0, 1.0/(2.0*T), N/2)

odmkPlot1D(fnum, y1_FFTscale, xfnyq, pltTitle, pltXlabel, pltYlabel)


# // *---------------------------------------------------------------------* //
# // *---Multi Plot - source signal array vs. FFT MAG out array---*
# // *---------------------------------------------------------------------* //

fnum = 3
pltTitle = 'Input Signals: sinArray (first '+str(tLen)+' samples)'
pltXlabel = 'sinArray time-domain wav'
pltYlabel = 'Magnitude'

# define a linear space from 0 to 1/2 Fs for x-axis:
xaxis = np.linspace(0, tLen, tLen)

odmkMultiPlot1D(fnum, sinArray, xaxis, pltTitle, pltXlabel, pltYlabel, colorMp='gnuplot')


fnum = 4
pltTitle = 'FFT Mag: yScaleArray multi-osc '
pltXlabel = 'Frequency: 0 - '+str(fs / 2)+' Hz'
pltYlabel = 'Magnitude (scaled by 2/N)'

# define a linear space from 0 to 1/2 Fs for x-axis:
xfnyq = np.linspace(0.0, 1.0/(2.0*T), N/2)

odmkMultiPlot1D(fnum, yScaleArray, xfnyq, pltTitle, pltXlabel, pltYlabel, colorMp='gnuplot')


# // *---------------------------------------------------------------------* //
# // *---Orthogonal Sine Plot - source signal array vs. FFT MAG out array---*
# // *---------------------------------------------------------------------* //

fnum = 5
pltTitle = 'Input Signals: orthoSinArray (first '+str(tLen)+' samples)'
pltXlabel = 'orthoSinArray time-domain wav'
pltYlabel = 'Magnitude'

# define a linear space from 0 to 1/2 Fs for x-axis:
xaxis = np.linspace(0, tLen, tLen)

odmkMultiPlot1D(fnum, orthoSinArray, xaxis, pltTitle, pltXlabel, pltYlabel, colorMp='gnuplot')


fnum = 6
pltTitle = 'FFT Mag: yOrthoScaleArray multi-osc '
pltXlabel = 'Frequency: 0 - '+str(fs / 2)+' Hz'
pltYlabel = 'Magnitude (scaled by 2/N)'

# define a linear space from 0 to 1/2 Fs for x-axis:
xfnyq = np.linspace(0.0, 1.0/(2.0*T), N/2)

odmkMultiPlot1D(fnum, yOrthoScaleArray, xfnyq, pltTitle, pltXlabel, pltYlabel, colorMp='hsv')


# // *---------------------------------------------------------------------* //
# // *---STFT Analysis Window - COLA test---*
# // *---------------------------------------------------------------------* //

colaNum = 4
colaLength = colaNum*Ra + (len(Awin) - Ra)

pvAwinShft = np.array([])
pvAwinSum = np.array([])
pvAwinCOLA = np.array([])

for z in range(0, colaNum*Ra, Ra):
    if z == 0:
        pvAwinShft = np.append(Awin, np.zeros(colaLength - len(Awin)))
        pvAwinSum = pvAwinShft
    else:
        pvAwinShft = np.append(np.zeros(z), Awin)
        pvAwinShft = np.append(pvAwinShft, np.zeros(colaLength - (z + len(Awin))))
        pvAwinSum = pvAwinSum + pvAwinShft
    pvAwinCOLA = np.concatenate((pvAwinCOLA, pvAwinShft))

pvAwinCOLA = np.concatenate((pvAwinCOLA, pvAwinSum))
pvAwinCOLA = pvAwinCOLA.reshape((colaNum + 1, colaLength))
pvAwinCOLA = pvAwinCOLA.transpose()

fnum = 200
pltTitle = 'PV Analysis window Cola test:'
pltXlabel = 'time'
pltYlabel = 'Amplitude'

# define a linear space from 0 to 1/2 Fs for x-axis:
xaxis = np.linspace(0, colaLength, colaLength)

odmkMultiPlot1D(fnum, pvAwinCOLA, xaxis, pltTitle, pltXlabel, pltYlabel, colorMp='hsv')


# // *---------------------------------------------------------------------* //
# // *---STFT Magnitude plot (1 frame)---*
# // *---------------------------------------------------------------------* //

fnum = 100
pltTitle = 'Scipy PV Mag: PVAout (1 frame) '+str(testFreq2)+' Hz'
pltXlabel = 'Frequency: 0 - '+str(fs / 2)+' Hz'
pltYlabel = 'Magnitude (scaled by 2/N)'

# sig <= direct

# define a linear space from 0 to 1/2 Fs for x-axis:
xfnyq = np.linspace(0.0, 1.0/(2.0*T), NFFT/2)

odmkPlot1D(fnum, PVAout[0, 11, :], xfnyq, pltTitle, pltXlabel, pltYlabel)

# // *---------------------------------------------------------------------* //
# // *---STFT Magnitude plot (All frame)---*
# // *---------------------------------------------------------------------* //

pvWaterfall = np.array([])

for j in range(len(PVAout[0,:,0])):
     pvWaterfall = np.concatenate((pvWaterfall, PVAout[0, j, :]))
pvWaterfall = pvWaterfall.reshape((len(PVAout[0,:,0]), len(PVAout[0,0,:])))     
pvWaterfall = pvWaterfall.transpose()
     
fnum = 101
pltTitle = 'Scipy PV Mag: PVAout (All frame) '+str(testFreq2)+' Hz'
pltXlabel = 'Frequency: 0 - '+str(fs / 2)+' Hz'
pltYlabel = 'Magnitude (scaled by 2/N)'

# sig <= direct

# define a linear space from 0 to 1/2 Fs for x-axis:
xfnyq = np.linspace(0.0, 1.0/(2.0*T), NFFT/2)

odmkMultiPlot1D(fnum, pvWaterfall, xfnyq, pltTitle, pltXlabel, pltYlabel, colorMp='Spectral')



# // *---------------------------------------------------------------------* //
# // *---STFT Spectrogram Plot??---*
# // *---------------------------------------------------------------------* //

result = PVAout[0]

result = 20*np.log10(result)          # scale to db
result = np.clip(result, -40, 200)    # clip values



# // *---------------------------------------------------------------------* //

plt.show()

print('\n')
print('// *--------------------------------------------------------------* //')
print('// *---::done::---*')
print('// *--------------------------------------------------------------* //')

# // *---------------------------------------------------------------------* //
