#!/usr/bin/env python

from boututils import shell, launch, getmpirun
import sys, os, ConfigParser, shutil, fileinput
from tempfile import mkstemp
from os import remove
from shutil import move
from datetime import *
from guifunctions import *


# get current working directory
currentDir = os.getcwd()
config = currentDir + '/config/config.ini'

# read the config file
parser = ConfigParser.ConfigParser()
parser.read(config)
# collect exe and archive and editor
exe = parser.get('exe', 'path')
archive = parser.get('archive', 'path')
editor = parser.get('text editor', 'editor')
MPIRUN = getmpirun()
# find the number of arguments
nargs = len(sys.argv)



# form of arguments: runid, key, subkey, initial, limit, increment, scanType, restart, initial2, limit2, key2, subkey2, increment2
# it is not necessary to have all the arguments, the "two's" make a twin scan where it increases one variable and then the other.

# read all the arguments
runid = sys.argv[1] + '/'

key = '[' + sys.argv[2] + ']'
if key == '[timing]':
  key = ''

subkey = sys.argv[3]

a = sys.argv[4]
initial = float(a)

                 
b = sys.argv[5]
limit =float(b)
                 
c = sys.argv[6]
increment = float(c)

restart = sys.argv[7]


incrementType = sys.argv[8]

scanType = sys.argv[9]

proc = sys.argv[10]

nicelvl = sys.argv[11]

# should a second set of scanning variable be given then this is called, this is defined by whether increment2 = None, these are ignored if not

if str(sys.argv[16]) != 'NONE':
  initial2 = sys.argv[12]
  initial2 = float(initial2)

  limit2 = sys.argv[13]
  limit2 = float(limit2)

  key2 = '[' + sys.argv[14] + ']'
  if key2 == '[timing]':
    key2 = ''
    

  subkey2 = sys.argv[15]

  increment2 = sys.argv[16]
  increment2 = float(increment2)

# if nargs < 12 then there aren't enough arguments to run a simulation
if nargs < 12:
    # prints help if arguments aren't given
    print("Format is: ")
    print("  %s <run id> [directory]")
    print("     directory - optional, default is 'tmp'")
    sys.exit(1)

# Unless an arguement is given a temporary folder is created to run in
if nargs > 12:
    directory = sys.argv[2]
else:
    directory = 'tmp'


# Confirms location of BOUT++ archive
try:
    archive = os.environ["BOUTARCHIVE"]
except KeyError:
    # No environment variable. Use default
    defaultArchive = os.getcwd() + '/Archive'
    if not os.path.isdir(defaultArchive):
        os.makedirs(defaultArchive)
    archive = defaultArchive

# Checks for a valid archive ID
def rundirectory(runid):   
    if os.path.exists(runid):
        print 'Valid runid', runid
    else:
        print 'Invalid runid', runid
        sys.exit(0)

# Makes a new directory called "tmp"
shell("mkdir " + directory) 
sourcedirectory = rundirectory(runid)



### directory = the runid
loadpath = directory + '/BOUT.inp'
loadfrom = runid

def scanPOWER(initial, limit, restart, loadpath, key, subkey, increment):
    
    global i, loadfrom
    inputfiles = os.listdir(loadfrom)
    for runfiles in inputfiles:
        filepath = os.path.join(loadfrom, runfiles)
        if os.path.isfile(filepath):
            shutil.copy(filepath, directory)
    # fixes headings back into the control files so the BOUT can understand them        
    returnHeadings(directory + '/BOUT.inp')
   
    #npro = raw_input('N.o of processors to use: ')
    cmd = exe + ' -d ' + directory + '/'
    print("Command = '%s'" % cmd)
    th, temp = mkstemp()
    with open(temp,'w') as g:
        with open(loadpath, 'r') as f:
            for line in f:
                if line.startswith(key):
                    g.write(line)
                    for line in f:
                        if line.startswith(subkey):
                            string = line.split()
                            a = string[string.index('=') + 1]
                            if i < 2:
                              final = initial

                            # this determines whether raw or percentage increase
                            elif incrementType == '+':
                              final = initial + increment
                              initial = final
                            else:
                              final = initial * increment
                              initial = final
                            b = str(final)
                            new = line.replace(a, b)
                            initial = final
                            g.write(new)
                            break
                        else:
                            g.write(line)
                else:
                    g.write(line)
            g.close()
    remove(loadpath)
    move(temp, loadpath)
    # runs the simulation, adds restart command if necessary
    if restart == 'y':
        launch(cmd + ' restart', nproc = proc, nice = nicelvl)
    else:
        launch(cmd, nproc = proc, nice = nicelvl, pipe=False)
    return initial


