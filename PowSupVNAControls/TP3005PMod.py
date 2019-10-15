"""
TP3005PMod.py
Author: Circumflex Designs
Modified by: Brady Volkmann
Institution: University of Missouri Kansas City
Last Edit: 7/15/2019

http://www.circumflex.systems/2017/06/controlling-tekpower-tp3005p-power.html

Used to control TP3005P power supply. See VNAandPowSup.py if you
want to control power supply with VNA.
"""

# IMPORTS =================================
import serial
import time

# PowSup ==================================

class PowSup(object):
    """
    Class for PowSup object. Used to control TP3005P
    power supply.

    Attributes:
            serTP               : Serial                : Establishes serial communication with TP 305P
            serArd              : Serial                : Establishes serial communication with Arduino
            voltageStep         : float or int > 0      : the number of volts to step between each trial
            _voltages           : list of floats/ints   : any voltages measured in the instance of this object
    """
    
    def __init__(self,comTP,comArd=None,voltageStep=None,initialVoltage=None):
        """
        Constructor for PowSup class. Sets output state to true 

        Parameters:
                comTP           : str                       : com for serial communications with TP (e.g. 'COM7')
                comArd          : str                       : com for serial communication with Ard
                voltageStep     : float or int > 0          : the number of volts to step between each trial
                initialVoltage  : 0 <= float or int <= 30   : intial voltage if run a set of trials

        """
        
        self.setSerTP(comTP)
        if comArd is not None:
            self.setSerArd(comArd)
        self.outputState(True)
        self._voltages = []   
        time.sleep(1.5)

        if voltageStep is not None:
            assert type(voltageStep) == float or int
            assert voltageStep > 0
            self.voltageStep = voltageStep

        if initialVoltage is not None:
            assert type(initialVoltage) == float or int
            assert initialVoltage >= 0 
            assert initialVoltage <= 30
            self.voltsSetpointSet(initialVoltage)
 

    def setSerTP(self,comTP):
        """
        Setter for serTP attribute for serial communications and clears buffers
        in serial communications
                comTP     : str    : com for serial communications (e.g. 'COM7')
        """
        assert type(comTP) == str
        self.serTP = serial.Serial(comTP, 9600, timeout=1)
        self.serTP.reset_input_buffer()
        self.serTP.reset_output_buffer()

    
    def setSerArd(self,comArd):
        """
        Setter for serArd attribute for serial communications
                comArd     : str    : com for serial communications (e.g. 'COM7')
        """
        assert type(comArd) == str
        self.serArd = serial.Serial(comArd, 9600, timeout=1)

    
    def getVoltages(self):
        """
        Getter for _voltages

        Returns: _voltages as list
        """
        return self._voltages


    def serClose(self):
        """
        Closes serial communications
        """
        self.serTP.close()


    def outputState(self,var):
        """
        Determines if output state of TP3005P
        is on or off.

        Parameters:
                var : bool : True if output on
        """
        time.sleep(0.05)
        if var == True:
            cmd = b'OUTPUT1:\\r\\n'
            # print("Output On")
        else:
            cmd = b'OUTPUT0\\r\\n'
            # print ("Output Off")
        self.serTP.write(cmd)
        time.sleep(0.05)


    def voltsSetpointSet(self,volts):
        """
        Sets voltage of TP3005P

        Parameters:
                volts : float or int >= 0 : voltage to set to
        """
        assert type(volts) == float or int
        assert volts >= 0

        time.sleep(0.05)
        cmd = b'VSET1:'                      #b'VSET1:07.00\\r\\n'
        cmd = cmd + format(volts, "=05.2F").encode('ascii')
        cmd = cmd + b'\\r\\n'
        self.serTP.write(cmd)


    def voltsSetpointGet(self):
        """
        Gets current voltage of TP3005P is set for

        Returns: voltage as float
        """
        time.sleep(0.05)
        cmd = b'VSET1?\\r\\n'
        self.serTP.write(cmd)
        line = self.serTP.readline()
        volts = float(line.decode('utf8'))
        return volts


    def voltsMeas(self):
        """
        Measures current voltage of TP3005P

        Returns: voltage as float
        """
        time.sleep(0.05)
        cmd = b'VOUT1?\\r\\n'
        self.serTP.write(cmd)
        line = self.serTP.readline()
        volts = float(line.decode('utf8'))
        return volts


    def ampsSetpointSet(self,amps):
        """
        Sets amperage on TP3005P

        Parameters:
                amps    : float or int >= 0 : amps to set to 
        """
        time.sleep(0.05)
        cmd = b'ISET1:'                      #b'ISET1:2.500\\r\\n'
        cmd = cmd + format(amps, "=05.3F").encode('ascii')
        cmd = cmd + b'\\r\\n'
        self.serTP.write(cmd)


    def ampsSetpointGet(self):
        """
        Gets current amperage of TP3005P is set for

        Returns: amps as float
        """
        time.sleep(0.05)
        cmd = b'ISET1?\\r\\n'
        self.serTP.write(cmd)
        line = self.serTP.readline()
        amps = float(line.decode('utf8'))
        return amps

    def ampsMeas(self):
        """
        Measures current amperage of TP3005P

        Returns: amperage as float
        """
        time.sleep(0.05)
        cmd = b'IOUT1?\\r\\n'
        self.serTP.write(cmd)
        line = self.serTP.readline()
        amps = float(line.decode('utf8'))
        return amps


    def statusGet(self):
        """
        Gets status of TP3005P

        Returns: status as int
        """
        time.sleep(0.05)
        cmd = b'STATUS?\\r\\n'
        self.serTP.write(cmd)
        line = self.serTP.readline()
        status = int(line.decode('utf8'))
        return status


    def incrementVolt(self,val,recorded=False):
        """
        Increment or decrement current voltage of TP3005P by val

        Parameters:
                val     : float or int  : value to increment/decrement voltage by 
                recorded: bool          : checks if voltage has already been recorded
        """
        assert type(val) == float or int

        if not recorded:
            self._voltages.append(self.voltsMeas())
        current = self.voltsSetpointGet()
        new = current + val
        assert new <= 30
        assert new >= -30
        self.voltsSetpointSet(new)


    def doTrial(self):
        """
        Measures voltages and appends it do self.voltages and increments the set voltage per val
        
        Parameters:
                val     : float or int  : value to increment/decrement voltage by 
        """
        time.sleep(1.5)
        self._voltages.append(self.voltsMeas())
        self.incrementVolt(self.voltageStep,recorded=True)
    
    
    def changePolarity(self):
        """
        Switches the polarization on the power supply by swapping the wires
        around with a relay.
        """
        self.serArd.write(b'P')

        
# Execution ====================================================================
if __name__ == "__main__":
    test = PowSup('COM7','COM6',voltageStep=3,initialVoltage=2)
    test.voltsSetpointSet(1)
    # time.sleep(20)
    # test.changePolarity()
    time.sleep(5)
    test.voltsSetpointSet(0)







