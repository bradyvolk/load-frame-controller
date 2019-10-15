"""
Experiment
Author: Brady Volkmann
Institution: University of Missouri Kansas City
Created: 7/22/2019
Edited: 7/22/2019
Python 3.6.0 64-bit (Anaconda 4.3.0)

This file defines the instrument class which 
many components of the loadframe-VNA-PowerSupply
apparatus inherit from.
"""
# IMPORTS ==========================================
import datetime

# Instrument =======================================
class Instrument(object):
    """
    Parent class to many subclasses. Contains methods any instrument may need.
    """

    @staticmethod
    def getDateFormatted():
        """
        Gets the current date and time formatted such that it can be used as
        a filename for logs, plots, etc

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


    def unitConverter(self,value):
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
                self.isSIUnit(value)

                multiplier = 1
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
                                elif pref == 'h' and 'z' not in value:          # To not get mixed with Hz
                                        multiplier = unitPrefixes[pref]
                                elif pref != 'd':
                                        multiplier = unitPrefixes[pref]
                                        break
                pos = 0
                while value[pos].isnumeric() or value[pos] == '.':
                        pos+=1
                convertedValue = float(value[:pos])*multiplier
                return convertedValue


    @staticmethod
    def isSIUnit(value):
        """
        Checks if the value is an SI Unit as a string
        """
        # Check if string
        assert type(value) == str

        # Check that string has numbers
        var = False
        for char in value:
            if char.isnumeric():
                var = True
        assert var == True

        # Check for units
        assert 'p' or 'n' or 'micro' or 'm' or 'c' or 'd' or 'd' \
                        or 'h' or 'k' or 'M' or 'G' or 'T' in value, "fail"