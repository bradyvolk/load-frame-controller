"""
VISA Control: RSA AvT Transfer
Author: Morgan Allison
Edited: Brady Volkmann
Date Created: 9/14
Date Edited: 6/20/2019
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

# IMPORTS ===================================================================
import visa
import numpy as np
import matplotlib.pyplot as plt
import datetime

# CONNECT OT INSTRUMENT =====================================================
rm = visa.ResourceManager()
rm.list_resources()
ttr = rm.open_resource('GPIB8::1::INSTR')
ttr.timeout = 10000
ttr.encoding = 'latin_1'
ttr.write_termination = None
ttr.read_termination = '\n'
print(ttr.query('*idn?'))
ttr.write('*rst')   # turns instrument settings to factory default
ttr.write('*cls')   # Clears these analyzer status data structures: 
                    # Event Queue, Status Byte Register (except the MAV bit), Standard Event Status Register (SESR)


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
ttr.write('abort')  # Aborts the current measurement and changes the trigger sequence to idle state for all channel

ttr.write('display:enable 1')

# Configure Sweep



# AQUIRE/PROCESS DATA =====================================================
# start acquisition
ttr.write('initiate:immediate')
ttr.query('*opc?')

# get raw amplitude vs time data from RSA
freqAtAllPoints = ttr.query_binary_values('sense:frequency:data?', datatype='f',
    container=np.array)
ttr.write('mmemory:store:snp:[DATA] {test.s1p}')
ttr.query('calculate1:selected:data;smemory?')

acqStart = float(rsa.query('display:avtime:x:scale:offset?'))
acqEnd = float(rsa.query('display:avtime:x:scale:full?'))
time = np.linspace(acqStart,acqEnd, len(avt))


# PLOTS ===================================================================
# plot the data
plt.ioff()
fig = plt.figure(1, figsize=(20, 10))
ax = fig.add_subplot(111, facecolor='k')
ax.plot(time, avt, 'y')
ax.set_title('Amplitude vs Time')
ax.set_ylabel('Amplitude (dBm)')
ax.set_xlabel('Time (s)')
ax.set_xlim(acqStart,acqEnd)
plt.show()


def getDateFormatted():
    """
    Gets the current date and time formatted such that it can be used as
    a filename for logs

    Return: date as string
    """
    date = datetime.datetime.today()
    date = str(date)
    pos = date.find('.')
    date = date[:pos]
    date = date.replace(" ","_")
    date = date.replace(":","-")
    date = date.replace(":","-")
    return date


def plotter(xAxis,yAxis):
    """
    Takes xAxis and yAxis to make a plot. It then saves
    the plot with a filename corresponding to its 
    timestamp.

    Precondition: len(xAxis) = len(yAxis)

    Parameters:
    xAxis : indexable : values you want on the xAxis
    yAxis : indexable : values you want on the xAxis
    """
    assert type(xAxis) == type(yAxis)
    assert len(xAxis) == len(yAxis)

    # TODO Incorporate Plot creation to this function or its own

    # Create filename for plot
    filenameG = getDateFormatted() + ".png"
    filenameG = "Graphs/" + filenameG   
    plt.savefig(filenameG)              # Plot saved in directory named Graphs located in same directory as pyTekVNA


def logger(xAxis,yAxis):
    """
    Takes xAxis and yAxis to make a plot. It then saves
    the plot with a filename corresponding to its 
    timestamp.

    Precondition: len(xAxis) = len(yAxis)

    Parameters:
    xAxis : indexable : values you want on the xAxis
    yAxis : indexable : values you want on the xAxis
    """
    assert type(xAxis) == type(yAxis)
    assert len(xAxis) == len(yAxis)

    # Create filename for log
    filenameF = getDateFormatted() + ".txt"
    filenameF = "Logs/" + filenameF     
    f = open(filenameF, "a+")           # Plot saved in directory named Logs located in same directory as pyTekVNA
   
    # Fill log with contents
    for i in range(len(xAxis)):
        line = str(i) + ": " + str(xAxis[i]) + "\t" + str(yAxis[i])
        f.write(line)
        f.write('\n')


rm.close()