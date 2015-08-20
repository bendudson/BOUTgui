# imports all relavent modules
import configparser, sys, os, time, difflib, shutil, re, fileinput
from datetime import *
from PySide.QtGui import *
from PySide.QtCore import *
from mainwindow import *
from dialog import *
from dialogcompare import *
from guifunctions import *


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

        
def left(line, sep):
        """
        called by commentsTup. similar to the clean function, strips off the comments from a line
        leaving just the important value
        """
        # splits the line at sep (#)
        for s in sep:
            line = line.split(s)[0]
        return line.strip()
    
def right(line, sep):
        """
        called by commentsTup. different to left in that this keeps only the comments and none of the
        important values
        """
        # splits the line at sep (#)
        try:
            for s in sep:
                line = line.split(s)[1]
            return line.strip()
        except IndexError:
            pass
        
def commentsTup(loadpath):
        """
        called by updateControls. creates a list of tuples containing values and comments, effectivly splits up
        the config file so that these parts can be treated seperatly. 
        """
        global tups
        tups = []
        # read the BOUT config file that this has been called abput
        with open(loadpath, 'r') as controlfile:
            lines = controlfile.readlines()
            # for each line split into a left and a right part
            for line in lines:
                name = left(line, '#')
                comment = '  #  ' + str(right(line, '#'))
                if name != '':
                    # create a list of tuples containing name and it's comment
                    tup = (name, comment)
                    tups.append(tup)
        return tups

def addComments(runid, tups):
        """
        called by worker and scan worker. reads through the config file and decides whether each option contains the value kept within
        the tuple and whether that value already has a comment associated with it. If not it adds
        the comment back onto the line - this makes up for the fact that the config parser deletes
        comments.
        """
        # steps through the list of tups
        for i in range(len(tups)):
            try:
                # get the first word of the name (e.g. NOUT)
                lineStart = tups[i][0].split()[0]
                # read all the lines in file
                for line in fileinput.input(runid, inplace = 1):
                        # see if there is already a comment
                    if lineStart in line and '#' not in line:
                            # append the comment provided that there is one - the comment is 'None' for blank lines
                        if 'None' not in tups[i][1]:
                            newline = line.rstrip() + '  ' + tups[i][1].rstrip() + '\n'
                            line = line.replace(line, newline)
                        # sys.stdout is redirected by fileinput so this writes to file
                    sys.stdout.write(line)            
            except IndexError:
                pass

def parentDir(loadpath, newpath):
    """
    called by create, used to append to the record.ini file the current file history
    """
    folder = re.sub('/BOUT.inp', '', loadpath)
    i = datetime.today()
    # get times
    TimeDate = ("%s:%s:%s   %s/%s/%s" % (i.hour, i.minute, i.second, i.day, i.month, i.year))
    # formatting template
    template = '{0:24}{1:24}{2:18}{3:18}{4:18}{5:5}'
    # if it exists in the oldpath then copy to the new path
    if os.path.isfile(folder + '/record.ini'):
        shutil.copy(folder + '/record.ini', newpath + '/record.ini')
        # write in the copied file the new line
        record = open(newpath + '/record.ini', 'a')
        record.write('\n' + 'Parent Directory:   ' + newpath + '   ' + TimeDate)
        # if not then creates a new file
    if not os.path.isfile(folder + '/record.ini'):
        record = open(newpath + '/record.ini', 'w')
        # writes to the new file
        record.write('Parent Directory:   ' + newpath + '   ' + TimeDate)
    record.close() 

        
def addTiming(loadpath):
    """
    called by changeHeading. addTiming should be called every time a file is loaded into config parser to make sure
    that the file has the timing section at the top
    """
    # read the file
    f = open(loadpath, 'r')
    filedata = f.readlines()
    f.close
    # if timing exists do nothe
    if '[timing]\n' in filedata:
        pass
    else:
            # add a new line at the top containing [timing]
        filedata.insert(0, '[timing]' + '\n')
        f = open(loadpath, "w")
        filedata = "".join(filedata)
        # write the file
        f.write(filedata)
        f.close()

def changeHeading(loadpath, oldheading, newheading):
    """
    called by changeHeadings possibly mulitple times, for everytime that a new heading that doesn't work with the GUI is encountered 
    """
    # changes a specified heading and replaces it with the original so that the control file works
    for line in fileinput.input(loadpath, inplace = 1):   
        if oldheading in line:
            line = line.replace(oldheading, newheading)
        sys.stdout.write(line)


def toStr(uni):
    codec = QTextCodec.codecForName("UTF-8")
    return str(codec.fromUnicode(str(uni)))
