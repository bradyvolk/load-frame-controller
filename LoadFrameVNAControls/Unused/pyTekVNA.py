"""
VISA Control: TTR VNA 
Author: Morgan Allison
Edited: Brady Volkmann
Date Created: 9/14
Date Edited: 6/20/2019

Windows 7 64-bit, TekVISA 4.0.4
Python 3.6.0 64-bit (Anaconda 4.3.0)
MatPlotLib 2.0.0, PyVISA 1.8
To get PyVISA: pip install pyvisa
Download Anaconda: http://continuum.io/downloads
Anaconda includes MatPlotLib

It seems the first trial always is bunk since the
the VNA does not change it's setting until after the
trial. So until I find a better approach, the first 
trial will always be thrown out.
"""

# IMPORTS ===================================================================
import visa
import numpy as np
import matplotlib.pyplot as plt
import datetime
import time
import csv
from constants import *


# CONNECT OT INSTRUMENT =====================================================
print("")
rm = visa.ResourceManager()
rm.list_resources()
ttr = rm.open_resource('GPIB8::1::INSTR')

# FUNCTIONS =====================================================

def listify(initial):
        """
        Takes a string separated by commas, and breaks each component
        separated by commas into its own element in a list. Then, it 
        returns the list as float elements. Also gets rid of alternating zero pattern.

        Return: listified version of initial

        Precondition: initial is a string with commas and numbers between commas

        Parameters:
                initial : str : this is what is listified
        """
        assert type(initial) == str
        assert ',' in initial

        listified = []

        while ',' in initial:
                pos = initial.find(',')
                listified.append(initial[0:pos])
                initial = initial[pos+1:]
                if ',' in initial:
                        pos = initial.find(',')
                        initial = initial= initial[pos+1:]
        final = []
        for item in listified:  
                final.append(float(item))
        return final


def getFreq(start,stop,measRange):
        """
        Used to generate frequency domain of measurement.

        Return: list of linearly spaced values for a domain

        Precondition: If start or stop are strings, they must have SI units.

        Parameters:
                start : str or int or float : the start of the frequency domain
                stop : str or int or float : the end of the frequency domain
                measRange : list of y values : the spacing of the frequency domain
        """
        assert type(start) == str and type(stop) == str
        assert type(measRange) == list

        start = unitConverter(start)
        stop = unitConverter(stop)
        freqDomain = np.linspace(start,stop, num=len(measRange))
        return freqDomain


def unitConverter(value):
        """
        Converts unit as a str with SI units into a a float

        Return: value as float

        Precondition: value > 1 in base unit (i.e. no mHz)

        Parameters:
                value : str : frequency to be converted
        """
        assert type(value) == str
        
        try:
                return float(value)
        except:
                assert 'p' or 'n' or 'micro' or 'm' or 'c' or 'd' or 'd' \
                        or 'h' or 'k' or 'M' or 'G' or 'T' in value

                multiplier = 0
                unitPrefixes = {
                                'p':10**-12, 'n':10**-9,
                                'micro':10**-6, 'm':10**-3,
                                'c':10**-2, 'd':10**-1,
                                'da':10**1, 'h':10**2,
                                'k':10**3, 'M':10**6,
                                'G':10**9, 'T':10**12
                                }

                for pref in unitPrefixes:
                        if pref in value:
                                if pref == 'd' and 'da' not in value:
                                        multiplier = unitPrefixes[pref]
                                        break
                                elif pref == 'h' and 'z' not in value:          # Not to get mixed with Hz
                                        multiplier = unitPrefixes[pref]
                                elif pref != 'd':
                                        multiplier = unitPrefixes[pref]
                                        break
                pos = 0
                while value[pos].isnumeric():
                        pos+=1
                convertedValue = float(value[:pos])*multiplier
                return convertedValue



# PLOTS ===================================================================

