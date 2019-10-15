"""
VISA Control: RSA AvT Transfer
Author: Morgan Allison
Date Created: 9/14
Date Edited: 1/17
This program transfers the Amplitude vs Time trace from the RSA to the 
computer and plots the results. 
Windows 7 64-bit, TekVISA 4.0.4
Python 3.6.0 64-bit (Anaconda 4.3.0)
MatPlotLib 2.0.0, PyVISA 1.8
To get PyVISA: pip install pyvisa
Download Anaconda: http://continuum.io/downloads
Anaconda includes MatPlotLib
Download SignalVu-PC programmer manual: http://www.tek.com/node/1828803
Download RSA5100B programmer manual: 
http://www.tek.com/spectrum-analyzer/inst5000-manual-7
Tested on RSA306B, RSA507A, and RSA5126B
"""


# IMPORTS ============================================================
import visa
import numpy as np
import matplotlib.pyplot as plt
import datetime


# CONNECT OT INSTRUMENT =====================================================
rm = visa.ResourceManager()
rsa = rm.open_resource('GPIB8::1::INSTR')
rsa.timeout = 10000
rsa.encoding = 'latin_1'
rsa.write_termination = None
rsa.read_termination = '\n'
print(rsa.query('*idn?'))
rsa.write('*rst')
rsa.write('*cls')


# INITIALIZE CONSTANTS ======================================================
# configure acquisition parameters
cf = 2.4453e9
span = 40e6
refLevel = -40
timeScale = 100e-6
timeOffset = 0
trigLevel = -50


# CONFIGURE INSTRUMENT ======================================================
# stop acquisitions while setting up instrument
rsa.write('abort')

# open spectrum, time overview, and amplitude vs time displays
rsa.write('display:general:measview:new spectrum')
rsa.write('display:general:measview:new toverview')
rsa.write('display:general:measview:new avtime')

# configure amplitude vs time measurement
rsa.write('spectrum:frequency:center {}'.format(cf))
rsa.write('spectrum:frequency:span {}'.format(span))
rsa.write('input:rlevel {}'.format(refLevel))
rsa.write('sense:avtime:span {}'.format(span))
rsa.write('sense:analysis:length {}'.format(timeScale))
rsa.write('sense:analysis:start {}'.format(timeOffset))

# configure power level trigger
rsa.write('trigger:event:input:type power')
rsa.write('trigger:event:input:level {}'.format(trigLevel))
rsa.write('initiate:continuous off')
rsa.write('trigger:status on')


# AQUIRE/PROCESS DATA =====================================================
# start acquisition
rsa.write('initiate:immediate')
rsa.query('*opc?')

# get raw amplitude vs time data from RSA
avt = rsa.query_binary_values('fetch:avtime:first?', datatype='f',
    container=np.array)

acqStart = float(rsa.query('display:avtime:x:scale:offset?'))
acqEnd = float(rsa.query('display:avtime:x:scale:full?'))
timeValues = np.linspace(acqStart,acqEnd, len(avt))


# PLOTS ===================================================================
# plot the data
plt.ioff()
fig = plt.figure(1, figsize=(20, 10))
ax = fig.add_subplot(111, facecolor='k')
ax.plot(timeValues, avt, 'y')
ax.set_title('Amplitude vs Time')
ax.set_ylabel('Amplitude (dBm)')
ax.set_xlabel('Time (s)')
ax.set_xlim(acqStart,acqEnd)


def logAndGraph(xAxis,yAxis):
    """
    Takes xAxis and yAxis to make a plot and log. It then saves
    the plot and log with a filename corresponding to its 
    timestamp.

    Precondition: len(xAxis) = len(yAxis)

    Parameters:
    xAxis : indexable : values you want on the xAxis
    yAxis : indexable : values you want on the xAxis
    """
    assert type(xAxis) == type(yAxis)
    assert len(xAxis) == len(yAxis)

    # Format Date
    date = datetime.datetime.today()
    date = str(date)
    pos = date.find('.')
    date = date[:pos]
    date = date.replace(" ","_")
    date = date.replace(":","-")
    date = date.replace(":","-")

    # Create filename for plot
    filenameG = date + ".png"
    filenameG = "Graphs/" + filenameG   
    plt.savefig(filenameG)              # Plot saved in directory named Graphs located 
                                        # in same directory as pyTekSA

    # Create filename for log
    filenameF = date + ".txt"
    filenameF = "Logs/" + filenameF     
    f = open(filenameF, "a+")           # Plot saved in directory named Logs located 
                                        # in same directory as pyTekSA

    # Fill log with contents
    for i in range(len(xAxis)):
        line = str(i) + ": " + str(xAxis[i]) + "\t" + str(yAxis[i])
        f.write(line)
        f.write('\n')

logAndGraph(timeValues,avt)
rm.close()
