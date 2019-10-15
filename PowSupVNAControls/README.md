# Power Supply and VNA Controller
Author: Brady Volkmann
<br/>
Institution: University of Missouri Kansas City
<br/>
Date: 7/15/2019
Edited: 7/22/2019
<br/><br/>

## To create a virtual env from requirements.txt
#### With Anaconda:
	conda create --name <env> --file requirements.txt
#### With pip:
	pip install -r requirements.txt
<br/><br/>

## Notes on about VNAandPowSup.py:
VNAandPowSup was written to control a TP3005P Power Supply
and a TTR506A VNA such that a measurement is taken with the 
VNA after each increment in voltage on the power supply. 
The plot frequency vs instensity/response with a legend
for different voltages is then saved in a file labeled 'Graphs/' 
in the same directory as this README.md.
<br/><br/>

## Notes on using VNAandPowSup.py:
If you simply want to use the script as intended by the author, 
VNAandPowSup.py is the only file you should concern youself with.
At the bottom of the script under execution, you can create an instance
of the PowSupVNA class with the PowSupVNA() constructor function.
It's arguments will set the parameters for the experiment. See the definition
of the class towards the top of the file for more detailed information on the 
possible parameters. Once you have created your instance and assigned it to
`<varName>`, use `<varName>.sweepUp()` to perform an experiment if you want to step
voltages monotonically by a step size determined by `<varName>.voltageStep`. If
you want to step up to 15 V, back to 0V, down to -15V, and back to 0V by an interval
determined by `<varName>.voltageStep`, use `<varName>.sweepUpDown()`. If you want to
sweep up from -15V to 15V by `<varName>.voltageStep`, use `<varName>.SweepDownUp()`.
Ensure that you've properly connected your computer to the Power Supply and 
have VectorVU-PC pulled up with your TTR506A VNA connected to it. Then, when you call 
the script in your terminal, the main loop will run. All data will be
recorded in the subdirectories of the directory that this README.md 
is contained in. If you would also like to record Voltage v. Intensity plots at a 
specified frequency, use `<varName>.plotFreqSpecific(<desiredFreq>)` where we will
take the closest approximation to `<desiredFreq>` in the frequency domain and record
the corresponding intensity values to plot against the voltages.
<br/><br/>


## Possible formats for data output for VNA measurements:

Key Phrase	| Meaning
------------|--------------
MLOGarithmic | Log magnitude 
PHASe | Phase 
GDELay | Group delay 
SLINear | Smith chart (Lin/Phase) 
SLOGarithmic | Smith chart (Log/Phase) 
SCOMplex | Smith chart (Real/Imag) 
SMITh | Smith chart (R+jX) 
SADMittance | Smith chart (G+jB) 
PLINear | Polar(Lin/Phase) 
PLOGarithmic | Polar (Log/Phase) 
POLar | Polar (Real/Imag) 
MLINear	| Linear Magnitude 
SWR |
REAL |
IMAGinary | Imaginary 
UPHase | Expanded phase 
PPHase | Positive phase
<br/><br/>

## Hardware set up for those with original design:
* Plug power supply into laptop via USB port
* Plug VNA into laptop via USB port
* Plug Arduino into laptop via USB port for relay to switch to negative polarization
<br/><br/>


## Controls Software:
* VectorVU-PC:  https://www.tek.com/vna/ttr500
* Programming Manual for TTR506A VNA: https://download.tek.com/manual/TTR500-Programmer-Manual-077125700.pdf
* Manual for TP3005P Power Supply: https://tekpower.us/tp3005pmanual.html
<br/><br/><br/>

Any Questions? Email bvv4@cornell.edu

Good luck
-Brady 
