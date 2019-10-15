"""
LoadFrameController.py
Author: Brady Volkmann
Institution: University of Missouri Kansas City
Created: 6/25/2019
Edited: 7/3/2019
Python 3.6.0 64-bit (Anaconda 4.3.0)
Additional Required Software: 
    VectorVU-PC:  https://www.tek.com/vna/ttr500
    PyVISA: pip install pyvisa
Programming Manual for TTR506A: https://download.tek.com/manual/TTR500-Programmer-Manual-077125700.pdf

This file contains the controller for the load frame as a whole
by linking the controls for the stepper motor, load cell, and
TTR506 VNA. This file is intended to fully automate VNA measurements
at incremental motor steps.

Controls Hardware:  Arduino Uno R3
                    POWERMAX II P22NRXC-LNN-NS-02 Stepper Motor
                    TB6560 V2 Stepper Motor Driver
                    Hx711 Amplifier (https://github.com/aguegu/ardulibs/tree/master/hx711) and full shield (https://www.amazon.com/gp/product/B010FG9RXO/ref=ppx_yo_dt_b_asin_title_o00_s00?ie=UTF8&psc=1)
                    Load Cell (https://www.amazon.com/gp/product/B077YHNNCP/ref=ppx_yo_dt_b_asin_title_o07_s00?ie=UTF8&psc=1)

To see how to run this file in detail, visit the README loacted
in the same directory as this file.

TL;DR:
    Go to bottom to the execution section, create an instance of controller
    with desired parameters for experiment, and use the .run() method 
    on the instance.

For confusions/questions/complaints: contact bvv4@cornell.edu
"""

# IMPORTS ===================================================================
import ttrvna as vna
import pyMotorControl as mc
import pyLoadControl as lc
import matplotlib as plt
import time
import serial

