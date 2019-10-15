"""
VNAandPowSup.py
Author: Brady Volkmann
Created: 7/15/2019
Last Edit: 7/22/2019
Python 3.6.0 64-bit (Anaconda 4.3.0)
Additional Required Software: 
    VectorVU-PC:  https://www.tek.com/vna/ttr500
    PyVISA: pip install pyvisa
Programming Manual for TTR506A: https://download.tek.com/manual/TTR500-Programmer-Manual-077125700.pdf
Manual for TP3005P: https://tekpower.us/tp3005pmanual.html

Used to control TP3005P power supply in conjunction with
Tektroniks TTR506 VNA. 

See README.md in this directory for detailed usage guide.
TL;DR:
    Go to the bottom under execution.
    Three ways to run:
        <PowSupVNAInstance>.sweepUpDown() : sweeps up to 15V, back to 0V, down to -15V, back to 0V at interval specified
                                            by voltageStep. records data in Graphs/ Logs/ and CSVs/ directories located in same directory
                                            as this
        <PowSupVNAInstance>.sweepUp()     : takes measurement at voltage step indicated by voltageStep for _trials times
                                            Records similarly to .sweepUpDown()
        <PowSupVNAInstance>.sweepDownUp() : sweeps from -15V to 15V by interval specified by voltageStep. Intended to be
                                            used with .plotFreqSpecific(<desiredFreq>), but doesn't have to be used as such.
    By default, plots are made as freq v. intensity with a different line for each voltage, but
        you can generate a plot voltage v. intensity at a specific frequency by calling 
        .plotFreqSpecific(<desiredFreq>) and it will pull values closest to <desiredFreq> from your
        frequency domain.

And quick side note:
    You may see large sections of the code commented out. I initially set it up to 
    plot the real part of measurements from the VNA only and to store the real and imaginary
    parts in logs and csvs. Instead, however, the magnitude of the complex value should be plotted,
    so in making that change, I was not able to still log the real and imaginary components separately.
    It is, of course, possible to do this, but the change is complicated and too large for the time
    I have left on this project. Thus, I left the code in to save the complex values unmapped to the reals
    commetted out in case the user decides they want to resurrect that feature. Doing so, will require
    some changes to how the ttrvna.py outputs it's _measuredRange in makeSweepUnprocessed(). If this is a
    change you'd like to make and find my code too nebulous, feel free to contact me.

For confusions/questions/complaints: contact bvv4@cornell.edu
"""

# IMPORTS ==============================================
import ttrvna as vna
import TP3005PMod as tp
import numpy as np
import matplotlib.pyplot as plt
import time
import csv


# PowSupVNA ============================================

