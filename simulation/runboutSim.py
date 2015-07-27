#!/usr/bin/env python

from boututils import shell, launch, getmpirun
import sys, os, ConfigParser, shutil
from datetime import *


configfile = '//hwdisks/data/bd512/sol1d-scans/5e8/config/config.ini'
parser = ConfigParser.ConfigParser()
parser.read(configfile)
exe = parser.get('exe', 'path')
archive = parser.get('archive', 'path')
MPIRUN = getmpirun()
nargs = len(sys.argv)
runid = sys.argv[1] # First argument is the Archive ID to load
restart = sys.argv[2]

print runid

if nargs < 3:
    # prints help if arguements aren't given
    print("Format is: ")
    print("  %s <run id> [directory]")
    print("     directory - optional, default is 'tmp'")
    sys.exit(1)

# Unless an arguement is given a temporary folder is created to run in
if nargs > 3:
    directory = sys.argv[3]
else:
    directory = 'tmp'


# Confirms location of BOUT++ archive
try:
    archive = os.environ["BOUTARCHIVE"]
except KeyError:
    # No environment variable. Use default
    archive = '/hwdisks/home/jh1479/BOUT-dev/archive/'

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

#JOE ADDED THIS
def removeTiming(loadpath):
    f = open(loadpath, 'r')
    filedata = f.read()
    f.close()

    newdata = filedata.replace('[timing]','')
    print filedata, loadpath


    with open(loadpath, 'w') as File:
        File.write(newdata)
        File.close()

# Inport inputs into the temporary directory ???
inputfiles = os.listdir(runid)
for runfiles in inputfiles:
    filepath = os.path.join(runid, runfiles)
    if os.path.isfile(filepath):
        shutil.copy(filepath, directory)
removeTiming(directory+'/BOUT.inp')

        

# Runs the bout code with the option of using restart files
# JOE changes this so that y/n was added as an argument, needed changing to work with GUI


cmd = exe + ' -d ' + directory + '/'
#print("Command = '%s'" % cmd)
if restart == 'y':
    launch(cmd + ' restart', nproc = 5, nice = 10)
else:
    launch(cmd, nproc = 5, nice = 10, pipe=False)








# Save files from tmp into the loaded archive file and allows for addition of notes

inputfiles = os.listdir(directory)
for runfiles in inputfiles:
    filepath = os.path.join(directory, runfiles)
    if os.path.isfile(filepath):
        shutil.copy(filepath, runid)

shutil.rmtree('tmp')
sys.exit(0)
