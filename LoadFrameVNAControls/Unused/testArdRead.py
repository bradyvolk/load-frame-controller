"""
testArdRead

Author: Brady Volkmann
Institution: University of Missouri Kansas City
Created: 6/25/2019

Trying Out Reading from Arduino into Python
"""

import serial
import time

ser = serial.Serial('COM6', 9800, timeout=1)
time.sleep(2.5)         # Need a start up time delay 

for _ in range(100):
    print(ser.readline())