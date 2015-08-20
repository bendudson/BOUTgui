![](https://github.com/joe1510/BOUTgui/blob/master/BOUTguilogo.png
## Introduction

BOUT++ is a 3D plasma fluid simulation code which has been developed at York in collaboration with the MFE group at LLNL and the MCS division at ANL. Different models are created for different scenarios with different assumptions being made in each. These models are written using this BOUT++ code. For further information see http://www-users.york.ac.uk/~bd512/bout/ . To run a simulation requires a control file (BOUT.inp) containing all the physical and non-physical variables to be linked to the simulation code that describes the specific model, written using BOUT++. Once the simulation is finished the data files and log files are copied to the folder containing the BOUT.inp file. Data then is analysed separately using a python code based on matplotlib called plotdata which comes as part of the BOUT data routines. In the past all of this was run within a linux terminal. 

The GUI was developed alongside a command line application with the aim to streamline this process, making everything more connected and the code a lot easier to use. It combines data analysis and data creation all within one application. It is has also been designed with data archiving in mind. Information about each run stored to aid the user when coming back to old runs and remember what changes were made and what the history of each data file is. This should make long term research easier, particularly if old data is requested for some reason. 

## Quick Installation Guide:

1) Download the tar archive from GitHub

2) Un-tar into the chosen folder, e.g. tar xvzf BOUTgui.tar.gz /hwdisks/home/username/BOUTgui

3) Can ignore all files except BOUTgui.py which is the main application file when running

4) Run the GUI by using ./BOUTgui.py once changed into the BOUTgui folder

**For help open the Installation and Running Guide (pdf) stored within the tar archive.**


