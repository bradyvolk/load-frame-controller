"""
Author: Brady Volkmann
Institution: University of Missouri Kansas City
Created: 7/24/2019
Edited: 7/24/2019
Python 3.6.0 64-bit (Anaconda 4.3.0)
"""

# IMPORTS ===================================
import serial
import time
import instrument as instr

# StrainGauge =================================
class StrainGauge(instr.Instrument):
    """
    """
    def __init__(self,com,rOne=121.1,rTwo=120.7,rThree=120.6,vEx=4.189,sgInitalRes=120.3,gf=1.84):
        """
        """
        assert type(com) == str 
        assert type(rOne) == int or float; assert type(rTwo) == int or float 
        assert type(rThree) == int or float; assert type(vEx) == int or float
        assert type(sgInitalRes) == int or float; assert type(gf) == int or float

        self.rOne = rOne
        self.rTwo = rTwo
        self.rThree = rThree
        self.vEx = vEx
        self.sgInitalRes = sgInitalRes
        self.gf = gf
        self._ser = serial.Serial(com,9800,timeout=1)
        self._voltages = []
        self._strains = []
  
    
    def averageRead(self,numReads):
        """
        """
        values = []
        # value = str(self._ser.read(6))
        for _ in range(numReads):
            value = str(self._ser.read(6))
            if value != "b''":
                pos = value.find('\\')
                value = float(value[2:pos])
                values.append(value)
            time.sleep(1)
        self._voltages.append((sum(values)/len(values))/1000)
    
    def getStrains(self):
        """
        """
        for voltage in self._voltages:
            top = self.rThree*(self.rOne + self.rThree)*self.vEx
            bottom = voltage*self.rOne + voltage*self.rTwo + self.rTwo*self.vEx
            measuredResistance = (top/bottom) - self.rThree
            strain = (self.sgInitalRes-measuredResistance)/self.gf
            self._strains.append(strain)





# EXECUTION ===================================
if __name__ == "__main__":
    test = StrainGauge('COM6')
    for _ in range(10):
        test.averageRead(10)
        print(test._voltages)
    test.getStrains()
    print(test._strains)