def run2(initial, limit, restart, loadpath, key, subkey, increment, initial2, limit2, key2, subkey2, increment2, scanType):
        """
        run2 has two differnt scanTypes which are chosen by the user in the GUI. They behave differently. The first is a powerup type of scan
        which is used when two different parameters need to be increased or reduced roughly proportionally to one another such as when increasing the
        power of a beam the powerflux also needs to be increased roughly in step with it. This makes the power up process an automatic one. The second
        is called full and is designed so that one paramter is slowly increased and for each increase step of that parameter the other parameter is run of the full
        range. This is useful for testing system behaviour over a range of values. 
        """
        # defines the initial conditions according to the arguments given by the GUI
        newinitial1 = initial
        newinitial2 = initial2
        limit1 = limit
        global i
        i =1
        # if i = 1 then inital is used by scan(), if i > 1 then initial + (or *) increment is used by scan 

        # for doing power up scans 
        if scanType == 'power':
            # uses the limit of the first variable as the overall limit.
            # for increasing increments
            if initial < limit1:
                while newinitial1 < limit1:
                    # a is the returned initial value
                    a = scanPOWER(newinitial1, limit, restart, loadpath, key, subkey, increment)
                    newinitial1 = float(a)
                    # new folder routine for each run
                    createfolder(subkey, newinitial1)
                    # For every increase in initial1 then initiail2 is also run and increased in step
                    b = scanPOWER(newinitial2,limit2,restart, loadpath, key2, subkey2, increment2)
                    newinitial2 = float(b)
                    createfolder(subkey2, newinitial2)
                    i += 1
                  
            else:
                # for decreasing increments
                while newinitial1 > limit1:
                  # exactly the same as above only the limits are the other way around
                    a = scanPOWER(newinitial1, limit, restart, loadpath, key, subkey, increment)
                    newinitial1 = float(a)
                    createfolder(subkey, newinitial1)
                    # For every increase in initial1 then initiail2 is also run and increased in step
                    b = scanPOWER(newinitial2,limit2,restart, loadpath, key2, subkey2, increment2)
                    newinitial2 = float(b)
                    createfolder(subkey2, newinitial2)
                    i += 1
  
        # for doing full scans             
        if scanType == 'full':
            # does an initial run with the first parameter setup
            a = scanPOWER(newinitial1, limit, restart, loadpath, key, subkey, increment)
            newinitial1 = float(a)
            createfolder(subkey, newinitial1)
            # initial lower the limit
            if initial < limit1:
                while newinitial1 < limit1:
                    # the main while loop is used to slowly step up the first parameter by increment1
                    newinitial2 = initial2
                    # newinitial2 has to be reset on each loop
                    while newinitial2 < limit2:
                      # this while loop then runs the second parameter from initial2 to limit2 with all increment steps 
                        b = scanPOWER(newinitial2,limit2,restart, loadpath, key2, subkey2, increment2)
                        newinitial2 = float(b)
                        createfolder(subkey2, newinitial2)
                        i += 1
                    # this then runs the next step of the first parameter and resets i
                    a = scanPOWER(newinitial1, limit, restart, loadpath, key, subkey, increment)
                    newinitial1 = float(a)
                    createfolder(subkey, newinitial1)
                    i = 1
                #  this final loop exists because the final test of the second parameter didn't happen as the criteria of main while loop has been met
                newinitial2 = initial2
                
            else:
                # initial higher than limit
                while newinitial1 > limit1:
                    # the main while loop is used to slowly step up the first parameter by increment1
                    newinitial2 = initial2
                    # newinitial2 has to be reset on each loop
                    while newinitial2 > limit2:
                      # this while loop then runs the second parameter from initial2 to limit2 with all increment steps 
                        b = scanPOWER(newinitial2,limit2,restart, loadpath, key2, subkey2, increment2)
                        newinitial2 = float(b)
                        createfolder(subkey2, newinitial2)
                        i += 1
                    # this then runs the next step of the first parameter and resets i
                    a = scanPOWER(newinitial1, limit, restart, loadpath, key, subkey, increment)
                    newinitial1 = float(a)
                    createfolder(subkey, newinitial1)
                    i = 1
                #  this final loop exists because the final test of the second parameter didn't happen as the criteria of main while loop has been met
                newinitial2 = initial2

            # accoounts for all posibilities, so can have one increment of increase and one an increment of decrease. 
            if newinitial2 < limit2: 
                while newinitial2 < limit2:
                    b = scanPOWER(newinitial2,limit2,restart, loadpath, key2, subkey2, increment2)
                    newinitial2 = float(b)
                    createfolder(subkey2, newinitial2)
                    i += 1
            else:
                while newinitial2 < limit2:
                    b = scanPOWER(newinitial2,limit2,restart, loadpath, key2, subkey2, increment2)
                    newinitial2 = float(b)
                    createfolder(subkey2, newinitial2)
                    i += 1