# CONTROLLER ================================================================
class Controller(object):
    """
    The Controller class is used to control the stepper motor, load cell, and
    TTR506 VNA all from one class.

    Attributes:
        motor           : Motor         : Motor instance to control stepper motor
        vna             : Ttrvna        : Ttrvna instance that controls VNA
        loadcell        : LoadCell      : LoadCell instance that controls reading data from laod cell
        trials          : int           : number of trials the experiment runs for
        stepSize        : float         : size of step set on stepper motor
        degrees         : float > 0     : number of degrees to turn
        byStep          : bool          : True if stepping by steps
        loadAvg         : int > 0       : number of samples to take for each load cell average
        forceStep       : float/int > 0 : if stepping by force, this is the step size
        _ser            : Serial        : establishes serial communication for experiment
    """


    def __init__(self,com,start=None,stop=None,delay=None,sParam=None,trials=None,format='mlogarithmic',
                            stepSize=1,degrees=1,byStep=False,baseStep=None,loadAvg=3,forceStep=None):
        """
        Constructor that initializes attributes of Controller instance
        
        Parameters:
                com             : str               : sets communication port for Arduino (e.g. 'COM6')
                start           : str as SI unit    : determines start frequency for frequency sweep
                stop            : str as SI unit    : determines stop frequency for frequency sweep
                delay           : str as SI unit    : determines delay between each sweep
                sParam          : str               : determines which S Parameter is measured
                trials          : int > 0           : determines the number of trials/sweeps
                format          : str               : determines format for the data to be outputted into
                stepSize        : float > 0         : determines step size of motor
                degrees         : float > 0         : number of degrees to turn
                byStep          : bool              : determines if stepping by steps
                baseStep        : float > 0         : sets base step size at full step in degrees
                loadAvg         : int > 0           : number of samples to take for each load cell average
                forceStep       : float/int > 0     : if stepping by force, this is the step size in N
        """
        self.setVNA(start=start,stop=stop,delay=delay,sParam=sParam,trials=trials,format=format)
        self._ser = serial.Serial(com,9800,timeout=1)
        self.setMotor(self._ser,stepSize,baseStep)
        self.setDegrees(degrees)
        self.setByStep(byStep)
        self.setLoadcell(self._ser)
        self.setLoadAvg(loadAvg)

        if trials is not None:
            self.setTrials(trials)
            if forceStep is not None:
                self.setForceStep(forceStep)
            

    def setVNA(self,start,stop,delay,sParam,trials,format):
        """
        Setter for vna attribute to control VNA.
        Preconditions are enforced in Ttrvna class

        Parameters:
                start        : str as SI unit    : determines start frequency for frequency sweep
                stop         : str as SI unit    : determines stop frequency for frequency sweep
                delay        : str as SI unit    : determines delay between each sweep
                sParam       : str               : determines which S Parameter is measured
                trials       : int > 0           : determines the number of trials/sweeps
                format       : str               : determines format for the data to be outputted into
        """
        self.vna = vna.Ttrvna(start=start,stop=stop,delay=delay,sParam=sParam,trials=trials,format=format)


    def setMotor(self,ser,stepSize,baseStep=None):
        """
        Setter for motor attribute to control stepper motor via Arduino
        
        Parameters:
                ser             : Serial            : establishes serial communication for motor
                stepSize        : float > 0         : determines step size of motor
        """
        if baseStep is not None:
            self.motor = mc.Motor(ser,stepSize,baseStep)
        else:
            self.motor = mc.Motor(ser,stepSize)

    
    def setLoadcell(self,ser):
        """
        Setter for load cell attribute to read data from load cell via Arduino

        Parameters:
                ser     : Serial       : establishes serial communication for experiment
        """
        self.loadcell = lc.LoadCell(ser)


    def setTrials(self,trials):
        """
        Setter for trials attribute to determine how many
        tests are done.

        Parameters:
                trials  : int > 0 : number of trials/tests
        """
        assert type(trials) == int
        assert trials > 0

        self.trials = trials


    def setDegrees(self,degrees):
        """
        Setter for degrees attribute to determine how many degrees
        to turn between each trial.

        Parameters:
                degrees : float, int > 0 : degrees to turn
        """
        assert type(degrees) == float or int
        assert degrees > 0
        self.degrees = degrees

    
    def setByStep(self, byStep):
        """
        Setter for byStep attribute to determine if stepping
        by steps.

        Parameters:
                byStep : bool : step by steps or not
        """
        assert type(byStep) == bool

        self.byStep = byStep

    
    def setLoadAvg(self,loadAvg):
        """
        Setter for loadAvg attribute to determine the number
        of samples the load cell should take to determine the
        average for each measurement.

        Parameters:
                loadAvg : int > 0 : number of samples to take for each load cell average
        """
        assert type(loadAvg) == int
        assert loadAvg > 0

        self.loadAvg = loadAvg
    

    def setForceStep(self, forceStep):
        """
        Setter for forceStep attribut to determine size of steps
        if stepping by force instead of by motor turns.

        Paramters:
                forceStep : float/int > 0 : step
        """
        # Load frame cannot is not rated for mroe than 1000 N
        assert type(forceStep) == int or float
        assert forceStep > 0
        assert forceStep*self.trials <= 1000
        self.forceStep = forceStep


    def tuneForForce(self,forceDesired):
        """
        Turns the motor until the desired force is reached 
        and read by the load cell.
        Gets desired force within 1 N. 
        """
        assert type(forceDesired) == int or float
        min = forceDesired - 1
        max = forceDesired + 1
        self.loadcell.doRead()
        time.sleep(1)
        self.loadcell.takeMeasurement(self.loadAvg,False)
        current = self.loadcell.allData[len(self.loadcell.allData)-1][1]
        time.sleep(3)

        # Step forward until load cell reading is greater than min
        while current <= min or current >= max:
            if current <= min:
                print('less')
                print(current)
                self.motor.doStep()
                time.sleep(1)
                self.loadcell.takeMeasurement(self.loadAvg,False)
                current = self.loadcell.allData[len(self.loadcell.allData)-1][1]
        # Step backward until load cell reading is less than max
            if current >= max:
                print('greater')
                self.motor.changeDirection()
                print(current)
                self.motor.doStep()
                time.sleep(1)
                self.loadcell.takeMeasurement(self.loadAvg,False)
                current = self.loadcell.allData[len(self.loadcell.allData)-1][1]          
                self.motor.changeDirection()

        
    def runByDeg(self):
        """
        Runs the experiment by stepping by degrees after a controller has been constructed 
        """
        # Dud trial to set up the experiment because first trial is always incorrect with this set up
        self.vna.makeSweep()    
        print('Beginning Collection')
        if self.byStep:
            for _ in range(self.trials):
                self.loadcell.takeMeasurement(self.loadAvg)
                time.sleep(2)
                self.vna.makeSweep()
                time.sleep(1)
                self.motor.doStep()
        else:
            for _ in range(self.trials):
                self.loadcell.takeMeasurement(self.loadAvg)
                time.sleep(2)
                self.vna.makeSweep()
                time.sleep(5)
                self.motor.turnByDeg(self.degrees)
                time.sleep(1)
        self.loadcell.saveData()
        print('Done!')

    
    def runByForce(self):
        """
        Runs the experiment by stepping by force after a controller has been constructed 
        """
        # Dud trial to set up the experiment because first trial is always incorrect with this set up
        assert self.trials is not None
        assert self.forceStep is not None
        self.vna.makeSweep() 
        forceDesired = 0
        for _ in range(0,self.trials*self.forceStep,self.forceStep):
            self.tuneForForce(forceDesired)
            self.loadcell.takeMeasurement(self.loadAvg)
            time.sleep(2)
            self.vna.makeSweep()
            time.sleep(5)
        self.loadcell.saveData()
        print('Done!')
        

# EXECUTION =======================================================
if __name__ == "__main__":
    """
    If did this well, the few lines below should be the only things you need 
    to change to do an experiment
    """
    test = Controller(com='COM6',start='50 MHz', stop='6 GHz', delay='8s', sParam='S21', trials=3, format='mlogarithmic',
                                stepSize=1,degrees=45,byStep=False,baseStep=None,loadAvg=2,forceStep=5)
    test.runByForce()