"""
ttrvna
Author: Brady Volkmann
Institution: University of Missouri Kansas City
Created: 6/20/2019
Edited: 6/27/2019
Python 3.6.0 64-bit (Anaconda 4.3.0)


This file contains the Ttrvna class
which is initialized when someone wants to do an
experiment with the Tektronix TTR506A VNA.

See VNAandPowSup.py if you want to control
the VNA in conjunction with a Power Supply.
"""

# IMPORTS ===================================================================
import visa
import numpy as np
import matplotlib.pyplot as plt
import time
import csv
import instrument as instr

# Ttrvna ===============================================================

class Ttrvna(instr.Instrument):
    """
    The Ttrvna class is used for instances of experiments with the Tektronix
    TTR506A VNA where the user may set up an automated design of experiment.

    Attributes:
        _rm                 : ResourceManager   : instance of visa's Resource Manager class
        _instr              : Resource          : instrument, TTR506A VNA in this case
        startFreqSweep      : str as SI unit    : determines start frequency for frequency sweep
        stopFreqSweep       : str as SI unit    : determines stop frequency for frequency sweep
        sweepDelay          : str as SI unit    : determines delay between each sweep
        sParam              : str               : determines which S Parameter is measured
        trials              : int > 0           : determines the number of trials/sweeps
        format              : str               : determines format for the data to be outputted into
        _measuredRange      : list of ints      : y values for the eventual output, usually s parameter
        _freqDomain         : list of ints      : x values in frequency for the eventual output
        _trial              : int               : current trial number
    """


    def __init__(self,start=None,stop=None,delay=None,sParam=None,trials=None,format='mlogarithmic'):
        """
        Constructor that initializes attributes of Ttrvna instance.
        By default the data format is 'mlogarithmic'.

        Parameters:
                start       : str as SI unit    : determines start frequency for frequency sweep
                stop        : str as SI unit    : determines stop frequency for frequency sweep
                dekay       : str as SI unit    : determines delay between each sweep
                sParam      : str               : determines which S Parameter is measured
                trials      : int > 0           : determines the number of trials/sweeps
                format      : str               : determines format for the data to be outputted into
        """
        self._rm = visa.ResourceManager()
        self._instr = self._rm.open_resource('GPIB8::1::INSTR')

        if start is not None:
            self.setStartSweep(start)
        if stop is not None:
            self.setStopSweep(stop)
        if delay is not None:
            self.setSweepDelay(delay)
        if sParam is not None:
            self.setsParam(sParam)
        if trials is not None:
            self.setTrials(trials)
        self.setFormat(format)
        
        self._measuredRange = None
        self._freqDomain = None
        self._trial = 1
    

    def setStartSweep(self,start):
        """
        Setter for Start of Frequency Sweep
        Example start = '50 MHz'
        """
        self.isSIUnit(start)
        self.startFreqSweep = start


    def setStopSweep(self,stop):
        """
        Setter for Stop of Frequency Sweep
        Example stop = '6 GHz'
        """
        self.isSIUnit(stop)
        self.stopFreqSweep = stop


    def setSweepDelay(self,delay):
        """
        Setter for delay between each sweep
        Example: delay = '1s'
        """
        self.isSIUnit(delay)
        self.sweepDelay = delay
    

    def setsParam(self,param):
        """
        Setter for the S parameter you would like to measure

        sParam must be one of the following as a srting:
        S11, S12, S21, S22

        Example: param = 'S21'
        """
        assert param in ['S11','S12','S21','S22']
        self.sParam = param


    def setTrials(self,trials):
        """
        Setter for number of trials/sweeps you would like to run
        Example: trials = 40
        """
        assert type(trials) == int
        assert trials > 0
        self.trials = trials


    def setFormat(self,format):
        """
        Setter for format of outputted data:

        Format must be one of the following as a string:
        mlogarithmic, phase, gdelay, slinear, slogarithmic, scomplex,
        smith, sadmittance, plinear, plogarithmic, polar, mlinear,
        swr, real, imaginary, uphase, pphase

        Example: format = mlogarithmic
        """
        assert type(format) == str
        assert format in ["mlogarithmic", "phase", "gdelay", "slinear", "slogarithmic", "scomplex",
                        "smith", "sadmittance", "plinear", "plogarithmic", "polar", "mlinear",
                        "swr", "real", "imaginary", "uphase", "pphase"]
        self.format = format


    def setMeasuredRange(self):
        """
        Takes a measurement according to inputted parameter after
        initializing data acquisition. After the data is appropriately
        modified into a list, it is set as the value for the 
        _measuredRange attribute.
        """

        self._initDataAcquisition()

        self._instr.write('calculate1:parameter1:define {}'.format(self.sParam))
        time.sleep(1)       # delay sometimes needed to ensure commands are used in sequence
        self._instr.write('calculate1:selected:format %s' % self.format)

        measurement = self._instr.query('calculate1:selected:data:fdata?')

        if self.isTwoComponents():                                         # If two components, create list of containing both components
            self._measuredRange = self._listify(measurement)
        else:                                                               # Otherwise, get rid of zero components that the TTR VNA
            measurement = self._listify(measurement)                        # uses to fill the second/imaginary component of
            self._measuredRange = self._removeSecondComponent(measurement)  # the measurement


    def setFreqDomain(self):
        """
        Used to set the frequency domain based on the the start
        and stop of the frequency sweep. Uses this as the value
        for self._freqDomain
        """
        start = self.unitConverter(self.startFreqSweep)
        stop = self.unitConverter(self.stopFreqSweep)
        if self.isTwoComponents():                                                     # If two components, set the domain for half the range
            freqDomain = np.linspace(start,stop, num=((len(self._measuredRange))/2))    # because of 1:2 Domain:Range correspondence
        else:
            freqDomain = np.linspace(start,stop, num=len(self._measuredRange))          # Otherwise, set domain to be same length as
        self._freqDomain = freqDomain                                                   # the _measuredRange


    def makeSweep(self):
        """
        Takes a sweep measurement for desired value with start
        and stop be the span of the sweep and delay being the time
        between each sweep. Logs data in three ways, text file, plot as 
        png, and csv.

        The Conditionals with the trials is used because it usually takes
        the VNA a trial to adjust to it the commanded settings.
        So the first trial is not recorded until I find a better way to do this.
        """

        self._configInst()
        self.setMeasuredRange()
        self.setFreqDomain()
        if self._trial > 1:          # Ensures that the first trial is not recorded
            self._createPlot()   # png
            self._logger()       # txt
            self._csvWriter()    # csv
        self._trial += 1

    
    def makeSweepUnprocessed(self):
        """
        Same as makeSweep, but it does not process the data. It merely returns the data
        as a list.
        """
        self._configInst()
        self.setMeasuredRange()
        self.setFreqDomain()
        if self.isTwoComponents():
            self._getMagnitudes()
            self._measuredRange = self._magnitudes
        self._trial += 1
        return [self._freqDomain,self._measuredRange]


    def run(self):
        """
        Function that you should call to run an experiment after the
        constructor has been called.
        Makes a sweep for each trial.
        """
        for _ in range(self.trials):
            self.makeSweep()
            time.sleep(self.unitConverter(self.sweepDelay))
        print("Done!")
    
     