def run1(initial, limit, restart, loadpath, key, subkey, increment):
        # this is run if not sufficient arguments are given for two runs, it should be scanType independent
        newinitial1 =initial
        limit1 = limit
        # i is global because this means that scanPOWER knows how many times the code has been round 
        global i
        i =1
        # code here is very similiar to above
        if newinitial1 < limit1:
            while newinitial1 < limit1:
              a = scanPOWER(newinitial1, limit, restart, loadpath, key, subkey, increment)
              newinitial1 = float(a)
              createfolder(subkey, newinitial1)
              i += 1
        else:
            while newinitial1 > limit1:
              a = scanPOWER(newinitial1, limit, restart, loadpath, key, subkey, increment)
              newinitial1 = float(a)
              createfolder(subkey, newinitial1)
              i += 1      
        
def createfolder(subkey, initial):      
    inputfiles = os.listdir(directory)
    list.sort(inputfiles)
    x = 1
    archive = (os.path.dirname(os.path.dirname(runid)))
    # creates the name of the new folder using the subkey and value of that subkey used in that simulation
    newfolder = str(archive) + '/' + str(subkey) + '.' + str(initial) + '.' + str(x) + '/'


    while os.path.isdir(newfolder):
        x = x + 1
        newfolder = str(archive) + '/' + str(subkey) + '.' + str(initial) + '.' + str(x) + '/'
    else:
        shell("mkdir " + newfolder)
      # copies all the files across to a new folder
    for file in inputfiles:
        # copies control file, log, restart and dmp files as all start with BOUT.
        if file.startswith('BOUT.'):
            filepath = os.path.join(directory, file)
            if os.path.isfile(filepath):
                shutil.copy(filepath, newfolder)
        # copies the record file
        if file.startswith('record.'):
            filepath = os.path.join(directory, file)
            if os.path.isfile(filepath):
                shutil.copy(filepath, newfolder)
        # copies the usernotes file
        if file.startswith('usernotes.'):
            filepath = os.path.join(directory, file)
            if os.path.isfile(filepath):
                shutil.copy(filepath, newfolder)
    global loadfrom
    loadfrom = newfolder  

try:
  if sys.argv[16]!= 'NONE':
    run2(initial, limit, restart, loadpath, key, subkey, increment, initial2, limit2, key2, subkey2, increment2, scanType)
  else:
    run1(initial, limit, restart, loadpath, key, subkey, increment)

    
    
except KeyboardInterrupt:
    print 'User Exit'
    shutil.rmtree('tmp')
    # should this rmtree be swapped for a call to createfolder(subkey, initial)
    sys.exit(0)

