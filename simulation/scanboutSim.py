#!/usr/bin/env python

from boututils import shell, launch, getmpirun
import sys, os, ConfigParser, shutil
from tempfile import mkstemp
from os import remove
from shutil import move
from datetime import *


configfile = '/hwdisks/data/bd512/sol1d-scans/5e8/config/config.ini'
parser = ConfigParser.ConfigParser()
parser.read(configfile)
exe = parser.get('exe', 'path')
archive = parser.get('archive', 'path')
editor = parser.get('text editor', 'editor')
MPIRUN = getmpirun()
nargs = len(sys.argv)


# First argument is the Archive ID to load
runid = sys.argv[1] + '/'

#Second argument
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

# form of arguments: runid, key, subkey, initial, limit, increment, restart

if nargs < 7:
    # prints help if arguements aren't given
    print("Format is: ")
    print("  %s <run id> [directory]")
    print("     directory - optional, default is 'tmp'")
    sys.exit(1)

# Unless an arguement is given a temporary folder is created to run in
if nargs > 7:
    directory = sys.argv[2]
else:
    directory = 'tmp'


# Confirms location of BOUT++ archive
try:
    archive = os.environ["BOUTARCHIVE"]
except KeyError:
    # No environment variable. Use default
    archive = '/hwdisks/home/lt724/BOUT-dev/archive/'

# Checks for a valid archive ID
def rundirectory(runid):   
    if os.path.exists(runid):
        print 'Valid runid', runid
    else:
        print 'Invalid runid', runid
        sys.exit(0)


def removeTiming(loadpath):
    f = open(loadpath, 'r')
    filedata = f.read()
    f.close()

    newdata = filedata.replace('[timing]','')


    with open(loadpath, 'w') as File:
        File.write(newdata)
        File.close()
# Makes a new directory called "tmp"
shell("mkdir " + directory) 
sourcedirectory = rundirectory(runid)



### directory = the runid
loadpath = directory + '/BOUT.inp'
loadfrom = runid
def scan(initial, limit, restart, loadpath, key, subkey, increment):
    loadfrom = runid
    i =1 
    while initial < limit:
        inputfiles = os.listdir(loadfrom)
        for runfiles in inputfiles:
            filepath = os.path.join(loadfrom, runfiles)
            if os.path.isfile(filepath):
                shutil.copy(filepath, directory)
        removeTiming(directory + '/BOUT.inp')
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
                                if i == 1:
                                  final = initial
                                  i = 2
                                elif i == 2:
                                  final = initial + increment
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
        inputfiles = os.listdir(directory)
        list.sort(inputfiles)
        if restart == 'y':
            launch(cmd + ' restart', nproc = 5, nice = 10)
        else:
            launch(cmd, nproc = 5, nice = 10, pipe=False)
       
        
    
        x = 1
        archive = (os.path.dirname(os.path.dirname(runid)))
        newfolder = str(archive) + '/' + str(subkey) + '.' + str(initial) + '.' + str(x) + '/'
        while os.path.isdir(newfolder):
            x = x + 1
            newfolder = str(archive) + '/' + str(subkey) + '.' + str(initial) + '.' + str(x) + '/'
        else:
            shell("mkdir " + newfolder)
        for file in inputfiles:
            if file.startswith('BOUT.'):
                filepath = os.path.join(directory, file)
                if os.path.isfile(filepath):
                    shutil.copy(filepath, newfolder)
            if file.startswith('record.'):
                filepath = os.path.join(directory, file)
                if os.path.isfile(filepath):
                    shutil.copy(filepath, newfolder)
            if file.startswith('usernotes.'):
                filepath = os.path.join(directory, file)
                if os.path.isfile(filepath):
                    shutil.copy(filepath, newfolder) 
        i = 2
        loadfrom = newfolder  

try:
    scan(initial, limit, restart, loadpath, key, subkey, increment)
except KeyboardInterrupt:
    print 'User Exit'
    shutil.rmtree('tmp')
    sys.exit(0)
 