# HELPER FUNCTIONS ==============================================

    def _initDataAcquisition(self):
        """
        Initializes data acquizition for the instrument.
        """
        self._instr.write('initiate:immediate')
        self._instr.query('*opc?')


    def _configInst(self):
        """
        Configures the instrument to the constants specified
        by the user.

        Precondition: startFreqSweep < stopFreqSweep
        """
        assert self.startFreqSweep < self.stopFreqSweep

        self._instr.timeout = 10000
        self._instr.encoding = 'latin_1'
        self._instr.write_termination = None
        self._instr.read_termination = '\n'
        if self.trials is None or self._trial == 1:
            print(self._instr.query('*idn?'))
        self._instr.write('*rst')   # turns instrument settings to factory default
        self._instr.write('*cls')   # Clears these analyzer status data structures: 
                                    # Event Queue, Status Byte Register (except the MAV bit), Standard Event Status Register (SESR)

        self._instr.write('abort')  # Aborts the current measurement and changes the trigger sequence to idle state for all channel

        self._instr.write('display:enable 1')
        self._instr.write('sense1:frequency:start {}'.format(self.unitConverter(self.startFreqSweep)))
        self._instr.write('sense1:frequency:stop {}'.format(self.unitConverter(self.stopFreqSweep)))
        self._instr.write('sense1:sweep:delay {}'.format(self.unitConverter(self.sweepDelay)))


    def _createPlot(self):
        """
        Creates plot with from xAxis and yAxis and then saves
        the plot in Graphs/ with a file name corresponding to 
        the date and time.
        """
        fig = plt.figure(1, figsize=(20, 10))
        ax = fig.add_subplot(111, facecolor='k')
        if self.isTwoComponents():
            ax.plot(self._freqDomain,self._magnitudes,'y')                                          
            lower = min(self._magnitudes)
            upper = max(self._magnitudes)
        else:                                                                                      
            ax.plot(self._freqDomain, self._measuredRange, 'y')                                     # just plot _freqDomain
            lower = min(self._measuredRange)                                                        # against _measuredRange
            upper = max(self._measuredRange)
                                                                                                    
        ax.set_title('Amplitude vs Frequency')
        ax.set_ylabel('Amplitude (dBm)')
        ax.set_xlabel('Freq (Hz)')
        ax.set_xlim(self._freqDomain[0],self._freqDomain[-1])
        ax.set_ylim(lower-(0.2*(upper-lower)),upper+(0.2*(upper-lower)))    # Scaled to fit range

        # Save Plot
        filenameG = self.getDateFormatted() + ".png"
        filenameG = "Graphs/" + filenameG   
        plt.savefig(filenameG)                   # Plot saved in directory named Graphs located in same directory as pyTekVNA
        plt.clf()


    def _logger(self):
        """
        Takes xAxis and yAxis to make a plot. It then saves
        the plot with a filename corresponding to its 
        timestamp.
        """

        # Create filename for log
        filenameF = self.getDateFormatted() + ".txt"
        filenameF = "Logs/" + filenameF     
        f = open(filenameF, "a+")           # Log saved in directory named logs located in same directory as this file
    
        # Fill log with contents
        if self.isTwoComponents():
            for i in range(len(self._freqDomain)):
                line = str(i) + ": " + str(self._freqDomain[i])+ "\t" + \
                            str(self._measuredRange[2*i]) + "\t" + str(self._measuredRange[(2*i)+1])    # If two components, log each
                f.write(line)                                                                           # pair on same line against
                f.write('\n')                                                                           # frequency
        else:    
            for i in range(len(self._freqDomain)):                                                      # Otherwise, log 1:1 domain:range
                line = str(i) + ": " + str(self._freqDomain[i]) + "\t" + str(self._measuredRange[i])
                f.write(line)
                f.write('\n')


    def _csvWriter(self):
        """
        Writes dataX and dataY to a csv file by making data into table first 
        Titled based on the date.
        The CSV is comma delimited.
        """

        # Make data into table
        table = []
        if self.isTwoComponents():                                                                          # Same as _logger()
            for i in range(len(self._freqDomain)):                                                          # If two components, log each
                table.append([self._freqDomain[i],self._measuredRange[2*i],self._measuredRange[(2*i)+1]])   # pair on same line against
        else:                                                                                               # frequency
            for i in range(len(self._freqDomain)):
                table.append([self._freqDomain[i],self._measuredRange[i]])                                  # Otherwise, log 1:1 domain:range

        # Write to CSV
        filename = 'CSVs/' + self.getDateFormatted() + '.csv'
        with open(filename, 'w', newline='') as csvfile:
                dataWriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
                for i in range(len(table)):
                        dataWriter.writerow(table[i])
    

    def isTwoComponents(self):
        """
        Determines if the measured output is one or
        two components based on format

        Return: True if is two component
        """
        if self.format in ["slinear","slogarithmic","scomplex",
                            "smith","sadmittance","plinear",
                            "plogarithmic","polar"]:
            return True
        else:
            return False
    
    
    def _inverseFFT(self):
        """
        Calculates the inverse fourier transform of the measured range.

        Precondition: self.isTwoComponents() == True

        Return: invFFT as list of complex values
        """
        assert self.isTwoComponents() == True
        return(np.fft.ifft(self._measuredRange))


    @staticmethod
    def _listify(initial):
        """
        Takes a string separated by commas, and breaks each component
        separated by commas into its own element in a list. Then, it 
        returns the list as float elements.

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
                if ',' not in initial:
                        listified.append(initial)
        final = []
        for item in listified:  
                final.append(float(item))
        return final
    

    @staticmethod
    def _removeSecondComponent(values):
        """
        Removes the second component in a list of complex values assuming
        that every other value starting from index one ought to be removed.

        Return: list with second component / imaginary values removed

        Parameters:
                values : list : the complex values are removed from this list
        """
        assert type(values) == list
        newList = []
        for i in range(len(values)):
            if (i%2) == 0:
                newList.append(values[i])
        return newList
    

    def _getMagnitudes(self):
        """
        Gets magnitude of measured range if measured range is complex and stores
        it in self._magnitudes as a list
        """
        assert self.isTwoComponents()
        self._magnitudes = []
        realPart = []
        complexPartTemp = []
        complexPart = []
        for i in range(len(self._measuredRange)):
            if (i%2) == 1:
                complexPartTemp.append(self._measuredRange[i])
            else:
                realPart.append(self._measuredRange[i])
        for i in range(len(complexPartTemp)):
            complexPart.append(complex(str(complexPartTemp[i])+'j'))
        for i in range(len(realPart)):
            self._magnitudes.append(abs(realPart[i]+complexPart[i]))


# EXECUTION ============================================
if __name__ == "__main__":
    test = Ttrvna(start='50 MHz', stop='6 GHz', delay='8s', sParam='S21',trials=1,format='smith')
    test.run()
    test._inverseFFT()

