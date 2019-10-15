"""
pyLoadControl
Author: Brady Volkmann
Institution: University of Missouri Kansas City
Date Created: 6/26/2019
Date Edited: 6/27/2019
Python 3.6.0 64-bit (Anaconda 4.3.0)

This program controls the reading and processing of data from a load
cell through serial communication with an Arduino.

See LoadFrameController.py if you want to control
the load cell in conjuction with a motor and VNA.
"""

# IMPORTS ============================================================
import serial
import time
import numpy as np
import datetime
import csv
import pyMotorControl
import instrument as instr

# LOADCELL ==========================================================

class LoadCell(instr.Instrument):
    """
    Instance of a LoadCell object that controls the reading and processing
    of data from a load cell through serial communication with an Arduino

    Attributes:
            data        : list             : holds data measured if used as a domain
            allData     : list             : holds all data measured
            _filename   : str              : filename for where csv data is logged
            _ser        : Serial           : sets communication port for Arduino
    """

    def __init__(self,ser):
        """
        Constructor initializes instance of LoadCell object

        Parameters:
                ser : Serial Object : establishes communication with Arduino via serial monitor

        """
        self.setSer(ser)
        self._setFilename()
        self.data = []
        self.allData = []


    def setSer(self,ser):
        """
        Setter for ser attriubte to establish serial
        communication with Arduino.

        Parameters:
                ser : Serial Object : sets communication port for Arduino
        """
        assert type(ser) == serial.Serial
        self._ser = ser


    def _setFilename(self):
        """
        Setter for filename. Created to log any data collected
        with the load cell. Format: 'load_' + str<currentDate>
        """
        self._filename = 'load_' + self.getDateFormatted()


    def takeMeasurement(self,samples=3,record=True):
        """
        Averages # of samples read from the loadcell, then
        appends it to data table if record is True. It will always
        append the data to allData because this may need to be accessed
        (e.g. tuneForForce in LoadFrameController.py) but you would not
        want to include in the domain for an experiment measurement since
        it would have no corresponding range.

        Paramter:
                samples : int > 0 : number of samples to average
                record  : bool    : determines if measurement is recorded to self.data
        """
        assert type(samples) == int
        assert samples > 0

        values = []

        time.sleep(10)
        self._ser.flush()
        print(self._ser.read(17))

        # Collect Data
        for _ in range(samples):
            self.doRead()
            time.sleep(20)                      # long sleep needed to receive bytes
            var = str(self.returnRead())        # Now to cut bytes into potential floats
            pos1 = var.find("'")
            pos2 = var.find('\\')
            var = float(var[pos1+1:pos2])
            values.append(var)

        # Average Data
        print(values)
        avg = np.mean(values)
        self.allData.append([len(self.allData)+1,avg])
        if record:
            self.data.append([len(self.data)+1,avg])



    def saveData(self):
        """
        Writes average and dataY to a csv file by making data into table first 
        Titled based on the date.
        The CSV is comma delimited.
        """
        table = self.data

        # Write to CSV
        filename = 'CSVs/' +  self._filename + '.csv'       # csv saved in directory named CSVs located in same directory as this script
        with open(filename, 'w', newline='') as csvfile:
                dataWriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
                for i in range(len(table)):
                        dataWriter.writerow(table[i])
        
        # Write to Log
        filename = 'Logs/' + self._filename + '.txt'   
        f = open(filename, "a+")           # Log saved in directory named Logs located in same directory as this script
        table = []
        for sublist in self.data:
            line = str(sublist[0]) +'\t' + str(sublist[1])
            f.write(line)
            f.write('\n')
                

    def doRead(self):
        """
        Tells the Arduino to take a measurement
        """
        self._ser.write(b'R')

    
    def returnRead(self):
        """
        Pulss the measurement from Arduino in 14 byte increaments

        Returns: 14 bytes read from Arduino
        """
        return self._ser.read(14)
    
    
    def _endSerial(self):
        """
        Closes serial communication
        """
        self._ser.close()
    

# EXECUTION =======================================================
if __name__ == "__main__":
    test = LoadCell(serial.Serial('COM6',baudrate=9800,timeout=10))
    test.takeMeasurement(5)
    test.saveData()