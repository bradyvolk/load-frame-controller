# Load Frame and VNA Controller
Author: Brady Volkmann
<br/>
Institution: University of Missouri 
Kansas City
<br/>
Date: 6/28/2019
<br/><br/>

## To create a virtual env from requirements.txt
#### With Anaconda:
	conda create --name <env> --file requirements.txt
#### With pip:
	pip install -r requirements.txt
<br/><br/>

## Notes on about LoadFrameController:
pyLoadFrameController is a script written to control a load frame
consisting of a stepper motor and load cell. Additionally,
the pyLoadControl is meant to also control a TTR506A VNA.
This devices work in union such that the VNA takes a measurement
and the load cell takes a measurement. Then, the stepper motor
turns slightly to increase the force applied by the load frame,
and the process is repeated. The measurements are stored in the same
directory as pyLoadControl in directories named "Graphs/", "Logs/",
and "CSVs/". The data for load cell measurements are stored in the 
"Logs/" and "CSVs/" with the word "load" prepended to the date for
the filename. In the load cell logs, the integers in the left column
correspond to measurement made, and each measurement is made after
motor step. 
<br/><br/>

## Notes on using LoadFrameController:
If you simply want to use the script as intended by the author, 
LoadFrameController is the only file you should concern youself with.
At the bottom of the script under execution, you can create an instance
of the Controller class with the Controller() constructor function.
It's arguments will set the parameters for the experiment. See the definition
of the class towards the top of the file for more detailed information on the 
possible parameters. Once you have created your instance and assigned it to
`<varName>`, use `<varName>.run()` to perform an experiment. Ensure that you've
properly connected your computer to the Arduino and have VectorVU-PC pulled
up with your TTR506A VNA connected to it. Then, when you call 
the script in your terminal, the main loop will run. All data will be
recorded in the subdirectories of the directory that pyLoadFrameController 
is contained in.
<br/><br/>

## Timing:
It is currently pretty slow to take measurements with this setup (~1 minute
for each sweep with typical settings). The main bottleneck is the loadcell
measurements. Each sample with the load cell takes about 15 seconds, and this
long length is mainly rooted in the serial communication. There may be a way to
shorten this, but it is not clear to me how at the moment. The motor turns and
the VNA sweep take around 5 seconds each. The delays through `time.sleep(<seconds>)`
account for all these timings. I've tried to optimize it to be as fast as possible,
but it could possibly be improved. It is very easy to make the program non-
functional by adjusting the timings, so be advised.
<br/><br/>

## Possible formats for data output:

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
* Plug Laptop into VNA via USB port
* Plug Laptop into Arduino via USB port
* Turn on controls hardware by plugging  24V DC power supply
	into the side of the junction box
<br/><br/>

## Controls Hardware:  
* Arduino Uno R3
* POWERMAX II P22NRXC-LNN-NS-02 Stepper Motor
TB6560 V2 Stepper Motor Driver
* Hx711 Amplifier https://github.com/aguegu/ardulibs/tree/master/hx711 and full shield https://www.amazon.com/gp/product/B010FG9RXO/ref=ppx_yo_dt_b_asin_title_o00_s00?ie=UTF8&psc=1
* Load Cell https://www.amazon.com/gp/product/B077YHNNCP/ref=ppx_yo_dt_b_asin_title_o07_s00?ie=UTF8&psc=1
<br/><br/>

## Controls Software:
* VectorVU-PC:  https://www.tek.com/vna/ttr500
* Programming Manual for TTR506A: https://download.tek.com/manual/TTR500-Programmer-Manual-077125700.pdf
<br/><br/><br/>

Any Questions? Email bvv4@cornell.edu

Good luck
-Brady 