class PowSupVNA(object):
    """
    Class for controlling TP3005P power supply in conjunction
    with Tektroniks TTR506 VNA

    Attributes:
            _power           : PowSup               : used to control TP3005P
            _vna             : Ttrvna               : used to control TTR506 VNA
            _trials          : int > 0              : the number of trials to run with PowSup and VNA
            _runData         : list of lists        : data from trials
            _frequency       : list of lists        : list of frequncy data from trials
            _voltages        : list of floats/ints  : list of voltages from trials
            _intensity       : list of lists        : list of intensity data from trials
    """
    
    def __init__(self,comTP,comArd=None,voltageStep=1,initialVoltage=0,trials=3,start=None,stop=None,delay=None,
                            sParam=None,format='mlogarithmic'):
        """
        Constructor for creating instances of PowSupVNA

        Parameters:
                comTP           : str                       : communications port for TP (e.g. "COM7")
                comArd          : str                       : communications port for Arduino (e.g. "COM7")
                voltageStep     : float or int > 0          : the number of volts to step between each trial
                initialVoltage  : 0 <= float or int <= 30   : intial voltage if run a set of trials
                trials          : int > 0                   : the number of trials to run with PowSup and VNA
                start           : str as SI unit            : determines start frequency for frequency sweep
                stop            : str as SI unit            : determines stop frequency for frequency sweep
                delay           : str as SI unit            : determines delay between each sweep
                sParam          : str                       : determines which S Parameter is measured
                format          : str                       : determines format for the data to be outputted into
        """
        self._power = tp.PowSup(comTP,comArd=comArd,voltageStep=voltageStep,initialVoltage=initialVoltage)
        self._vna = vna.Ttrvna(start=start,stop=stop,delay=delay,
                                    sParam=sParam,format=format,trials=3)
        self._trials = trials
        

    def sweepUp(self):
        """
        Runs trials, collects data into _runData
        as a list with format [voltages,[[frequency],[range]]]
        """
        self._vna.makeSweepUnprocessed()   # run dud trial here
        print('Beginning Data Collection')
        time.sleep(10)

        vnaData = []
        for _ in range(self._trials):
            vnaData.append(self._vna.makeSweepUnprocessed())
            time.sleep(10)
            self._power.doTrial()
            time.sleep(1)
        self._runData = []
        for i in range(len(vnaData)):
            self._runData.append([self._power.getVoltages()[i],vnaData[i]])
        self._power.voltsSetpointSet(0)
        self._formatData()
        self._record()


    def sweepUpDown(self):
        """
        Runs trials, collects data into _runData
        as a list with format [voltages,[[frequency],[range]]]
        Goes up to 15V then down to -15V taking with step size
        designated by the user. Then processes and records data in
        ._processData().
        """
        self._vna.makeSweepUnprocessed()
        print('Beginning Data Collection')

        vnaData = []
        # Start voltage at zero
        self._power.voltsSetpointSet(0)
        negStep = (-1)*self._power.voltageStep; time.sleep(1)

        # Step to 30V and record each step
        for _ in range(0, 15, self._power.voltageStep):
            vnaData.append(self._vna.makeSweepUnprocessed()); time.sleep(10)
            self._power.incrementVolt(self._power.voltageStep); time.sleep(1)
        # Step back to 0V and record each step
        for _ in range(0, 15, self._power.voltageStep):
            vnaData.append(self._vna.makeSweepUnprocessed()); time.sleep(10)
            self._power.incrementVolt(negStep); time.sleep(1)  
        # Switch polarity on power supply
        assert self._power.voltsMeas() == 0; time.sleep(2)
        self._power.changePolarity(); time.sleep(2)
        # Step to -30V and record each step
        for _ in range(0, 15, self._power.voltageStep):
            vnaData.append(self._vna.makeSweepUnprocessed()); time.sleep(10)
            self._power.incrementVolt(self._power.voltageStep); time.sleep(1)
        # Step back to 0V and record each step
        for _ in range(0, 15, self._power.voltageStep):
            vnaData.append(self._vna.makeSweepUnprocessed()); time.sleep(10)
            self._power.incrementVolt(negStep); time.sleep(1)
        self._power.voltsSetpointSet(0)

        # Switch polarity on power supply
        assert self._power.voltsMeas() == 0; time.sleep(2)
        self._power.changePolarity(); time.sleep(2)

        self._processData(vnaData)


    def sweepDownUp(self):
        """
        Sweeps from -15V to 15V by self._voltageStep. Meant to be
        used in conjunction with plotFreqSpecific.
        """
        self._vna.makeSweepUnprocessed()
        print('Beginning Data Collection')

        vnaData = []
        # Start voltage at zero
        self._power.voltsSetpointSet(0)
        negStep = (-1)*self._power.voltageStep; time.sleep(1)
        # some time is needed to let Arduino as a load cell is usually attached to 
        # my Arduino in my set up.
        time.sleep(20)

        # Switch polarity on power supply
        assert self._power.voltsMeas() == 0; time.sleep(2)
        self._power.changePolarity(); time.sleep(2)
        self._power.voltsSetpointSet(15)
        
        # Increment up to 0V
        for _ in range(0, 15, self._power.voltageStep):
            vnaData.append(self._vna.makeSweepUnprocessed()); time.sleep(10)
            self._power.incrementVolt(negStep); time.sleep(1)
        # Switch polarity on power supply
        assert self._power.voltsMeas() == 0; time.sleep(2)
        self._power.changePolarity(); time.sleep(2)
        # Increment up to 15V
        for _ in range(0, 15, self._power.voltageStep):
            vnaData.append(self._vna.makeSweepUnprocessed()); time.sleep(10)
            self._power.incrementVolt(self._power.voltageStep,recorded=False); time.sleep(1)
        vnaData.append(self._vna.makeSweepUnprocessed()); time.sleep(10)
        self._power.incrementVolt((-1)*15)
        self._processData(vnaData,fromDownUp=True)


    def plotFreqSpecific(self,frequency):
        """
        Creates a plot with voltage as x-axis and y-axis as intensity.
        Used to look at a specific frequency and see how it changes in 
        intensity as voltage changes.

        Parameters:
                frequency   : str as SI Unit    : frequency desired to examine (e.g. '50 MHz')
        """
        self._vna.isSIUnit(frequency)
        freqConverted = self._vna.unitConverter(frequency)
        fig = plt.figure()

        # Search for closest frequency to that frequency in the freq Domain
        for i in range(len(self._frequency[0])):
            if i != (len(self._frequency)-1):
                # Look for the value the converted frequency is between in the freqDomain
                if self._frequency[0][i] <= freqConverted and freqConverted <= self._frequency[0][i+1]:
                    # Check if upper or lower is closer to the frequency we want
                    if np.abs(self._frequency[0][i]-freqConverted) <= np.abs(self._frequency[0][i+1]-freqConverted):
                        pos = i
                    else:
                        pos = i+1
        intensities = []
        voltages = []
        # if self._vna.isTwoComponents():
        #     for i in range(len(self._frequency)):
        #         intensities.append(self._intensity[i][2*pos])
        # else:
        for i in range(len(self._frequency)):
            intensities.append(self._intensity[i][pos])
        for i in range(len(self._voltages)):
            voltages.append(self._voltages[i][0])
        plt.plot(voltages,intensities)
        fig.suptitle('Intensity-Voltage at %s' % frequency, fontsize=20)
        plt.xlabel('Voltage (V)', fontsize=18)
        plt.ylabel('Intensity (dBm)', fontsize=16)

        self._saveFig()


    def _processData(self,vnaData,fromDownUp=False):
        """
        Processes data, formats it, and records it.

        Parameter:
                vnaData : list of lists : unprocessed data from .sweepUp(), .sweepUpDown(), .sweepDownUp()
        """
        self._runData = []
        if not fromDownUp:
            neg = False
            for i in range(len(vnaData)):
                if not neg:
                    self._runData.append([self._power.getVoltages()[i],vnaData[i]])
                else:
                    self._runData.append([(-1)*self._power.getVoltages()[i],vnaData[i]])
                if i > 0 and self._power.getVoltages()[i] == 0:
                    neg = True
        else:
            neg = True
            for i in range(len(vnaData)):
                if neg:
                    self._runData.append([(-1)*self._power.getVoltages()[i],vnaData[i]])
                else:
                    self._runData.append([self._power.getVoltages()[i],vnaData[i]])
                if i > 0 and self._power.getVoltages()[i] == 0:
                    neg = False
        self._formatData()
        self._record()


    def _record(self):
        """
        Saves data in plots, logs, and CSVs, located in same directory
        as this file with the subdirectory names 'Graphs/', 'Logs/', and
        'CSVs/' respectively.
        """
        self._plot()
        self._csvWriter()
        self._logger()
                

    def _formatData(self):
        """
        Formats _runData into three separate lists _frequency, _voltages,
        and _intensity
        """
        assert self._runData is not None

        # Getting Axes data into separate lists
        x=[]; y=[]; z=[]
        for i in range(len(self._runData)):
            ySet = []; xSet = []; zSet = []
            for _ in range(len(self._runData[i][1][0])):
                ySet.append(self._runData[i][0])
            y.append(ySet)
            xSet.append(self._runData[i][1][0])
            x.append(xSet)
            zSet.append(self._runData[i][1][1])
            z.append(zSet)

        # Reduce extra brackets
        xnew = []; znew = []
        for i in range(len(x)):
            xnew.append(x[i][0])
            znew.append(z[i][0])
        x = xnew; z = znew

        self._frequency = x
        self._voltages = y
        self._intensity = z


    def _plot(self):
        """
        Creates a 2D plot of the data with frequency domain on the x-axis and power on the y-axis.
        Multiple lines are plotted - one for each voltages. Then saves
        files as png in /Graphs located in the same directory as this script.

        The data is formatted strangely so that a user may make use this
        to generate 3D plots relatively easily.
        """
        fig = plt.figure()

        # Take out second component of intensity if needed
        # if self._vna.isTwoComponents():
        #     intensitySimplified = []
        #     for i in range(len(self._intensity)):
        #         tempSet = []
        #         for j in range(len(self._intensity[i])):
        #             if (j%2) == 0:
        #                 tempSet.append(self._intensity[i][j])
        #         intensitySimplified.append(tempSet)
        #     for i in range(len(self._frequency)):
        #         plt.plot(self._frequency[i],intensitySimplified[i],label=('%sv' % self._voltages[i][0]))
        # else:
        for i in range(len(self._frequency)):
            plt.plot(self._frequency[i],self._intensity[i],label=('%sv' % self._voltages[i][0]))
        plt.legend(loc='upper left')
        fig.suptitle('Intensity-Frequency with non-Constant Voltage', fontsize=18)
        plt.xlabel('Frequency (Hz)', fontsize=18)
        plt.ylabel('Intensity (dBm)', fontsize=16)

        # Save plot
        self._saveFig()


    def _saveFig(self):
        """
        Saves current figure from matplotlib into file located in same
        directory named "Graphs/"
        """
        # Save plot
        filenameG = self._vna.getDateFormatted() + ".png"
        filenameG = "Graphs/" + filenameG   
        plt.savefig(filenameG)              # Plot saved in directory named Graphs located in same directory as pyTekVNA
        plt.clf()


    def _logger(self):
        """
        Takes frequency and intensity to make a log. It then saves
        the log with a filename corresponding to its 
        timestamp in "Logs/"
        """

        # Create filename for log
        filenameF = self._vna.getDateFormatted() + ".txt"
        filenameF = "Logs/" + filenameF     
        f = open(filenameF, "a+")           # Log saved in directory named logs located in same directory as this file
    
        # if self._vna.isTwoComponents():
        #     for i in range(len(self._voltages)):
        #         f.write('%s\t\t\t' % self._voltages[i][0])
        # else:
        for i in range(len(self._voltages)):
            f.write('%s\t\t' % self._voltages[i][0])
        f.write('\n')

        # if self._vna.isTwoComponents():
        #     for i in range(len(self._voltages[0])):
        #         line = ""
        #         for j in range(len(self._voltages)):
        #             line = line + str(self._frequency[j][i]) + '\t' + str(self._intensity[j][2*i]) + \
        #                     str(self._intensity[j][2*i + 1]) + '\t'
        #         f.write(line)
        #         f.write('\n')
        # else:    
        for i in range(len(self._voltages[0])):
            line = ""
            for j in range(len(self._voltages)):
                line = line + str(self._frequency[j][i]) + '\t' + str(self._intensity[j][i]) + '\t' 
            f.write(line)
            f.write('\n')

    
    def _csvWriter(self):
        """
        Takes frequency and intensity to make a csv. It then saves
        the csv with a filename corresponding to its 
        timestamp in "CSVs/"  
        """
        # Initialize Header
        table = []
        voltageRow = []
        for i in range(len(self._voltages)):
            voltageRow.append(self._voltages[i][0])
            voltageRow.append(" ")
            if self._vna.isTwoComponents():
                voltageRow.append(" ")
        table.append(voltageRow)
        
        # Fill table with data
        # if self._vna.isTwoComponents():
        #     for i in range(len(self._frequency[0])):
        #         row = []
        #         for j in range(len(self._frequency)):
        #             row.append(self._frequency[j][i])
        #             row.append(self._intensity[j][2*i])
        #             row.append(self._intensity[j][2*i + 1])
        #         table.append(row)
        # else:                                                                                            
        for i in range(len(self._frequency[0])):
            row = []
            for j in range(len(self._frequency)):
                row.append(self._frequency[j][i])
                row.append(self._intensity[j][i])
            table.append(row)

        # Write to CSV
        filename = 'CSVs/' + self._vna.getDateFormatted() + '.csv'
        with open(filename, 'w', newline='') as csvfile:
                dataWriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
                for i in range(len(table)):
                        dataWriter.writerow(table[i])

        

# EXECUTION ===============================================
"""
This is the only part you should need to change to make measurements.
"""
if __name__ == "__main__":
    test = PowSupVNA('COM7',comArd='COM6',voltageStep=5,initialVoltage=0,trials=3, start='50 MHz',
                    stop='6 GHz', delay='8s', sParam='S21', format='smith')
    
    # Three ways to get data; uncomment the one you want
    # ================================================
    """
    Sweeps up to 15V, back to 0V, down to -15V, back to 0V at interval specified by self._voltageStep.
    Records data as intensity v. frequency plots and makes logs and CSVs in the subdirectories of the
    directory this file is in. 
    """
    # test.sweepUpDown()
    # ================================================
    """
    Sweeps up from 0 to however many volts depending on self._voltageStep and self._trials.
    Records data like .sweepUpDown()
    """
    # test.sweepUp()
    # ================================================
    """
    Sweeps from -15V to 15V by self._voltageStep. Saves data as normal and additionally
    makes a intensity v. voltage plot at a specific frequency argument specified by 
    .plotFreqSpecific(<desiredFreq>)
    """
    test.sweepDownUp()
    time.sleep(5)
    test.plotFreqSpecific('3.02 GHz')






    

        

        



