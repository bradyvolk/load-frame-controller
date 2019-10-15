"""
Experiment
Author: Brady Volkmann
Institution: University of Missouri Kansas City
Created: 7/24/2019
Edited: 7/24/2019
Python 3.6.0 64-bit (Anaconda 4.3.0)

Keitheley 6514 Electrometer: http://www.tunl.duke.edu/documents/public/electronics/Keithley/keithley-6514-electrometer-manual.pdf
"""

# IMPORTS ===================================================================
import visa
import numpy as np
import matplotlib.pyplot as plt
import datetime
import time
import csv
import instrument as instr


# ELECTROMETER ===============================================================
class Electrometer(instr.Instrument):
    """
    The Electrometer class is used for instances of experiments with the Keithley
    6514 Electrometer where the user may set up an automated design of experiment.

    Attributes:
        _rm                 : ResourceManager   : instance of visa's Resource Manager class
        _instr              : Resource          : instrument, 6514 Electrometer in this case
    """


    def __init__(self,start=None,stop=None,delay=None,sParam=None,trials=None,format='mlogarithmic'):
        """
        Constructor that initializes attributes of Experiment instance.
        By default the data format is 'mlogarithmic'.

        Parameters:
        """
        self._rm = visa.ResourceManager()
        self._instr = self._rm.open_resource('GPIB8::1::INSTR')
    

    def _configInst(self):
        """
        Configures the instrument to the constants specified
        by the user.
        """
        self._instr.timeout = 10000
        self._instr.encoding = 'latin_1'
        self._instr.write_termination = None
        self._instr.read_termination = '\n'
        print(self._instr.query('*idn?'))
        self._instr.write('*rst')   # turns instrument settings to factory default
        self._instr.write('*cls')   # Clears these analyzer status data structures: 
                                    # Event Queue, Status Byte Register (except the MAV bit), Standard Event Status Register (SESR)

        self._instr.write('abort')  # Aborts the current measurement and changes the trigger sequence to idle state for all channel

# Execution =============================================
test = Electrometer()
test._configInst()
