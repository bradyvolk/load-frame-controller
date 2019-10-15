import serial
import time

ser = serial.Serial('COM6', 9800, timeout=1)
ser.write(b'L')

def blink(numBlinks):
    accum = 0
    while accum < numBlinks:
        ser.write(b'L')
        time.sleep(0.05)
        ser.write(b'H')
        time.sleep(0.05)
        accum += 1

var = int(input("Number of blinks desired: "))
blink(var)

ser.write(b'L')