def createPlot(xAxis, yAxis):
        """
        Creates plot with from xAxis and yAxis and then saves
        the plot in Graphs/ with a file name corresponding to 
        the date and time.

        Parameters:
                xAxis : list of floats : the x Axis of the plot
                yAxis : list of floats : the y Axis of the plot
        """

        fig = plt.figure(1, figsize=(20, 10))
        ax = fig.add_subplot(111, facecolor='k')
        ax.plot(xAxis, yAxis, 'y')

        ax.set_title('Amplitude vs Frequency')
        ax.set_ylabel('Amplitude (dBm)')
        ax.set_xlabel('Freq (Hz)')
        ax.set_xlim(xAxis[0],xAxis[-1])
        ax.set_ylim(-150,10)

        # Save Plot
        filenameG = getDateFormatted() + ".png"
        filenameG = "Graphs/" + filenameG   
        plt.savefig(filenameG)                   # Plot saved in directory named Graphs located in same directory as pyTekVNA



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

    Precondition: len(xAxis) == len(yAxis)

    Parameters:
        xAxis : indexable : values you want on the xAxis
        yAxis : indexable : values you want on the xAxis
    """
    assert len(xAxis) == len(yAxis)


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


def csvWriter(dataX,dataY):
        """
        Writes dataX and dataY to a csv file by making data into table first 
        Titled based on the date.
        The CSV is comma delimited.
        
        Precondition: len(dataX) == len(dataY)
        Parameter: 
                dataX : indexable : data for x-axis
                dataY : indexable : data for y-axis
        """
        assert len(dataX) == len(dataY)

        # Make data into table
        table = []
        for i in range(len(dataX)):
                table.append([dataX[i],dataY[i]])

        # Write to CSV
        filename = 'CSVs/' + getDateFormatted() + '.csv'
        with open(filename, 'w', newline='') as csvfile:
                dataWriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
                for i in range(len(table)):
                        dataWriter.writerow(table[i])


def configInst(startFreqSweep, stopFreqSweep, sweepDelay):
        """
        Configures the instrument to the constants specified
        by the user.

        Precondition: startFreqSweep < stopFreqSweep

        Param:
                startFreqSweep : str as SI unit : start of frequency sweep
                stopFreqSweep : str as SI unit : stop of frequency sweep
                sweepDelay : str as SI unit : delay between each sweep
        """
        assert type(startFreqSweep) == str
        assert type(stopFreqSweep) == str
        assert type(sweepDelay) == str

        ttr.timeout = 10000
        ttr.encoding = 'latin_1'
        ttr.write_termination = None
        ttr.read_termination = '\n'
        print(ttr.query('*idn?'))
        ttr.write('*rst')   # turns instrument settings to factory default
        ttr.write('*cls')   # Clears these analyzer status data structures: 
                            # Event Queue, Status Byte Register (except the MAV bit), Standard Event Status Register (SESR)



        ttr.write('abort')  # Aborts the current measurement and changes the trigger sequence to idle state for all channel

        ttr.write('display:enable 1')
        ttr.write('sense1:frequency:start {}'.format(unitConverter(startFreqSweep)))
        ttr.write('sense1:frequency:stop {}'.format(unitConverter(stopFreqSweep)))
        ttr.write('sense1:sweep:delay {}'.format(unitConverter(sweepDelay)))


def initDataAcquisition():
        """
        Initializes data acquizition for the instrument.
        """
        ttr.write('initiate:immediate')
        ttr.query('*opc?')

        

def measure(value):
        """
        Takes a measurement according to inputted parameter after
        initializing data acquisition.

        Return: measurement

        Parameter:
                value : str : value you want to measure
        """
        assert type(value) == str

        initDataAcquisition()

        ttr.write('calculate1:parameter1:define {}'.format(value))
        time.sleep(1)
        measurement = ttr.query('calculate1:selected:data:fdata?')
        print(measurement)
        return measurement


def makeSweep(start,stop,delay,value):
        """
        Takes a sweep measurement for desired value with start
        and stop be the span of the sweep and delay being the time
        between each sweep. Logs data in three ways, text file, plot as 
        png, and csv.

        Parameters:
                start : str as SI unit : start of frequency sweep
                stop : str as SI unit : stop of frequency sweep
                delay : str as SI unit : delay between each sweep
                value : str : value you want to measure
        """

        configInst(start,stop,delay)
        intensity = listify(measure(value))
        frequencies = getFreq(start, stop, intensity)
        createPlot(frequencies,intensity)       # png
        logger(frequencies,intensity)           # txt
        csvWriter(frequencies,intensity)        # csv


# EXECUTION ========================================================================

makeSweep(startFreqSweep,stopFreqSweep,sweepDelay,sParam)
print("Done!")
print("")
print("Expected ignored exception below:")

time.sleep(10)
makeSweep(startFreqSweep,stopFreqSweep,sweepDelay,sParam)
print("Done!")
print("")
print("Expected ignored exception below:")

time.sleep(10)
makeSweep(startFreqSweep,stopFreqSweep,sweepDelay,sParam)
print("Done!")
print("")
print("Expected ignored exception below:")