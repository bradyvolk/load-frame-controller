"""
pyMotorControl
Author: Brady Volkmann
Institution: University of Missouri Kansas City
Date Created: 6/17/2019
Date Edited: 6/27/2019
Python 3.6.0 64-bit (Anaconda 4.3.0)

This program controls a stepper motor by writing to the Serial Monitor
of an Arduino 

See LoadFrameController.py if you want to control
the motor in conjunction with a load cell and VNA.
"""

# IMPORTS ============================================================
import serial
import time

# MOTOR ==========================================================

class Motor(object):
    """
    Instance of a motor object used to control a stepper motor by communicating
    serially with an Arduino.

    Attributes:
            stepSize : float > 0        : step size of the stepper motor
            baseStep : float > 0        : size of step in degrees at full step size
            ser      : Serial object    : establishes serial communications
    """

    def __init__(self,ser,stepSize,baseStep=1.8):
        """
        Constructor to initialize motor object

        Parameters:
                ser      : Serial           : establishes communication with Arduino via serial monitor
                stepSize : float > 0        : step size of the stepper motor
                numSteps : int > 0          : number of steps wanted        
        """
        self.setSer(ser)
        self.setStepSize(stepSize)
        self.setBaseStep(baseStep)


    def setSer(self,ser):
        """
        Setter for ser attriubte to establish serial
        communication with Arduino

        Parameters:
                ser : Serial : establishes communication with Arduino via serial monitor
        """
        assert type(ser) == serial.Serial
        self._ser = ser


    def setStepSize(self, stepSize):
        """
        Setter for stepSize attribute to determine size of step
        for stepper motor.

        Must be one of the following sizes:
        1, 0.5, 0.25, 0.125, 0.0625

        Parameter:
                stepSize : float > 0 : size of steps
        """
        assert stepSize in [1,0.5,0.25,0.125,0.0625]

        self.stepSize = stepSize


    def setBaseStep(self,baseStep):
        """
        Setter for base step size attribute in degrees.

        Parameter:
                baseStep : float > 0 : base step size
        """
        assert type(baseStep) == float or int
        assert baseStep > 0
        self.baseStep = baseStep


    def doStep(self):
        """ 
        Steps the motor once by sending an "S" to the serial monitor that the arduino receives
        """
        self._ser.write(b'S')


    def halfTurnMotor(self):
        """
        Turns the stepper motor 180 degrees provided the motor step size is set to 1
        """
        self._ser.write(b'H')


    def turnByStepUser(self):
        """
        Steps the motor based on the number of steps based on
        user input
        """
        steps = int(input("Number of steps desired? "))
        for _ in range(steps):
            self.doStep()
            time.sleep(0.1)


    def turnByDegUser(self):
        """ 
        Steps the motor based the number of degrees desired based
        on user input
        """
        numDeg = int(input("Number of degrees desired? "))
        stepSize = int(input("Step Size? "))
        steps = int(round(numDeg / (self.baseStep * stepSize))) 
        self.turnByStep(steps)


    def turnByStep(self,steps):
        """
        Steps the motor based on the number of steps 

        Parmeters:
                steps : int > 0 : number of steps to step
        """
        assert type(steps) == int
        assert steps > 0

        for _ in range(steps):
            self.doStep()
            time.sleep(0.1)


    def turnByDeg(self,numDeg):
        """ 
        Steps the motor based the number of degrees 

        Parameters:
                numDeg      : int > 0   : number of degrees to turn
        """
        assert type(numDeg) == int
        assert numDeg > 0

        steps = int(round(numDeg / (self.baseStep * self.stepSize))) 
        self.turnByStep(steps)
    

    def changeDirection(self):
        """
        Changes the direction the motor rotates;
        counterclockwise by default
        """
        self._ser.write(b'D')

    
    def _endSerial(self):
        """
        Closes serial communication
        """
        self._ser.close()


# Execution ==================================================================

if __name__ == "__main__":
    mot = Motor(serial.Serial('COM6',9800,timeout=1),1)
    time.sleep(2.5) # Need a start up time delay 
    mot.turnByDegUser()
    time.sleep(5)
    mot._endSerial()
