import configparser, sys, os, time, difflib, shutil, re, fileinput
from datetime import *
from PySide.QtGui import *
from PySide.QtCore import *
from mainwindow import *
from dialog import *
from dialogcompare import *
from guifunctions import *



def left(line, sep):
        """
        similar to the clean function, strips off the comments from a line
        leaving just the important value
        """
        for s in sep:
            line = line.split(s)[0]
        return line.strip()
    
def right(line, sep):
        """
        different to left in that this keeps only the comments and none of the
        important values
        """
        try:
            for s in sep:
                line = line.split(s)[1]
            return line.strip()
        except IndexError:
            pass
        
def commentsTup(loadpath):
        """
        creates a list of tuples containing values and comments, effectivly splits up
        the config file so that these parts can be treated seperatly. 
        """
        global tups
        tups = []
        with open(loadpath, 'r') as controlfile:
            lines = controlfile.readlines()
            for line in lines:
                name = left(line, '#')
                comment = '  #  ' + str(right(line, '#'))
                if name != '':
                    tup = (name, comment)
                    tups.append(tup)
        return tups

def addComments(runid, tups):
        """
        reads through the config file and decides whether each option contains the value kept within
        the tuple and whether that value already has a comment associated with it. If not it adds
        the comment back onto the line - this makes up for the fact that the config parser deletes
        comments.
        """

        for i in range(len(tups)):
            try:
                lineStart = tups[i][0].split()[0]
                for line in fileinput.input(runid, inplace = 1):
                    if lineStart in line and '#' not in line:
                        if 'None' not in tups[i][1]:
                            newline = line.rstrip() + '  ' + tups[i][1].rstrip() + '\n'
                            line = line.replace(line, newline)
                    sys.stdout.write(line)            
            except IndexError:
                pass


def comments(loadpath, newpath, notes): ##(USERCOMMENTS NOT CONFIG FILE COMMENTS
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

def changeHeading(loadpath, oldheading, newheading):
    # changes a specified heading and replaces it with the original so that the control file works
    for line in fileinput.input(loadpath, inplace = 1):   
        if oldheading in line:
            line = line.replace(oldheading, newheading)
        sys.stdout.write(line)

def changeHeadings(loadpath):
        addTiming(loadpath)
        ######################################################################
        #ADD ANY CHANGES TO HEADINGS FROM ORIGINAL TO WORK WITH PARSER
        ######################################################################
        changeHeading(loadpath, '[2fluid]', '[TWOfluid]')
        ######################################################################

def returnHeadings(loadpath):
        ######################################################################
        #RETURNS THE CONTROL FILE BACK TO HOW IT WAS BEFORE
        ######################################################################
        changeHeading(loadpath, '[timing]', '')
        changeHeading(loadpath, '[TWOfluid]', '[2fluid]')
        ######################################################################

def toStr(uni):
    codec = QTextCodec.codecForName("UTF-8")
    return str(codec.fromUnicode(str(uni)))
