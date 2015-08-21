#!/usr/bin/env python

"""
BOUT gui is designed as a graphical interface for running BOUT++ simulations
    Copyright (C) 2015 authored by Joseph Henderson, Department of Physics, York, jh1479@york.ac.uk

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
from boututils import shell, launch, getmpirun
import sys, os, ConfigParser, shutil, fileinput
from datetime import *
from guifunctions import *


currentDir = os.getcwd()
config = currentDir + '/config/config.ini'

# get all the variables from either the arguments given when this code is run or from the config file
parser = ConfigParser.ConfigParser()
parser.read(config)
exe = parser.get('exe', 'path')
archive = parser.get('archive', 'path')
MPIRUN = getmpirun()
nargs = len(sys.argv)
runid = sys.argv[1] # First argument is the Archive ID to load
restart = sys.argv[2]
proc = sys.argv[3]
nicelvl =sys.argv[4]



if nargs < 5:
    # prints help if arguements aren't given
    print("Format is: ")
    print("  %s <run id> [directory]")
    print("     directory - optional, default is 'tmp'")
    sys.exit(1)

# Unless an argument is given a temporary folder is created to run in
if nargs > 5:
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



# Import inputs into the temporary directory
inputfiles = os.listdir(runid)
for runfiles in inputfiles:
    filepath = os.path.join(runid, runfiles)
    if os.path.isfile(filepath):
        shutil.copy(filepath, directory)
returnHeadings(directory + '/BOUT.inp')    

# Split exe into path and file
path, exe = os.path.split(exe)

print("Path = '%s', exe = '%s'" % (path, exe))

# Change directory
old_dir = os.getcwd()
os.chdir(path)

cmd = "./" + exe + ' -d ' + os.path.join(old_dir, directory) + '/'

print("Current dir = '%s', running '%s'" % (os.getcwd(), cmd))

#print("Command = '%s'" % cmd)
if restart == 'y':
    launch(cmd + ' restart', nproc = proc, nice = nicelvl)
else:
    launch(cmd, nproc = proc, nice = nicelvl, pipe=False)

# Change back to old directory
os.chdir(old_dir)

# Save files from tmp into the loaded archive file and allows for addition of notes

inputfiles = os.listdir(directory)
for runfiles in inputfiles:
    filepath = os.path.join(directory, runfiles)
    if os.path.isfile(filepath):
        shutil.copy(filepath, runid)

shutil.rmtree('tmp')
sys.exit(0)