##
##
##def scan1var():
##    global initial, limit, restart, loadpath, key, subkey, increment
##    loadpath = directory + '/BOUT.inp'
##    key = raw_input('Key of input : ')
##    subkey = raw_input('Variable to change : ')
##    f = open(loadpath, 'r')
##    for line in f:
##        if line.startswith(key):
##            for line in f:
##                if line.startswith(subkey):
##                    string = line.split()
##                    a = string[string.index('=') + 1]
##                    initial = float(a)
##                    print 'Initial Value: ', initial
##    increment = raw_input('Increment of increase of variable : ')
##    thresh = raw_input('Upper limit of scan : ')
##    limit = float(thresh)
##    restart = raw_input('Use restart each iteration? (y/n) : ')
##    scan()




##def scan2var():
##    global initial, initial2, limit, restart, loadpath, key, subkey, subkey2, increment
##    loadpath = directory + '/BOUT.inp'
##    key = raw_input('Key of input1 : ')
##    subkey = raw_input('Variable1 to change : ')   
##    f = open(loadpath, 'r')
##    for line in f:
##        if line.startswith(key):
##            for line in f:
##                if line.startswith(subkey):
##                    string = line.split()
##                    a = string[string.index('=') + 1]
##                    initial = int(a)
##                    print 'Initial Value: ', initial
##    increment = raw_input('Increment of increase of variable1 : ')
##    thresh = raw_input('Upper limit of scan of variable1 : ')
##    limit = int(thresh)
##    reset = (limit + int(increment) - int(initial))
##    key2 = raw_input('Key of input2 : ')
##    subkey2 = raw_input('Variable2 to change : ')
##    f = open(loadpath, 'r')
##    for line in f:
##        if line.startswith(key2):
##            for line in f:
##                if line.startswith(subkey2):
##                    string = line.split()
##                    a = string[string.index('=') + 1]
##                    initial2 = int(a)
##                    print 'Initial Value2: ', initial2
##    increment2 = raw_input('Increment of increase of variable2 : ')
##    thresh2 = raw_input('Upper limit of scan variable2 : ')
##    limit2 = int(thresh2)
##    restart = raw_input('Use restart each iteration? (y/n) : ')
##    #npro = raw_input('N.o of processors to use: ')
##    while initial2 < limit2:
##        scan()
##        th, temp = mkstemp()
##        with open(temp,'w') as g:
##            with open(loadpath, 'r') as f:
##                for line in f:
##                    if line.startswith(key2):
##                        g.write(line)
##                        for line in f:
##                            if line.startswith(subkey2):
##                                string = line.split()
##                                a = string[string.index('=') + 1]
##                                initial2 = int(a)
##                                n = int(increment2)
##                                final2 = initial2 + n
##                                b = str(final2)
##                                new = line.replace(a, b)
##                                g.write(new)
##                                break
##                            else:
##                                g.write(line)
##                    else:
##                        g.write(line)
##                g.close()
##        remove(loadpath)
##        move(temp, loadpath)
##        th, temp = mkstemp()
##        with open(temp,'w') as g:
##            with open(loadpath, 'r') as f:
##                for line in f:
##                    if line.startswith(key):
##                        g.write(line)
##                        for line in f:
##                            if line.startswith(subkey):
##                                string = line.split()
##                                a = string[string.index('=') + 1]
##                                ending = int(a)
##                                initial = ending - reset
##                                b = str(initial)
##                                new = line.replace(a, b)
##                                g.write(new)
##                            else:
##                                g.write(line)
##                    else:
##                        g.write(line)
##                g.close()
##        remove(loadpath)
##        move(temp, loadpath)



      

##if parameters == '2':
##    try:
##        scan2var()
##    except KeyboardInterrupt:
##        print 'User Exit'
##        shutil.rmtree('tmp')
##        sys.exit(0)
##    shutil.rmtree('tmp')



