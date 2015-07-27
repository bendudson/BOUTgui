import configparser, sys, os, time, difflib, shutil, re
from datetime import *
from PySide.QtGui import *
from PySide.QtCore import *
from mainwindow import *
from dialog import *
from dialogcompare import *
from guifunctions import *


def comments(loadpath, newpath, notes):
    """
    finds the folder in the archive (or otherwise) of the file that has been loaded
    for editing and running. copies or creates a usernotes.ini file to store comments
    in. saves any new comments in the folder of the new file.
    """
    folder = re.sub('/BOUT.inp', '', loadpath)
    if os.path.isfile(folder + '/usernotes.ini'):
        shutil.copy(folder + '/usernotes.ini', newpath + '/usernotes.ini')
        usernotes = open(newpath + '/usernotes.ini', 'w')
        usernotes.write(notes)
        usernotes.close()
    if not os.path.isfile(folder + '/usernotes.ini'):

        usernotes = open(newpath + '/usernotes.ini', 'w')
        usernotes.write(notes)
        usernotes.close()

def parentDir(loadpath, newpath):
    folder = re.sub('/BOUT.inp', '', loadpath)
    i = datetime.today()
    TimeDate = ("%s:%s:%s   %s/%s/%s" % (i.hour, i.minute, i.second, i.day, i.month, i.year))
    template = '{0:24}{1:24}{2:18}{3:18}{4:18}{5:5}'
    if os.path.isfile(folder + '/record.ini'):
        shutil.copy(folder + '/record.ini', newpath + '/record.ini')
        record = open(newpath + '/record.ini', 'a')
        record.write('\n' + 'Parent Directory:   ' + newpath + '   ' + TimeDate)
    if not os.path.isfile(folder + '/record.ini'):
        record = open(newpath + '/record.ini', 'w')    
        record.write('Parent Directory:   ' + newpath + '   ' + TimeDate)
    record.close() 

def removeTiming(loadpath):

    """
 need to insert this into the run code(?) so that the file that gets sent to the temporary
 folder doesn't have the header timing
    """
    f = open(loadpath, 'r')
    filedata = f.read()
    f.close

    newdata = filedata.replace('[timing]', 'hello')


    with open(loadpath, 'w') as File:
        File.write(newdata)
        File.close


def addTiming(loadpath):
    """
    addTiming should be called every time a file is loaded into config parser to make sure
    that the file has the timing section at the top
    """
    
    f = open(loadpath, 'r')
    filedata = f.readlines()
    f.close

    if '[timing]\n' in filedata:
        pass
    else:
        filedata.insert(0, '[timing]' + '\n')
        f = open(loadpath, "w")
        filedata = "".join(filedata)
        f.write(filedata)
        f.close()

def toStr(uni):
    codec = QTextCodec.codecForName("UTF-8")
    return str(codec.fromUnicode(str(uni)))
