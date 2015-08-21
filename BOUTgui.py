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

### For development of this code there are a huge number of variables related to those created automatically using pyside imported in mainwindow. The easiest
### way to find variable names is to open qt in the background and click on the element that needs coding for, it displays the variable name there.

# This code is long, ideally all the different classes would be in their own files and imported but because of the nature of using pyside and also because possibly the
# best approach to global variables wasn't taken initially this has been unavoidable.
# To navigate there for the order has been made as logical as possible, with the order relating to the order in which the GUI is run,
# so all the load stuff comes first, then inputs, outputs and graphing. Other menu functions are at the end of all of this

"""
Contents :

1) imports
2) global variables
3) thread classes
    o run simulation
    o run scanning simulation
    o collect worker
    o plot worker
4) mainwindow
    o initialisation of buttons and linking to functions
      - order of file actions = order of file menu in gui
      - buttons split by tab
      - checkboxes by tab
    o functions for load tab
    o functions for change inputs tab
    o functions for output tab
    o functions for graphing tab
    o functions for other menu actions (e.g.file history)

5) resize
6) dialogSave
7) Scandialog
8) dialogSimulation
9) defaultsave
10) addDefaultVar
11) textDisplay
12) textdisplayhistory
13) helpView
"""

# imports standard python libraries
import configparser, sys, os,  difflib, subprocess, threading, signal
from datetime import *
from time import *

# BOUT data files
from boututils.datafile import DataFile

# imports other functions
from guifunctions import *

# imports the pyside modules
from PySide.QtGui import *
from PySide.QtCore import *

# imports from all the qt created files
from mainwindow import *
from dialog import *
from dialogcompare import *
from textdisplay import *
from textdisplayhistory import *
from defaultsave import *
from scanbout import *
from resize import *
from dialogSimulation import *
from dialogArchive import *
from defaultVars import *

# imports taken from pyxpad to make the console work 
try:
  import cPickle as pickle
except:
  import pickle
try:
  from StringIO import StringIO  # Python 2
except:
  from io import StringIO
import re
import string

# this gets current directory = the directory of BOUTgui.py and stores it in oldDir
currentDir = os.getcwd()
config = currentDir + '/config/config.ini'
oldDir = currentDir

# lists to hold infomation for automatic creation of inputs
inputsLst = []
sectionLst = []
inputsTupLst = []
groupbox = []
loadpath1= 'empty'
run = 'false'
cell =False 
parser2 = configparser.ConfigParser()

###################################################################
#   APPRARANCE
 # used to get the values for the automatic creation of input buttons, they are taken from the config file
 # defines the position and size of the boxes that are created to contain inputs

# reads the config file
with open(config) as fp:
    position = configparser.ConfigParser()
    position.optionxform = str
    position.readfp(fp)
# defines all the appearance variables using config parser
leftBorder = int(position.get('appearance', 'leftborder'))
verticalSeperation = int(position.get('appearance', 'verticalseperation'))
topBorder = int(position.get('appearance', 'topborder'))
maxLength = int(position.get('appearance', 'maxlength'))
boxWidth = int(position.get('appearance', 'boxwidth'))
horizontalSeperation = int(position.get('appearance', 'horizontalseperation'))
boxLength = int(position.get('appearance', 'boxlength'))
sepInput = int(position.get('appearance', 'sepinput'))
########################################################################


# collects archive folder from config
archive = position.get('archive', 'path')
# and simulation code from config
codeFile = position.get('exe', 'path')
# create the global parser variable
parser = configparser.ConfigParser()

####################################### NEW CLASS #######################################

class Worker(QThread):
##    """ 
##    This thread runs the simulations in the backgrounds so preventing the GUI from freezing while running
##    STDOUT is redirected to a signal which is collected by the text editor of the output stream
##        """

      dataLine1 = Signal(str)
      def __init__(self, path, restart, numProc, nice, outputStream,  parent = None):
              QThread.__init__(self, parent)
              # define all the varaibles and run parameters from the class call
              self.path = path + '/'
              self.loadpath = path
              self.restart = restart
              self.outputStream = outputStream
              self.numProc = numProc
              self.nice = nice
              # goes from inputs tab to the output tab
              window.tabWidget.setTabEnabled(2, True)
              # reattaches comments that would have been lost because of the config parser, tups is the list of tuples that they are saved within
              global tups

              # imported from gui functions, reattaches inline comments to the contro file
              addComments(self.path + 'BOUT.inp', tups)
                  


      def run(self):
          # resets directory to dir of GUI
          os.chdir(oldDir)
          # proc runs the simulation
          global proc
          # intiates the subprocess to run the simulation
          # for code see ./BOUTgui/runboutSim.py
          proc = subprocess.Popen([currentDir + '/runboutSim.py', str(self.path), str(self.restart), str(self.numProc), str(self.nice)],
                                  shell = False, stdout = subprocess.PIPE, stderr = subprocess.PIPE, preexec_fn=os.setsid) # last term is used for the keyboard interupt
            
          running = True
          while running == True:
              # while running checks to see if there is an output
              output = proc.stdout.readline()
              if output == '' and proc.poll() is not None:  # at the end of proc stops reading empty ines to allow the program to close
                        # when no more output moves to graphing tab
                       window.tabWidget.setCurrentIndex(3)
                       proc.wait()
                       running = False
                       # for collect
                       global loadpath1
                       loadpath1 = self.loadpath
              else:
                  # while there is output sends it to dataLine1 
                  self.dataLine1.emit(output) 


                  
####################################### NEW CLASS #######################################

class scanWorker(QThread):
##                """ 
##                Different to the above because this is for running scanned simulations so has many more inputs and uses
##                scanbout rather than runbout. 
##                """

      dataLine1 = Signal(str)
      def __init__(self, path, key, subkey, initial, limit, increment, restart, incrementType, scanType, key2, subkey2, initial2, limit2, increment2, numProc, nice, outputStream, parent = None):
              QThread.__init__(self, parent)
              # defines all the variables and run parameters from the worker call
              self.path = path
              self.key = key
              self.subkey = subkey
              self.initial = initial
              self.limit = limit
              self.increment = increment
              self.restart = restart
              self.key2 = key2
              self.subkey2 = subkey2
              self.initial2 = initial2
              self.limit2  = limit2
              self.increment2 = increment2
              self.incrementType = incrementType
              self.scanType = scanType
              self.outputStream = outputStream
              self.numProc = numProc
              self.nice = nice
              # takes to the outputsteam tab
              window.tabWidget.setTabEnabled(2, True)
              #print self.path
              addComments(self.path + '/BOUT.inp', tups)


      def run(self):
          # resets directory to dir of GUI
          os.chdir(oldDir)
          # proc runs the simulation
          global proc
          # starts the subprocess
          # for code see ./BOUTgui/scanboutSim.py
          proc = subprocess.Popen([currentDir + '/scanboutSim.py', str(self.path), str(self.key), str(self.subkey), str(self.initial), str(self.limit), str(self.increment), str(self.restart), str(self.incrementType), str(self.scanType), str(self.numProc), str(self.nice), str(self.initial2), str(self.limit2), str(self.key2),str(self.subkey2),str(self.increment2)],
                                   shell = False, stdout = subprocess.PIPE, stderr = subprocess.PIPE) # the keyboard interupt doesn't work for scans for some reason
          # used for an exit on keyboard interupt
          global pid
          pid = proc.pid
          # keeps the output checking for a stream
          running = True
          while running == True:
              output = proc.stdout.readline()
              if output == '' and proc.poll() is not None:  # at the end of proc stops reading empty lines to allow the program to close
                       window.list_archive('inp')
                       # moves to graphing tab
                       window.tabWidget.setCurrentIndex(3)
                       proc.wait()
                       # stops the loop
                       running = False
                       global loadpath1
                       loadpath1 = self.path
              else:
                  self.dataLine1.emit(output) # lines of output are emited here 
                  

####################################### NEW CLASS #######################################

class WorkerCollect(QThread):
    """
      Started by window.collect(). Works in the back ground to collect all the variables that are contained within the loaded data files
      that are also on the defaults list. The defaults list is created because models like sol1d have around
      40 collectable variables, importing all automatically takes too long and even causes crashes so instead
      the user choses automatic defaults to collect suitable to the data that they need. 
    """

    def __init__(self, path,  parent = None):
        # initialise the thread
        QThread.__init__(self, parent)
        self.path = path
        
        
    def insertTableRow(self, *args):
        """
        Inserts a row into the table at row 0
        The inputs to this function will be inserted in order as
        columns in this new row. Need one of these functions for each table. 
        """
        # First disable sorting, so table won't rearrange itself
        addDefaultVar.otherVariablesTable.setSortingEnabled(False)
        
        # Insert a row at 0, i.e. the top
        addDefaultVar.otherVariablesTable.insertRow(0)
        
        # Loop over all arguments, inserting into rows
        for col, value in enumerate(args):
            # col is the column number, value is the value to set to
            # Note that the values should be strings
            item = QTableWidgetItem(toStr(value))
            addDefaultVar.otherVariablesTable.setItem(0,col, item)
            
        # Re-enable sorting
        addDefaultVar.otherVariablesTable.setSortingEnabled(True)
        
    def run(self):
            """
            Runs the collect routine. Currently the python pyxpad part has to collect seperatly to the GUI features which is
            why all the imports have to happen twice. This is slow so have a thread - also adds stability. Sleep functions
            mean prevents all commands from being executed simulateously which crahses the system. 
            """
            # it is tempting to push the collect button while collect is happening in the background. This would
            # start another thread and cause a crash so to show the user that the GUI is working collect, plot and
            # collect extra are all disabled
            window.pushButton_7.setEnabled(False)
            window.createGraph.setEnabled(False)
            window.collectExtraVariable.setEnabled(False)
            window.variableCombo.clear()
            window.extraVarsCombo.clear()
            datapath = re.sub('/BOUT.inp', '', loadpath1)
            os.chdir(datapath)
            #change directory to path
            window.textOutput.ensureCursorVisible()
            window.dataTable.clearContents()
            window.dataTable.setRowCount(0)
            window.data = {}  # resets the data stored in pyxpad as multiple collects would cause a crash otherwise.

            # load data file, used to look at avaiable variables
            try:
                d = DataFile('BOUT.dmp.0.nc')
            except RuntimeError:
                # an exception created for runtime error caused by no data files 
                window.pushButton_7.setEnabled(True)
                window.createGraph.setEnabled(True)
                window.collectExtraVariable.setEnabled(True)
                window.commandEntered('NO DATAFILES!!!')

            # create a list of keys in the data file
            d.keys()

            # want all the keys that contain 4 dimensions
            varLst = []
            for v in d.keys():
                    if d.ndims(v)==4: # counts dimensions
                             varLst.append(v)

            window.commandEntered('from boutdata import collect')
            sleep(0.01)    # stops all collect calls happening simulataneously
            window.commandEntered('from boututils import plotdata')
            sleep(0.01)
            #os.chdir(self.path)
            
            # the defaults are stored in the config file
            global defaultLst
            defaultLst =  position.get('defaultVars', 'vars')
            
            def getlist(option, sep=',', chars=None):
                """Return a list from a ConfigParser option. By default, 
                   split on a comma and strip whitespaces."""
                return [ chunk.strip(chars) for chunk in option.split(sep) ]

            defaultLst = getlist(defaultLst)

            # collects for command line
            for var in varLst:
                    # checks if default list to all the 4D variable and then collects
                    if var in defaultLst:
                          window.commandEntered(str(var.strip(',.').lower())+ '= collect(' +'"'+str(var)+ '"' + ')')
                          sleep(0.1)
                          
            # temp was something I needed for SOL1D so it was automated, possibly could be deleted
            try:
              if 'P' and 'Ne' in varLst:
                  window.commandEntered('temp = 0.5*p/ne')
                  sleep(0.1)
            except NameError:
                pass

            # collects for the GUI graphing    
            from boutdata import collect
            global varDic, plotLst, notLoadedLst
            varDic = {}
            plotLst = []
            notLoadedLst = []
            
            
            # does the same as before but appends all data to a dictionary of variables
            for var in varLst:
                    # adds to combo for graphing and collects if var is a default
                    if var in defaultLst:
                        plotLst.append(var)
                        window.variableCombo.addItem(var)
                        a = collect(str(var))
                        varDic[var] = a
                        
                    # again cerates the temp variable which could potentially be removed
                    elif 'P' and 'Ne' in varLst and 'temp' not in plotLst:
                        try:
                            var = 'temp'
                            plotLst.append(var)
                            window.variableCombo.addItem(var)
                            a = collect('P')
                            b = collect('Ne')
                            varDic[var] = 0.5*a/b
                        except NameError:
                            pass
                        
                    else:
                      # all varaibles that aren't defaults are appended to the combobox for optional collection
                        window.extraVarsCombo.addItem(var)
                        notLoadedLst.append(var)
                        self.insertTableRow(var)
                        sleep(0.01)
                        
                        

            # sets the label onscreen with the folder path of collection 
            window.collectedLabel.setText(str(self.path))

            # re-enables all the buttons after the collect thread has finished working
            window.pushButton_7.setEnabled(True)
            window.createGraph.setEnabled(True)
            window.collectExtraVariable.setEnabled(True)
             
            self.exit()

            
####################################### NEW CLASS #######################################
                  
# this worker thread does graph plotting
class Worker2(QThread):
    """
      Creates graphs using the matplotlib widget, is called by both the GUI and the console plotting functions
    """

    def __init__(self, parent = None):
        QThread.__init__(self, parent)

    def run(self):
        # 4D values from user input
        x = (window.xspin.text())
        y = (window.yspin.text())
        z = (window.zspin.text())
        t = (window.tspin.text())

        # finds index of variable combo
        i = window.variableCombo.currentIndex()

        # uses plotLst, varDic created in collectworker
        global plotLst, varDic
        # variable becomes the data of the selected variable onscreen
        variable =  plotLst[i]
        variable = varDic[variable]

        # call plotdata
        self.plotdata(variable, t, x, y, z)
        
    def plotdata(self, variable, t, x, y, z):
        """
        Takes into account all of the possiblilties when it comes to plotting any graph where one or
        two of the variables is taken as an entire data set (i.e. 1D or 2D plots), 3D plots are not
        possible - this may seem overcomplicated BUT cannot input colon as a string into plotdata so
        this is the only way! NOTE that it might be possible to use mycode = 'code..' then exec
        mycode as has been done later in this file, but seeing as this code works reliably have
        left that change for now.
        """
        # imports that plotdata module installed when the BOUT code is installed on the system
        from boututils import plotdata
        
        # if plotting anything against all of time
        if window.tall.isChecked() == True:
            # 2D permutations
            if window.xall.isChecked() == True:
                window.DataPlot.plotdata(variable[:,:,int(y),int(z)])
            if window.yall.isChecked() == True:
                window.DataPlot.plotdata(variable[:,int(x),:,int(z)])
            if window.zall.isChecked() == True:
                window.DataPlot.plotdata(variable[:,int(x),int(y),:])
            # 1D permutation
            if window.xall.isChecked() == False and window.yall.isChecked() == False and window.zall.isChecked()== False:
                window.DataPlot.plotdata(variable[:,int(x),int(y),int(z)], title=None, xtitle=None, ytitle=None)
                
        # if plotting against all of x       
        if window.xall.isChecked() == True:
            # 2D permuations
            if window.yall.isChecked() == True:
                window.DataPlot.plotdata(variable[int(t),:,:,int(z)])
            if window.zall.isChecked() == True:
                window.DataPlot.plotdata(variable[int(t),:,int(y),:])
            # 1D permutation 
            if window.tall.isChecked() == False and window.yall.isChecked() == False and window.zall.isChecked()== False:
                window.DataPlot.plotdata(variable[int(t),:,int(y),int(z)])
                
        # if plotting against all of y        
        if window.yall.isChecked() == True:
            # 2D permutation
            if window.zall.isChecked() == True:
                window.DataPlot.plotdata(variable[int(t),int(x),:,:])
            # 1D permutation
            if window.xall.isChecked() == False and window.tall.isChecked() == False and window.zall.isChecked()== False:
                window.DataPlot.plotdata(variable[int(t),int(x),:,int(z)])
                
        # if plotting against all of z
        if window.zall.isChecked() == True:
            # 1D permuation - because order doesn't matter all the 2D permuations have already been taken into account 
            if window.xall.isChecked() == False and window.yall.isChecked() == False and window.tall.isChecked()== False:
                window.DataPlot.plotdata(variable[int(t),int(x),int(y),:])
                
####################################### NEW CLASS #######################################

class generalDialog(QtGui.QMainWindow, Ui_Dialogcompare):
    """
    Creates a general, single-button, dialog box for giving the user information. This is called many times and
    each time the text displayed is changed and the window name changed with two lines of code...
        generalDialog.label.setText(QtGui.QApplication.translate("generalDialog", "Displayed Text" , None, QtGui.QApplication.UnicodeUTF8))
        generalDialog.setWindowTitle(QtGui.QApplication.translate("generalDialog", "Window Name", None, QtGui.QApplication.UnicodeUTF8))
    """
    def __init__(self, parent=None):
        """
        Initialisation routine 
        """
        # These calls set up the window
        super(generalDialog, self).__init__(parent)
        self.setupUi(self)
            
####################################### NEW CLASS ######################################

class MainWindow(QtGui.QMainWindow, Ui_MainWindow):
    """
    This class represents the main window
    which inherits from Qt's QMainWindow and from
    the class defined in mainwindow (called Ui_MainWindow)
    """
    def __init__(self, parent=None):
        """
        Initialisation routine
        """
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        ###################################################
        # INITIALISE ALL THE MAINWINDOW BITS
        ##########
        
        # set global all the file paths
        global archive, config, codeFile

        # set the path indicator labels for archive and simulation code (see inputs tab)
        if os.path.isdir(archive):
            self.archivePath.setText(archive)
        if os.path.isfile(codeFile):
            self.simulationFile.setText(codeFile)        
        # set niceness default
        self.niceSpin.setValue(10)
        # initialise the defaults combo with all the variables from defaults within the config file
        self.defaultCombo.currentIndexChanged.connect(self.loadDefault)
        ###################################################
        
        ###################################################
        # TOP MENU ACTIONS
        ##########
        ## FILE 

        # bring up graphical file explorer to load archive
        self.actionArchive.triggered.connect(self.archiveLoad)
        # bring up graphical file explorer to load simualation code
        self.actionSimulation_Code.triggered.connect(dialogsave.loadSimCode)
        # brings up the default variables window where defaults can be added and deleted
        self.actionDefault_Variables.triggered.connect(self.show_Variables)
        
        # load file history, brings up the textdisplay
        self.actionFileHistory.triggered.connect(self.FileHistoryClicked)        
        # start the compare routine, asks to load second file the brings up text display
        self.actionCompare.triggered.connect(self.compareClicked)
        
        # interupt simulation     
        self.actionStop_Simulation.triggered.connect(self.STOP)

        # exit the program
        self.actionExit.triggered.connect(self.close)
        
        ##########
        ## VIEW 
        
        # bring up the resize and reposition window
        self.actionPositioning.triggered.connect(self.showResize)
      
        ##########
        ## HELP 
        
        # bring up the help text viewer
        self.actionAbout.triggered.connect(self.showAbout)
        self.actionHelp.triggered.connect(self.openHelp)
        ###################################################

        ###################################################
        # BUTTONS
        ##########
        ## LOAD TAB
        
        # load button, loads the current selected file from the table
        self.pushButton.clicked.connect(self.buttonAction)
        # (also double clicking does the same)
        self.tableWidget.cellDoubleClicked.connect(self.loadinp)

        ##########
        ## CHANGE INPUTS TAB
        
        # starts a scanning simulation
        self.runScanningSimulation.clicked.connect(self.changeScan)
        # the 'write' button to save the changes
        self.pushButton_2.clicked.connect(self.showDialog)
        # starts a normal simulation 
        self.pushButton_3.clicked.connect(self.changerun)

        ##########
        ## OUTPUT STREAM TAB
        
        # stop simulation button, call function to create a keyboard interupt
        self.stopSimulation.clicked.connect(self.STOP)        

        ##########
        ## GRAPHING TAB
        
        # delete default, as in plotting default
        self.deleteButton.clicked.connect(self.deleteDefault)        
        # collects manually the variable selected in the extra combo box
        self.collectExtraVariable.clicked.connect(self.collectExtra)
        # create a graph       
        self.createGraph.clicked.connect(self.rungraph)
        # collect data
        self.pushButton_7.clicked.connect(self.collectit)
        # save the current setup on the GUI 
        self.saveDefaultButton.clicked.connect(self.saveDefault)
        ###################################################

        ###################################################
        # CHECKBOXES
        ##########
        ## CHANGE INPUTS TAB
        
        # if restart is checked locks in number of processor to use so that the wrong number for number of data files can't be input
        self.checkBox.stateChanged.connect(self.disableProc)
        
        ##########
        ## GRAPHING TAB
        # disable/ enable plotting spin boxes for t, x, y, z
        self.tall.stateChanged.connect(self.disablet)
        self.xall.stateChanged.connect(self.disablex)
        self.yall.stateChanged.connect(self.disabley)
        self.zall.stateChanged.connect(self.disablez)
        ###################################################

        ######################################################################################################
        #all the console and graphing bits as used in some of Ben's bits, such as pyxpad and matplotlib widget.
        ######################################################################################################
        self.data = {}
        self.commandInput.commandEntered.connect(self.commandEntered)
        self.commandButton.clicked.connect(self.commandEntered)
        self.dataTable.cellChanged.connect(self.dataTableChanged)
               
        # import bits for Matplotlib_widget
        try:  
            from matplotlib_widget import MatplotlibWidget
            self.DataPlot = MatplotlibWidget(self.frame)
        except:
            raise
        self.tableWidget.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        ######################################################################################################

##################################################################################################################
##################################################### LOAD TAB ###################################################
     
    def archiveLoad(self):
        """
        Called when file -> 'archive load' is clicked. 
        This function calls a file viewer/ explorer window for the user to chose or create their archive folder
        """
        # redefine the global archive to be differnet to that loaded from the config file
        global archive
        # this calls the file viewer (FileDialog)
        archive = QtGui.QFileDialog.getExistingDirectory(self, "Choose or Create Archive",
                QtCore.QDir.currentPath())
        # set the new archive in the config file position
        position.set('archive', 'path', str(archive))
        # write to the config the changes
        with open (config, 'w') as configfile:
            position.write(configfile)
        # clear data from the archive table            
        self.clearTable()
        self.tabWidget.setCurrentIndex(1)
        # lists the files in the new archive
        self.list_archive('.inp')
        self.tabWidget.setCurrentIndex(0)
        # sets the text of the label at bottom of tab
        if os.path.isdir(archive):
          # tests if a directory, if so sets to directory
            self.archivePath.setText(archive)
        else:
          # if not displays these instructions
            self.archivePath.setText('None loaded or bad file path, click File -> Archive Location to load')

            
    def clean(self,line, sep):
        """
        called in a few differnt places. used because of compatibitilty issues with old and new config parser,
        old config parser kept returning comments when using parser.get, this removes
        anything after sep term
        """
        for s in sep:
            line = line.split(s)[0]
        return line.strip()

    def clearTable(self):
        """
        Clears the table contents
        """
        # clears all the cell data
        self.tableWidget.clearContents()
        # required to actually delete rows, otherwise end up with extra blank rows. 
        self.tableWidget.setRowCount(0)
        
        
    def insertTableRow(self, *args):
        """
        called by list_archive. Inserts a row into the table at row 0
        The inputs to this function will be inserted in order as
        columns in this new row.
        """
        # First disable sorting, so table won't rearrange itself
        self.tableWidget.setSortingEnabled(False)
        
        # Insert a row at 0, i.e. the top
        self.tableWidget.insertRow(0)
        
        # Loop over all arguments, inserting into rows
        for col, value in enumerate(args):
            # col is the column number, value is the value to set to
            # Note that the values should be strings
            item = QTableWidgetItem(toStr(value))
            self.tableWidget.setItem(0,col, item)
            
        # Re-enable sorting
        self.tableWidget.setSortingEnabled(True)
        
    def list_archive(self, filetype):
        """
        called by save, run, loadinitial.  given a files type then this is a versatile function which creates a list of files stored in a list. This list then is
        used to create directory which contains date created, date modified, shortened file path aswell as the comment data
        for that file if any
        """

        #loads all the files from the archive
        oldpath = ''
        # calls clear table function
        self.clearTable()
        if os.path.isdir(archive):
              lst = os.listdir(archive)
              list.sort(lst)
              #directory is a global variable used in many functions
              global directory
              directory = []
              subdirectory = []
              
              #look in each folder
              for folder in lst:
                  # look in each child folder
                  path = os.path.join(archive, str(folder))
                  if os.path.isdir(path):
                      sublst = os.listdir(path)
                      for file in sublst:
                          filepath = os.path.join(path, file)
                          # adds all the .nc files to a list
                          if os.path.isfile(filepath) and filepath.endswith('.nc'):
                              subdirectory.append(filepath)
                  # divides length of list by two to get proc number
                  procNumber = len(subdirectory)/2
                  if procNumber == 0:
                      procNumber = 'No restart files'
                  
                  if os.path.isdir(path):
                    # for each child folder list the files
                    for file in os.listdir(path):
                        allpaths = path + '/' + file
                  
                        # checks to see if the folder has a usernotes or record file and if not copies them from the main config folder
                        checknotes = path + '/usernotes.ini'
                        checkhistory = path + '/record.ini'
                        try:
                            # copies usernotes and record template file from config folder in BOUTgui
                            if not os.path.isfile(checknotes):
                                shutil.copy(currentDir+'/config/usernotes.ini', checknotes)
                            if not os.path.isfile(checkhistory):
                                shutil.copy(currentDir+'/config/record.ini', checkhistory)
                        except IOError:
                            pass
                        # if further folders are encountered within the child folders has a look in them to see if files of the correct type
                        if os.path.isdir(allpaths):
                          for files in os.listdir(allpaths):
                            allfilepaths = allpaths + '/' + files
                            if allfilepaths.endswith(filetype):
                                # for each file in this second child folder the time of creation and modification is found 
                                Time1 = os.path.getctime(allfilepaths)
                                Time2 = os.path.getmtime(allfilepaths)
                                global a
                                a = datetime.fromtimestamp(Time1).strftime("%d %b %Y  %H:%M:%S")
                                global b
                                b = datetime.fromtimestamp(Time2).strftime("%d %b %Y  %H:%M:%S")
                                # comments file is read
                                notespath =  allpaths + '/usernotes.ini'
                                # if there are comments then added to the 
                                if os.path.isfile(notespath):
                                    f= open(notespath, 'r')
                                    filedata = f.read()
                                    f.close
                                    # lists the found files attributes from directory in table in the GUI 
                                    directory.append(('/' + folder + '/' + file + '/' + files,a,b, filedata, procNumber))
                                                                  
                                    
                        if file.endswith(filetype):
                            # does the same as above for files
                            Time1 = os.path.getctime(path)
                            Time2 = os.path.getmtime(path)
                            #global a
                            a = datetime.fromtimestamp(Time1).strftime("%d %b %Y  %H:%M:%S")
                            #global b
                            b = datetime.fromtimestamp(Time2).strftime("%d %b %Y  %H:%M:%S")
                            # adds comments to the directory
                            notespath =  path + '/usernotes.ini'

                            # reads comments     
                            if os.path.isfile(notespath):
                                f= open(notespath, 'r')
                                filedata = f.read()
                                f.close
                                # lists the found files attributes from directory in table in the GUI 
                                directory.append(('/'+str(folder)+'/'+str(file),a,b, filedata, procNumber))
                  # resets subdirectory for next loop
                  subdirectory = []
                                
                               
              for i in range(len(directory)):
                  # call insertTableRow to add a new row, each with all of directories infomation, so filepath, date created, date modified, no proc, comments
                  self.insertTableRow(directory[i][0], directory[i][1], directory[i][2], directory[i][4], directory[i][3])

    def sortdir(self):
        """
        Called by list_archive. This function will sort the directory list so that it has the same order as those in the table
        when the table is resorted, i.e. by clicking on one of the headers to sort by file/ path... other wise the cell row number does not correspond
        with the list item of directory. 
        """
        
        global directory
        # import directory
        length = len(directory)
        # reset directory
        directory = []
        # rebuilds the directory by cycling through the values of the cells in the y = 1 column
        for i in range(length):
            items = self.tableWidget.item(i,0)
            # for each item in items add to directory 
            directory.append(str(items.text()))
        return directory

    
    def buttonAction(self):
        """
        called when load is clicked in the loadinp tab. gets the current row that is selected and sends it to a call of loadinp
        """
        # current row
        row = self.tableWidget.currentRow()
        self.loadinp(row)

    def loadinp(self,x):
        """
        called when loading file by double clicking in the archive and by button action after clicking load.
        The functionality of loadinp changes, if compare is clicked then loadinp doesn't update controls but instead
        loads the compare functions. Loadpath2 is created as indication of compare being clicked and the need for two loadpaths to
        exist to compare with each other
        """
        self.sortdir()
        global loadpath1, loadpath2, procNumber
        # set proc number to same as previous run unless no run data do sets to default 5
        try:        
            procNumber = int(self.tableWidget.item(x,3).text())
        except ValueError:
            procNumber = 5
            
        loadpath = str(archive) + str(directory[x])
        # change headings so readable by config parser
        changeHeadings(loadpath)

        # generally loading will proceed to load from the parser and update the controls
        if 'loadpath2' not in globals():
            loadpath1 = loadpath
            self.procSpin.setValue(procNumber)
            # reads the config file
            parser.read(str(loadpath))
            # starts updateControls and input creation 
            self.updateControls(loadpath)
            # move to change inputs
            self.tabWidget.setCurrentIndex(1)

        # if compare is selected and so loadpath2 declared then only loadpath2 will be changed on file selection
        else:
            # the 'load' button at this point says 'compare' 
            loadpath2 = loadpath
            # runs the compare functions
            self.comparefiles(loadpath1, loadpath2)
            # sets the button back to load
            self.pushButton.setText(QtGui.QApplication.translate("MainWindow", "Load", None, QtGui.QApplication.UnicodeUTF8))
            # delete loadpath2
            del loadpath2        

    def showResize(self):
        """
        Called when view -> Edit Input Positions is chosen. Brings up the resize window to edit positions
        """
        resize.show()

##################################################################################################################

##################################################################################################################
################################################### CHANGE INPUTS ################################################
        
    def updateControls(self, inpfile):
        """
        called every time a new file is loaded, so in the loadinp function and the loadcopied function. Also called when positions in resize are changed/
        The function calls to delete to clear the change inputs tab and resets all the global lists used to store inputs from BOUT.inp the reads the new
        control file (or rereads the old file if positioning is being changed) using config parser. Then calls readConfig and rearrange to sort postioning.
        """
        #  all the global lists involved in input creation
        global inputsLst, sectionLst, inputsTupLst, groupbox, parser, tups
        # trys to delete all the old inputs on the change inputs tab
        try:
            self.delete()
        # skips this step if none have yet been created, i.e. on first time run
        except RuntimeError:
            pass
        except NameError:
            pass
        # resets the global lists
        inputsLst = []
        sectionLst = []
        inputsTupLst = []
        groupbox = []
        # defines the loadpath of the folder of the inp file
        folder = re.sub('/BOUT.inp', '', inpfile)
        # reads the comments file
        text = open(folder + '/usernotes.ini').read()
        # sets comments to appear in the text edit
        self.plainTextEdit.setPlainText(text)
        # calls commentsTup in guifunctions which saves inline comments form being lost
        tups = commentsTup(inpfile)
        # reads the config file
        with open(inpfile) as fp:
            parser = configparser.ConfigParser()
            # calls changeHeadings from guifunctions
            changeHeadings(inpfile)
            parser.optionxform = str
            parser.readfp(fp)
        # sets the label in change inputs tab to equal the correct file path
        self.fileLabel.setText(QtGui.QApplication.translate("MainWindow", str(inpfile), None, QtGui.QApplication.UnicodeUTF8))
        # calls the two functions which create and position the input controls
        self.readConfig()
        self.rearrange()
        
        
    def readConfig(self):
        """
        Called by updateControls. Uses the contents of the selected config file. For each section it creates a new group box to insert controls.
        It then finds all the items within that section and test the data type of that value, inserting either a combobox,
        double combobox or line edit depending into each group box. Objects are created by calls to later functions. 
        """
        global n, sections
        # defines globally a list containing all the sections within that control file
        sections = parser.sections()
        for section in sections:
            # creates a list of all the items in that section
            items = parser.items(section)
            # no of items in the section
            y =len(items)
            # for each section a groupBox is created
            self.createGroupBox(section, y)
            # creates the count n
            n = 1   
            for i in range(len(items)):
                # cycles through all the items in a list
                subkey = items[i][0]
                # removes comments from the item
                value = self.clean(items[i][1], '#')
                # logically works through to test data types
                try:
                    # if integer creates a spin box
                    int(value)                  
                    self.createBox(n , subkey, value, section)
                except ValueError:
                    try:
                        # if a large or small float creates a line edit
                        float(value)
                        if float(value) > 1:
                            self.createLine(n , subkey, value, section)
                        elif float(value) < 0.01:
                            self.createLine(n , subkey, value,section)
                        else:
                        # for floats such as 0.95 (percentages) creates a double spin box 
                            self.createDoubleSpin(n , subkey, value, section)
                    except ValueError:
                        # if not a float try true and false strings to create a combobox with options true or false
                        if value == 'true' or value == 'false':
                            self.createTorF(n , subkey, value, section)
                        else:
                            # if all else fails create a line edit
                            self.createLine(n , subkey, value, section)
                # the n count is used so that each succesivly created input is created in a lower grid position within the groupbox
                n = n + 1
            mycode = 'self.' + section + '.setLayout(self.' + str(section) + 'Grid)'
            exec mycode
            
    def createGroupBox(self, section, y):
        """
        Called by readConfig. creates a new groupbox for each section in the control file and . 
        """

        objectName = section
        sectionLst.append(sectionLst)
        # finds the length of all the input controls in this section
        ylength = 28 + y *21
        # create a groupbox in tab_2 with name = section    
        mycode = 'self.' + objectName + ' = QtGui.QGroupBox(self.tab_2)'
        exec mycode
        # adds the headings to the group boxes of the section
        mycode = 'self.' + objectName + ' .setTitle(QtGui.QApplication.translate("MainWindow", section, None, QtGui.QApplication.UnicodeUTF8))'
        exec mycode
        # create a grid layout with name = sectionGrid
        mycode = 'self.' + objectName + 'Grid'+ '= QtGui.QGridLayout()'
        exec mycode
        # change the balance between the two columns 
        mycode = 'self.' + objectName + 'Grid.setColumnStretch(0,1)'
        exec mycode
        mycode = 'self.' + objectName + 'Grid.setColumnStretch(1,0.4)'
        exec mycode
        # used as a way of storing how long each group box is for rearrange function
        tup = (section, ylength)    
        groupbox.append(tup)
        
      

    def createDoubleSpin(self, n, subkey, value, section):
        """
        Called by readConfig. creates a new double spin for each input item that is a medium sized float. 
        """
        # calls the globals defined by the config file
        global xLabel, xInput, labelWidth, sepInput
        objectName = subkey + 'Double' + section
        # adds to list containing a store of object names
        inputsLst.append(objectName)
        tup = (section, objectName)
        # tuple means that inputs with the same name can be differentiated by section
        inputsTupLst.append(tup)
        # create double spin
        mycode = 'self.' + objectName + ' = QtGui.QDoubleSpinBox(self.' + section +')'
        exec mycode
        # set the attributs of the float, min, max, step, intial value, object name.
        mycode = 'self.' + objectName + '.setMinimum(-1000000.0)'
        exec mycode
        mycode = 'self.' + objectName + '.setMaximum(1000000.0)'
        exec mycode
        mycode = 'self.' + objectName + '.setSingleStep(0.01)'
        exec mycode
        mycode = 'self.' + objectName + '.setProperty("value",' + value + ')'
        exec mycode
        mycode = 'self.' + objectName + '.setObjectName(objectName)'
        exec mycode
        # adds to the grid with the name sectionGrid where section = section of input
        mycode =  'self.' + section + 'Grid' + '.addWidget(self.' + objectName + ',' + str(n) + ',1)'
        exec mycode
        # creates a label in the groupbox of the section
        mycode = 'self.label = QtGui.QLabel(self.' +section + ')'
        exec mycode
        # adds the label to the grid of the correct section
        mycode =  'self.' + section + 'Grid' + '.addWidget(self.label,' + str(n) + ',0)'
        exec mycode
        
        # adds an automatic tooltip based on the comments in the control file
        for i in range(len(tups)):
            # tups is a list of subkeys and their comments
            line = tups[i][0].split()[0]
            # search for subkey comments
            if line == subkey:
                # tooltip is set to the comments of not 'None'
                tooltip = right(str(tups[i][1]), '#')
                if tooltip != 'None':
                  mycode = 'self.' +objectName + '.setToolTip(tooltip)'
                  exec mycode     
        #labels
        self.label.setObjectName("label_n")
        self.label.setText(QtGui.QApplication.translate("MainWindow", subkey, None, QtGui.QApplication.UnicodeUTF8))
        mycode = 'self.' + section + 'Grid' + '.setVerticalSpacing(sepInput)'
        exec mycode


    def createTorF(self, n, subkey, value, section):
        """
        Called by readConfig. creates a new double spin for each input item that is a float. 
        """
        # calls the globals defined by the config file
        global xLabel, xInput, labelWidth, sepInput
        objectName = subkey + 'TorF' + section
        # adds to list containing a store of object names
        inputsLst.append(objectName)
        tup = (section, objectName)
        # tuple means that inputs with the same name can be differentiated by section
        inputsTupLst.append(tup)
        # create combobox
        mycode = 'self.' + objectName + ' = QtGui.QComboBox(self.' + section +')'
        exec mycode
        # add the true false items
        mycode = 'self.' + objectName + '.addItem("true")'
        exec mycode
        mycode = 'self.' + objectName + '.addItem("false")'
        exec mycode
        # set the object name
        mycode = 'self.' + objectName + '.setObjectName(objectName)'
        exec mycode
        # add to the grid for that section
        mycode =  'self.' + section + 'Grid' + '.addWidget(self.' + objectName + ',' + str(n) + ',1)'
        exec mycode
        # create label 
        mycode = 'self.label = QtGui.QLabel(self.' +section + ')'
        exec mycode
        # add to grid
        mycode =  'self.' + section + 'Grid' + '.addWidget(self.label,' + str(n) + ',0)'
        exec mycode
        # set initial position of the box, either true or false value depending
        if value == 'true':
            mycode = 'self.' + objectName + '.setCurrentIndex(0)'
            exec mycode
        else:
            mycode = 'self.' + objectName + '.setCurrentIndex(1)'
            exec mycode
        # adds an automatic tooltip based on the comments in the control file
        for i in range(len(tups)):
            # tups is a list of subkeys and their comments
            line = tups[i][0].split()[0]
            # search for subkey comments
            if line == subkey:
                # tooltip is set to the comments of not 'None'
                tooltip = right(str(tups[i][1]), '#')
                if tooltip != 'None':
                  mycode = 'self.' +objectName + '.setToolTip(tooltip)'
                  exec mycode              
        #labels
        self.label.setObjectName("label_n")
        self.label.setText(QtGui.QApplication.translate("MainWindow", subkey, None, QtGui.QApplication.UnicodeUTF8))
        mycode = 'self.' + section + 'Grid' + '.setVerticalSpacing(sepInput)'
        exec mycode

        
    def createBox(self, n, subkey, value, section):
        """
        creates a new spin box for each input item that is an integer. 
        """
        # calls the globals defined by the config file
        global xLabel, xInput, labelWidth, sepInput
        objectName = subkey + 'Spin' + section
        # adds to list containing a store of object names
        inputsLst.append(objectName)
        tup = (section, objectName)
        # tuple means that inputs with the same name can be differentiated by section
        inputsTupLst.append(tup)
        # create spin box
        mycode = 'self.' + objectName + ' = QtGui.QSpinBox(self.' +section + ')'
        exec mycode
        # set properties of the spin box
        mycode = 'self.' + objectName + '.setMinimum(-1000000)'
        exec mycode
        mycode = 'self.' + objectName + '.setMaximum(1000000)'
        exec mycode
        mycode = 'self.' + objectName + '.setSingleStep(1)'
        exec mycode
        mycode = 'self.' + objectName + '.setProperty("value",' + value + ')'
        exec mycode
        mycode = 'self.' + objectName + '.setObjectName(objectName)'
        exec mycode
        # add the spin box to the grid of that section
        mycode =  'self.' + section + 'Grid.addWidget(self.' + objectName + ',' + str(n) + ',1)'
        exec mycode
        # create a label
        mycode = 'self.label = QtGui.QLabel(self.' +section + ')'
        exec mycode
        # add label to the grid of that section
        mycode =  'self.' + section + 'Grid' + '.addWidget(self.label,' + str(n) + ',0)'
        exec mycode       
        # adds an automatic tooltip based on the comments in the control file
        for i in range(len(tups)):
            # tups is a list of subkeys and their comments
            line = tups[i][0].split()[0]
            # search for subkey comments
            if line == subkey:
                # tooltip is set to the comments of not 'None'
                tooltip = right(str(tups[i][1]), '#')
                if tooltip != 'None':
                  mycode = 'self.' +objectName + '.setToolTip(tooltip)'
                  exec mycode          
        # labels
        self.label.setObjectName("label_n")
        self.label.setText(QtGui.QApplication.translate("MainWindow", subkey, None, QtGui.QApplication.UnicodeUTF8))
        mycode = 'self.' + section + 'Grid' + '.setVerticalSpacing(sepInput)'
        exec mycode        

        
    def createLine(self, n, subkey, value, section):
        """
        creates a new line for each input item that is text. 
        """
        # calls the globals defined by the config file
        global xLabel, xInput, labelWidth, sepInput
        objectName = subkey + 'Line' + section
        # adds to list containing a store of object names
        inputsLst.append(objectName)
        tup = (section, objectName)
        # tuple means that inputs with the same name can be differentiated by section
        inputsTupLst.append(tup)
        # create line edit
        mycode = 'self.' + objectName + ' = QtGui.QLineEdit(self.' + section + ')'
        exec mycode
        # set the parameters of the line edit
        mycode = 'self.' + objectName + '.setObjectName(objectName)'
        exec mycode        
        mycode = 'self.' + objectName + '.setText( str(value))'
        exec mycode
        # add to the grid layout of that section
        mycode =  'self.' + section + 'Grid' + '.addWidget(self.' + objectName + ',' + str(n) + ',1)'
        exec mycode
        # create label
        mycode = 'self.label = QtGui.QLabel(self.' +section + ')'
        exec mycode
        # add to the grid layout of that section
        mycode =  'self.' + section + 'Grid' + '.addWidget(self.label,' + str(n) + ',0)'
        exec mycode
        # adds an automatic tooltip based on the comments in the control file
        for i in range(len(tups)):
            # tups is a list of subkeys and their comments
            line = tups[i][0].split()[0]
            # search for subkey comments
            if line == subkey:
                # tooltip is set to the comments of not 'None'
                tooltip = right(str(tups[i][1]), '#')
                if tooltip != 'None':
                  mycode = 'self.' +objectName + '.setToolTip(tooltip)'
                  exec mycode                       
        # labels
        self.label.setObjectName("label_n")
        self.label.setText(QtGui.QApplication.translate("MainWindow", subkey, None, QtGui.QApplication.UnicodeUTF8))
        mycode = 'self.' + section + 'Grid' + '.setVerticalSpacing(sepInput)'
        exec mycode

        
    def rearrange(self):
        global leftBorder, topBorder, verticalSeperation, maxLength, boxWidth, horizontalSeperation, boxLength
        """
        Called by updateContols. The groupbox list contains the names of all the group boxes and the length of the inputs in that section, stored as a list of tuples,
        it then works out the best arrangement for these by finding frames of sizes that add together to a defined limit.
        For each column of groupboxes that is calculate a scrolllayout is created which is of grid form and a scroll widget created to contain this layout.
        A scroll area is created and the scroll widget put inside of it. Each of the groupboxes contain inputs is then added to the scrolllayout.

        So you end up with input widgets displayed neatly in a grid (as in readConfig), the grid is stored in a group box with the section name as object name and heading
        This group box is contained within a second vertical grid with other group boxes to make up a specified length. This second vertical is itself part of a scroll layout
        which sits within a scroll area. This makes it so that you can have long lists of inputs, longer than the window, as you can scroll up and down the list. 
        """
        # create a second tuples list so that variables can be deleted but keeps the old data intact
        groupbox2 = groupbox
        global n
        # n is a count
        n = 0
        # these loop finds suitable lengths of sets of groupboxes
        while len(groupbox2) > 0:
            # k is also a count
            k = 0
            # newLst is cleared each time a group of suitable length is found and contains the current group
            newLst = [] 
            newLst.append(groupbox2[0])
            # once appended then deleted from list
            del groupbox2[0]
            total = self.total(newLst)
            for i in range(len(groupbox2)):
                # compares current length + current list item to user given maxLength and appends if less.
                if total + int(groupbox2[i-k][1]) < maxLength:
                    newLst.append(groupbox2[i-k])
                    # calls total function to find the length of the current set
                    total = self.total(newLst)
                    del groupbox2[i-k]
                    # k is increased when an object is deleted to get around index errors, so i-k is used
                    k = k + 1   
            # m count, added to for each grooup in set so they aren't produced on top of each other
            m = 0
            #### each of these named dependedent on the n count
            # create scroll layout and widget and put the layout in the widget
            mycode = 'self.scrolllayout' + str(n) +  '= QtGui.QGridLayout()'
            exec mycode
            mycode = 'self.scrollwidget' + str(n) + '= QtGui.QWidget()'
            exec mycode
            mycode = 'self.scrollwidget' + str(n) + '.setLayout(self.scrolllayout' + str(n) + ')'
            exec mycode
            # create scroll area
            mycode = 'self.scroll' + str(n) + '= QtGui.QScrollArea(self.tab_2)'
            exec mycode
            # Set to make the inner widget resize with scroll area
            mycode = 'self.scroll' + str(n) + '.setWidgetResizable(True)'
            exec mycode
            # put the scroll widget in the scroll area
            mycode = 'self.scroll' + str(n) + '.setWidget(self.scrollwidget' + str(n) +')'
            exec mycode
            # set the position and size of the scoll area, each one is position subsequently further right
            mycode = 'self.scroll' + str(n) + '.setGeometry(QtCore.QRect(leftBorder + horizontalSeperation*n, topBorder, boxWidth+ 30, total + verticalSeperation * len(newLst) + 30 * len(newLst)))'
            exec mycode
            # set scroll length as user defined, the longer this is the fewer scroll areas there will be
            mycode = 'self.scroll' + str(n) + '.setMaximumHeight(boxLength)'
            exec mycode
            mycode = 'self.scroll' + str(n) + '.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)'
            exec mycode
            #container widget for the grid
            self.widget = QWidget()
            #layout of container
            self.grid = QtGui.QGridLayout()
            self.grid.setVerticalSpacing(verticalSeperation)
            for obj in newLst:
                # for each groupbox in current set added to grid in row down from the previous              
                mycode = 'self.grid.addWidget(self.' + obj[0] + ',m ,0)'
                exec mycode
                # add to m count
                m = m+1
            # put the grid containing group box into the container widget.   
            self.widget.setLayout(self.grid)
            # put the container widget in the scroll layout
            mycode = 'self.scrolllayout' + str(n) + '.addWidget(self.widget,0,0)'
            exec mycode
            n = n +1
       
    def total(self, Lst):
        """
        Called by rearrange. Is just used to find the total of the input list
        """
        total = 0
        for x in range(len(Lst)):
            total = total + int(Lst[x][1])
        return total
      
    def saveSettings(self, path):

        """
        called by dialogsave.create() when ever a file is saved or run. the for loops in this function go through the whole lit of inputs, remember that inputs in lits are
        stored as input + object + section type, e.g. timingDouble and so removes either 'line', 'double' or 'spin' and then removes section. Remember inputsTupList has input
        stored alongside section so removing section is easy. The change function is then used to update the config file with new values. 
        """
        
        for item in inputsTupLst:
            # looks for line edits and strips
            stripitem = re.sub('Line', '', item[1])
            if stripitem != item[1]:
                # removes section name
                stripitem = re.sub(item[0], '', stripitem)
                mycode = 'self.change(item[0], stripitem, self.' + item[1] + '.text())'
                exec mycode
                
                
        for item in inputsTupLst:
            # looks for doubles and strips
            stripitem = re.sub('Double', '', item[1])
            if stripitem != item[1]:
                # removes section name
                stripitem = re.sub(item[0], '', stripitem)
                mycode = 'self.change(item[0], stripitem, self.' + item[1] + '.value())'
                exec mycode
                
        for item in inputsTupLst:
            # looks for spin and strips
            stripitem = re.sub('Spin', '', item[1])
            if stripitem != item[1]:
                # removes section name
                stripitem = re.sub(item[0], '', stripitem)
                mycode = 'self.change(item[0], stripitem, self.' + item[1] + '.value())'
                exec mycode

        for item in inputsTupLst:
            # looks for TorF and strips
            stripitem = re.sub('TorF', '', item[1])
            if stripitem != item[1]:
                # removes section name
                stripitem = re.sub(item[0], '', stripitem)
                mycode = 'self.change(item[0], stripitem, self.' + item[1] + '.currentText())'
                exec mycode
                
        # writes the file in config parser
        with open (path, 'w') as configfile:
            parser.write(configfile)
        # fixes the headings back to how they should be for running
        returnHeadings(path)

    def change(self, section, option, value):
        """
        changes the value of the section -> option within parser
        """
        parser.set(section, option, value)

    """""""""""""""""""""""
    The exec parts of the code in the create and delete functions are used because I couldn't find a way of using a variable within a line such as self.objectName.setText (etc)
    by this method all are called objectName which won't work for updating the control file. The exec code method allows objectName to be equall to some other value, not just
    literally objectName. Object name takes the form of subkey value + section name. This is to make sure that when two objects of the same name in different sections are
    created they are unique and so can have their own behaviour. 
    """""""""""""""""""""""
    def delete(self):
        """
        Called by updateControls and deletes all the objects created by reading the previous control file using the global lists sections and inputsLst
        deleteLate() means that at the next oppurtunity in the code the specified object is deleted.
        """

        for item in inputsLst:
          # all items are deleted as inputsLst is a list of all the input control buttons
          mycode = 'self.' + item + '.deleteLater()'
          exec mycode
      
      
        for section in sections:
          objectName = section
          # delete all the group boxes, because groupbox name = section
          mycode = 'self.' + objectName + '.deleteLater()'
          exec mycode
          # deletes all the grids used to contain the controls within each groupbox, named objectName + Grid
          mycode = 'self.' + objectName + 'Grid.deleteLater()'
          exec mycode
          
        try:
            # deletes all the scroll layout parts. Named auotmatically scrolllayoutn where n = interger
            # so need to do the same when deleting. In range 1000 as the number of layouts it dynamic, but surely will be less than 1000 
            for n in range(1000):
                mycode = 'self.scrolllayout' + str(n) + '.deleteLater()'
                exec mycode
                mycode = 'self.scrollwidget' + str(n) + '.deleteLater()'
                exec mycode
                mycode = 'self.scroll' + str(n) + '.deleteLater()'
                exec mycode
        # stops when hits Attribute error, when nothing left to delete
        except AttributeError:
            pass

    def disableProc(self):
        """
        called when the restart box is checked in the change inputs tab. Disables the procCombo and sets to original vale - don't want user to be able to chose
        a different number of processors if restarting as this causes a crash
        """
        if self.checkBox.isChecked() == True:
            # restart checked
            global procNumber
            # disables combo and sets to original value
            try:
                self.procSpin.setValue(procNumber)
            except NameError:
                pass
            self.procSpin.setEnabled(False)
        else:
            # re-enables the proc box
            self.procSpin.setEnabled(True)

        # the if not statement looks to see if the current archive is a folder and prompts the user to select one if not on initialisation

    def changerun(self):
        """
        called by clicking on run simulation button. creates a global variable run that changes the save dialog boxes function so
        that clicking on run causes simualtion not just saving then calls the dialog.
        """
        # tests to see whether simulation code is a good path
        if not os.path.isfile(codeFile):
            # if not calls this function which creates a file explorer
            dialogsave.simulationCode()
        # sets the text displayed in the dialog box
        dialogsave.label.setText(QtGui.QApplication.translate("Choose Folder Path", "Save path for control file and comments file:" , None, QtGui.QApplication.UnicodeUTF8))
        # sets the window title of the dialog box
        dialogsave.setWindowTitle(QtGui.QApplication.translate("Dialog", "Save", None, QtGui.QApplication.UnicodeUTF8))
        # creates global run and sets to true
        global run
        run = 'true'
        # shows the save dialog
        self.showDialog()

    def changeScan(self):
        """
        called by clicking on run scanning simulation button. creates a global variable run that changes the save dialog boxes function so
        that clicking on run causes simualtion not just saving
        """
        # tests to see whether simulation code is a good path
        if not os.path.isfile(codeFile):
            # if not calls this function which creates a file explorer
            dialogsave.simulationCode()
        # sets the text displayed in the dialog box
        dialogsave.label.setText(QtGui.QApplication.translate("Choose Folder Path", "General Save Path for Mulitple Runs:" , None, QtGui.QApplication.UnicodeUTF8))
        # sets the window title of the dialog box
        dialogsave.setWindowTitle(QtGui.QApplication.translate("Dialog", "Save", None, QtGui.QApplication.UnicodeUTF8))
        # creates global run and sets to scan
        global run
        run = 'scan'
        # shows the save dialog
        self.showDialog()

    def showDialog(self):
        """
        called by functions changeRun and chagneScan aswell as when the write button is click (pushButton_2)
        Brings up a dialog box in which the save file path is chosen for the control file
        """
        # calls function to append loadpath to line edit 
        dialogsave.updatepath()
        dialogsave.show()
        
################################################## INPUTS TAB ####################################################           
##################################################################################################################

##################################################################################################################
################################################## OUTPUT TAB ####################################################   
      
    def STOP(self):
        """
        called by either a keyboard interupt, clicking stop or going to file -> stop simulation, this may only work for single
        simulations. 
        """
        # proc imported as the process called by subprocess
        global proc
        try:
            # kills the process
            os.killpg(proc.pid, signal.SIGINT)
        except OSError:
            pass

##################################################################################################################
          
##################################################################################################################
############################################## GRAPHING TAB CODE STARTS ##########################################
        

    def collectit(self):
        """
        called by clicking on the collect button. Checks to see is anything has been loaded, and if not shows a dialog box and moves to load tab,
        if so then runs the collect function
        """
        # if nothing loaded
        if loadpath1 == 'empty':
            # create dialog and set text
            generalDialog.label.setText(QtGui.QApplication.translate("Load folder", "Please load folder to collect from" , None, QtGui.QApplication.UnicodeUTF8))
            # set dialog window title
            generalDialog.setWindowTitle(QtGui.QApplication.translate("Dialogcompare", "Load Folder", None, QtGui.QApplication.UnicodeUTF8))
            # move to load tab
            self.tabWidget.setCurrentIndex(0)
            generalDialog.show()
        else:
            # set path of collection as parent folder of BOUT.inp file
            newpath = re.sub('/BOUT.inp', '', loadpath1)
            # run the collect function
            self.collect(newpath)

    def collect(self, path):
        """
        Called by collectit and clicking exit on the default variables dialog (function is addDefaultVar.Close)
        starts a thread to run the collect routines in the background, stops the gui from sticking
        """
        # call WorkerCollect
        self.workercollect = WorkerCollect(path)
        if self.workercollect.isRunning():
          # quit if running
                self.workercollect.quit()
        if not self.workercollect.isRunning():
          # else start the worker
            self.workercollect.exiting= False
            self.workercollect.start()

    def collectExtra(self):
        """
        called when the 'collect variable' button is clicked to collect non-default variable manually. Adds and collects selected variable
        to the other variables that were previously collected automatically . Removes from the extra variables lists and combo box and appends to the loaded inputs. 
        """
        # import the data stores created in workercollect
        global notLoadedLst, varDic, plotLst
        from boutdata import collect
        #find the currently selected variable
        i = self.extraVarsCombo.currentIndex()
        var = notLoadedLst[i]
        del notLoadedLst[i]
        # add to new and remvoe from old
        self.variableCombo.addItem(var)
        self.extraVarsCombo.removeItem(i)
        # so on the list of variables that can be plotted
        plotLst.append(var)
        # gui collect
        a = collect(str(var))
        varDic[var] = a
        # command line collect
        window.commandEntered(str(var.strip(',.').lower())+ '= collect(' +'"'+str(var)+ '"' + ')')

    def list_defaults(self):
        """
        called by loadDefault and when the mainwindow is initialised. Based on the list_archive function this finds all the files in the defaults
        folder within the config folder
         """
        global defaultLst
        # creates blank default list
        defaultLst = []
        # lists all default in Defaults folder in BOUTgui, this folder should only contain defaults
        defaultLst = os.listdir(currentDir+ '/Defaults')
        iniLst = []
        for file in defaultLst:
            # defaults saved as .ini
            if file.endswith('ini'):
                iniLst.append(file)
        return iniLst
      
    def appendToCombo(self):
          """
          called when file is saved and when self.window() is called. uses the defaultLst created by list_defaults to populate a combobox
          """
          global defaultLst
          lst = defaultLst
          # clear the combo initially
          self.defaultCombo.clear()
          for file in lst:
                  # for each file pass to parser and read getting the title to append to the combobox
                  parser2.read(currentDir+ '/Defaults/' + str(file))
                  name = parser2.get('heading', 'title')
                  self.defaultCombo.addItem(name)

    def loadDefault(self):
          """
          the call for this create in the initialisation section. Everytime the defaults combo is changed this is called. Sets the setting of the
          graphical graphing plot box to be the same as stored in the .ini file. 
          """
          try:
              # get the index number selected
              index = int(self.defaultCombo.currentIndex())
              lst = (self.list_defaults())
              # use index to find the correct default in list
              default = lst[index]
              # parser then reads that file from defaults folder
              parser2.read(currentDir+ '/Defaults/' + default)
              # get all the values
              self.xspin.setValue(int(parser2.get('others','x')))
              self.yspin.setValue(int(parser2.get('others','y')))
              self.zspin.setValue(int(parser2.get('others','z')))
              self.tspin.setValue(int(parser2.get('others','time')))
              self.variableCombo.setCurrentIndex(int(parser2.get('main', 'variable')))
              # if t,x,y,z is True then this means tick all. 
              if parser2.get('checkboxes', 'time') == 'True':
                      self.tall.setCheckState(Qt.Checked)
              else:
                      self.tall.setCheckState(Qt.Unchecked)
              if parser2.get('checkboxes', 'x') == 'True':
                      self.xall.setCheckState(Qt.Checked)
              else:
                      self.xall.setCheckState(Qt.Unchecked)
              if parser2.get('checkboxes', 'y') == 'True':
                      self.yall.setCheckState(Qt.Checked)
              else:
                      self.yall.setCheckState(Qt.Unchecked)
              if parser2.get('checkboxes', 'z') == 'True':
                      self.zall.setCheckState(Qt.Checked)
              else:
                      self.zall.setCheckState(Qt.Unchecked)
              # incase of problem doesn't load
          except IndexError:
              pass
            
    def saveDefault(self):
          """
          called when the save button is clicked on the graphing tab. brings up a dialog box to name the default
          """
          defaultSave.show()

    def deleteDefault(self):
          """
          called when delete is clicked on the graphin tab. removes the selected defaults ascosiated file then recalls append to combo to refresh the gui
          """
          # define the file to be deleted
          delFile = self.defaultCombo.currentText() + '.ini'
          delFile = currentDir + '/Defaults/' + delFile
          # delete that file
          os.remove(delFile)
          global defaultLst
          # delete from defaultLst
          del defaultLst[self.defaultCombo.currentIndex()]
          # use defaultLst to reappend to combo 
          self.appendToCombo()

    """
    These four functions are of the same form of the disableProc function and of each other. The are called by the state changed calls of the 'All' checkboxes.
    The code for these are found in the graphing tab part of the initialisation under the checkboxes part. When checked the spinbox that they correspond to (i.e.
    t, x, y, z) is disabled to indicate to the user that this bears no relation to the plotting as checking plots against all. 
    """  
    def disablet(self):
         # for time coordinate
        if self.tall.isChecked() == True:
            # disable
            self.tspin.setEnabled(False)
        else:
            # enable
            self.tspin.setEnabled(True)
        
    def disablex(self):
        # for x coordinate
        if self.xall.isChecked() == True:
            # disable
            self.xspin.setEnabled(False)
        else:
            # enable
            self.xspin.setEnabled(True)      

        
    def disabley(self):
        # for y coordinate
        if self.yall.isChecked() == True:
            # disable
            self.yspin.setEnabled(False)
        else:
            # enable
            self.yspin.setEnabled(True)      

        
    def disablez(self):
        # for z coordinate
        if self.zall.isChecked() == True:
            # disable
            self.zspin.setEnabled(False)
        else:
            # enable
            self.zspin.setEnabled(True)      
            
    def rungraph(self):
        """
        called when 'create graph' is clicked. Starts the worker2 thread which creates graph, prevents the gui from freezing up when the graph is created
        """
        self.worker2 = Worker2()
        if self.worker2.isRunning():
              # if already running quit
                self.worker2.quit()
        if not self.worker2.isRunning():
              # otherwise (usually) start
            self.worker2.exiting= False
            self.worker2.start()
          
          
############################################## COMMAND LINE CODE STARTS ##########################################

# This part of the code was taken from a file with an application called PyXPad authored
# by Ben Dudson, Department of Physics, University of York, benjamin.dudson@york.ac.uk 
#
# PyXPad is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PyXPad is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.

    def write(self, text):
        """
        Write some log text to output text widget
        """
        self.textOutput.ensureCursorVisible()
        self.textOutput.append(text)
        self.textOutput.ensureCursorVisible()
        

    def makeUnique(self, name):
        """
        Modifies a given string into a valid Python variable name
        which is not already in self.data
        
        Input
        -----
            name  ::  string

            self.data   (class member)
            
        Returns
        ------
            string containing modified name

        Modifies
        --------
            None
        """
        # First make sure the name is a valid variable name
        name = re.sub(b'\W|^(?=\d)','_', name) # Replace invalid characters with '_'
        
        if iskeyword(name): # Check if name is a keyword
            name += '2'

        if name in self.data:
            # Name is already in the list. Add a number to the end to make it unique
            i = 1
            while name + "_"+str(i) in self.data:
                i += 1
            return name + "_"+str(i)
        return name

    def uniqueName(self):
        """
        Generates a unique variable name, which
        is not already in self.data
        """
        
        def findName(name,length):
            """
            Finds a name
            """
            for c in string.ascii_lowercase:
                if length <= 1:
                    if not name+c in self.data:
                        return name+c
                else:
                    r = findName(name+c,length-1)
                    if r != None:
                        return r
            return None
        
        length = 1
        while True:
            n = findName("",length)
            if n != None:
                return n
            length += 1
            
    def updateDataTable(self):
        """
        Updates the table of data based on self.data dictionary
        """
        n = len(self.data)
        table = self.dataTable
        table.setSortingEnabled(False) # Stops the table rearranging itself
        self.dataTable.cellChanged.disconnect(self.dataTableChanged) # Don't call the dataTableChanged function
        table.setRowCount(n)
        for row, name in enumerate(self.data):
            item = self.data[name]
            it = QTableWidgetItem(name)
            it.oldname = name # Save this for when it's changed
            table.setItem(row, 0, it)
            
            # Assume it's an XPadDataItem
            try:
                it = QTableWidgetItem(item.source)
                it.setFlags(it.flags() ^ Qt.ItemIsEditable); # Make source read only
                table.setItem(row, 1, it)
            except:
                table.setItem(row, 1, QTableWidgetItem(""))    
            
            try:
                it = QTableWidgetItem(item.name)
                it.setFlags(it.flags() ^ Qt.ItemIsEditable); # Make trace read only
                table.setItem(row, 2, it)
            except:
                table.setItem(row, 2, QTableWidgetItem(""))
                
            try:
                try:
                    comment = item.comment
                except AttributeError:
                    comment = item.desc
                    if comment == "":
                        comment = item.label
                        if item.units != "":
                            comment += " ("+item.units+") "
                
                    if item.dim != []:
                        comment += " [" + item.dim[0].name
                        for d in item.dim[1:]:
                            comment += ", " + d.name
                        comment += "] "
                    else:
                        comment += " = " + str(item.data)
                
                table.setItem(row, 3, QTableWidgetItem(comment))
            except:
                table.setItem(row, 3, QTableWidgetItem(str(item)))
            
        table.setSortingEnabled(True)  # Re-enable sorting
        self.dataTable.cellChanged.connect(self.dataTableChanged)
        
    def dataTableChanged(self, row, col):
        """
        Called when the user changes the value of a cell
        in the data table. This can either be to change 
        the name of a variable, or the comment.
        """
        if col == 0:
            # The name of the variable
            it = self.dataTable.item(row, col)
            name = toStr(it.text())
            oldname = it.oldname
            if name == oldname:
                return # Not really changed
            
            # Need to make sure new name is unique and valid
            name = self.makeUnique(name)
            it.setText(name)
            it.oldname = name
            self.data[name] = self.data[oldname]
            del self.data[oldname]
        
    def commandEntered(self, text):
        """
        Called when a command is entered on the Data tab.
        Gets the command string from the text box, and calls
        the runCommand to run the command.
        """
        # Get the command text and clear the text box
        cmd = toStr(text)
        self.commandInput.clear()
        self.runCommand(cmd)

    def runSandboxed(self, func, args=()):
        # To capture print statements stdout is temporarily directed to a StringIO buffer
        buffer = StringIO()
        oldstdout = sys.stdout
        sys.stdout = buffer
        val = None
        try:
            val = func(*args)
        except:
            e = sys.exc_info()
            self.write("Error: " + str(e[0]))
            self.write("Reason: " + str(e[1]))
        sys.stdout = oldstdout
        output = buffer.getvalue()
        if len(output) > 0:
            self.write(output)
        return val

    def _runExec(self, cmd, glob, loc):
        """
        This is a wrapper around exec
        Needed because exec isn't allowed in a lambda or nested function
        and can't be passed as a function pointer.
        """
        exec(cmd, glob, loc)
    
    def runCommand(self, cmd):
        # Output the command
        self.write(">>> " + cmd)
        
        glob = globals()
        glob['plot'] = self.DataPlot.plotdata
        glob['variables'] = self.showVariables
        # Evaluate the command, catching any exceptions
        # Local scope is set to self.data to allow access to user data
        self.runSandboxed(self._runExec, args=(cmd, glob, self.data))
        self.updateDataTable()
        


##### command line functions           
    def showVariables(self):
          """
          called from the command line when typing 'variables()' see runCommand above. shows all the 4D variables
          """
          # path of folder containing data files
          path = re.sub('/BOUT.inp', '', loadpath1)
          #change directory to path
          os.chdir(path)

          # load data file 
          d = DataFile('BOUT.dmp.0.nc')

          # create a list of keys in the data file
          d.keys()

          # want all the keys that contain 4 dimensions
          for v in d.keys():
                  if d.ndims(v)==4:
                           print v

############################################## COMMAND LINE CODE ENDS ############################################


############################################## GRAPHING TAB CODE ENDS ############################################
##################################################################################################################


########################################### CODE FOR OTHER MENU ACTIONS ##########################################                           
    def FileHistoryClicked(self):
        """
        called when file -> filehistory is clicked. so filehistory action. loads the record.ini file into a new window if a control file has
        been loaded to show that files history
        """
        # if nothing from archive has been loaded
        if loadpath1 == 'empty':
            # set the text of the dialog box
            generalDialog.label.setText(QtGui.QApplication.translate("Dialog", "Please load initial file first" , None, QtGui.QApplication.UnicodeUTF8))
            # set the window name
            generalDialog.setWindowTitle(QtGui.QApplication.translate("Dialogcompare", "Load Initial File", None, QtGui.QApplication.UnicodeUTF8))
            # create the dialog box
            generalDialog.show()
        else:
            # path set from control file to record.ini
            newpath = re.sub('/BOUT.inp', '', loadpath1)
            newpath = newpath + '/record.ini'
            # read the file
            f = open(newpath, 'r')
            data = f.read()
            f.close
            # set the text browser to show the data of the file.
            txthist.textBrowser.clear()
            txthist.textBrowser.setPlainText(data)      #if PlainText not used then get strange formatting
            txthist.show()

    def compareClicked(self):
        """
        called when fileAction compare is clicked, file -> compare. Changes the load table to compare mode to allow a second file to be chosen, creating the loadpath2
        global variable open which loadinp is dependent in its if/ else statement and loadpath1 and loadpath2 can be fed into the compare function,
        after this reverts the table back to load mode
        """
        # if no initial file has been loaded
        if loadpath1 == 'empty':
            # sets dialog text asking to load a file first
            generalDialog.label.setText(QtGui.QApplication.translate("Dialog", "Please load initial file before comparison" +'\n' + "can be made", None, QtGui.QApplication.UnicodeUTF8))
            # sets window name
            generalDialog.setWindowTitle(QtGui.QApplication.translate("Dialogcompare", "Load File 1 to Compare", None, QtGui.QApplication.UnicodeUTF8))
            # shows the dialog box
            generalDialog.show()
            self.tabWidget.setCurrentIndex(0)
        else:
            print loadpath1
            # take to load tab
            self.tabWidget.setCurrentIndex(0)
            # set dialog text
            generalDialog.label.setText(QtGui.QApplication.translate("Dialog", "Choose a file to compare with", None, QtGui.QApplication.UnicodeUTF8))
            # set window name
            generalDialog.setWindowTitle(QtGui.QApplication.translate("Dialogcompare", "Load File 2 to Compare", None, QtGui.QApplication.UnicodeUTF8))
            # show the dialog box
            generalDialog.show()
            # change the loadbutton to 'compare' 
            self.pushButton.setText(QtGui.QApplication.translate("MainWindow", "Compare", None, QtGui.QApplication.UnicodeUTF8))
            # creation of loadpath 2, causes loadinp to follow compare routines not load 
            global loadpath2        
            loadpath2 = 'x'

            
    def comparefiles(self, loadpath1, loadpath2):
        """
        called by self.loadinp. Gets the two files in loadpath1 and loadpath2, reads them both and compares the difference between them.
        A text browser is displayed as a pop up with all the differnt lines show. old lines are shown as a - and new as +
        """
        # read the two files
        with open(loadpath1, 'r') as sf1, open(loadpath2, 'r') as sf2:
            lineA = sf1.readlines()
            lineB = sf2.readlines()
        # compare lines
        d = difflib.Differ()
        diff = d.compare(lineA, lineB)
        # if lines start with '-' appended to a
        a =  '\n'.join(self.clean(str(x[0:]),'#') for x in diff if x.startswith('- '))           
        d = difflib.Differ()
        diff = d.compare(lineA, lineB)
        # if lines start with '+' append to b
        b = '\n'.join(self.clean(str(x[0:]), '#') for x in diff if x.startswith('+ '))

        # saves to the text edit tab
        txt.textBrowser.clear()
        # insert all the text
        txt.textBrowser.insertPlainText('\n' + 'Differences between files' + '\n')
        txt.textBrowser.insertPlainText('\n' + 'Content of File 1' + '\n' + str(loadpath1) + '\n'+ str(a) )
        txt.textBrowser.insertPlainText('\n' + '\n' + 'Content of File 2'+ '\n' + str(loadpath2) + '\n' + '\n' + str(b))
        # show the text dialog popup 
        txt.show()

        
    def show_Variables(self):
        """
        called by the menu action file -> default variables. Shows the window for changing default collect variables
        """
        addDefaultVar.show()

    def showAbout(self):
        txt.textBrowser.clear()
        txt.textBrowser.insertPlainText('BOUTgui  Copyright (C) 2015  Joseph Henderson \n This program comes with ABSOLUTELY NO WARRANTY \n This is free software, and you are welcome to redistribute it\n under certain conditions \n\n\n')
        txt.show()
        with open('licence.txt', 'r') as alllines:
            lines = alllines.readlines()
            for line in lines:
                txt.textBrowser.insertPlainText(str(line))
        
    def openHelp(self):
          """
          called when help -> help is clicked or f11 pressed.
          opens the help file which is stored as an HTML for loading within a text editior
          """
          # changes directory to where BOUTgui is installed incase collect has been run
          os.chdir(oldDir)
          # this just uses a subprocess command to linux terminal to load the help pdf using evince. Perhaps not the best help method but easy, would do more if had more time
          proc = subprocess.Popen(['evince', 'InstallationandRunningGuide.pdf'])

        
##################################################################################################################
# END OF MAINWINDOW ##############################################################################################
##################################################################################################################

####################################### NEW CLASS #######################################

class resize(QtGui.QMainWindow, Ui_Resize):
    """
    called when clicking view -> edit input positioning
    Creates a a small window which contains lots of variables to change the appearence of the control boxes as created automtically
    so that the user can make sure they are best organised. 
    """
    def __init__(self, parent=None):
        """
        Initialisation routine
        """
        # These calls set up the window
    def __init__(self, parent=None):
        """
        Initialisation routine
        """
        # These calls set up the window
        super(resize, self).__init__(parent)
        self.setupUi(self)

        # initialise the resize window with values from the config file using the position parsed file from the start
        self.leftSpin.setValue(int(position.get('appearance', 'leftborder')))
        self.vSpin.setValue(int(position.get('appearance', 'verticalseperation')))
        self.topSpin.setValue(int(position.get('appearance', 'topborder')))
        self.maxSpin.setValue(int(position.get('appearance', 'maxlength')))
        self.widthSpin.setValue(int(position.get('appearance', 'boxwidth')))
        self.hSpin.setValue(int(position.get('appearance', 'horizontalseperation')))
        self.inputSepSpin.setValue(int(position.get('appearance', 'sepinput')))
        self.boxLengthSpin.setValue(int(position.get('appearance', 'boxlength')))

        # changes the config file that has been read into the system
        self.leftSpin.valueChanged.connect(lambda: position.set('appearance', 'leftborder',self.leftSpin.value()))
        self.vSpin.valueChanged.connect(lambda: position.set('appearance', 'verticalseperation',self.vSpin.value()))
        self.topSpin.valueChanged.connect(lambda: position.set('appearance', 'topborder',self.topSpin.value()))
        self.maxSpin.valueChanged.connect(lambda: position.set('appearance', 'maxlength',self.maxSpin.value()))
        self.widthSpin.valueChanged.connect(lambda: position.set('appearance', 'boxwidth',self.widthSpin.value()))
        self.hSpin.valueChanged.connect(lambda: position.set('appearance', 'horizontalseperation',self.hSpin.value()))
        self.inputSepSpin.valueChanged.connect(lambda: position.set('appearance', 'sepinput',self.inputSepSpin.value()))
        self.boxLengthSpin.valueChanged.connect(lambda: position.set('appearance', 'boxlength',self.boxLengthSpin.value()))

        #  configures the button box
        self.ok.clicked.connect(self.updateConfig)
        self.ok.clicked.connect(self.close)
        self.cancel.clicked.connect(self.close)
        self.apply.clicked.connect(self.updateConfig)

    def updateConfig(self):
        """
        called when ok in the resize dialog is clicked. Writes all changes that have been made in the dialog box to the config file
        """
        global config
        # writes to position
        with open (config, 'w') as configfile:
            position.write(configfile)
        # calls update values below, 
        self.updateValues()


    def updateValues(self):
        """
        called by updateConfig. Updates the positions of the boxes and inputs in the inputs tab taknig into account the changes to the control file that have been made. 
        """
        global leftBorder, verticalSeperation, topBorder, maxLength, boxWidth, horizontalSeperation, xLabel, xInput, labelWidth, sepInput, loadpath1, boxLength
        # reads config file using config parser for position
        with open(config) as fp:
            position = configparser.ConfigParser()
            position.optionxform = str
            position.readfp(fp)
        # collects all the different variables to do with size and position
        leftBorder = int(position.get('appearance', 'leftborder'))
        verticalSeperation = int(position.get('appearance', 'verticalseperation'))
        topBorder = int(position.get('appearance', 'topborder'))
        maxLength = int(position.get('appearance', 'maxlength'))
        boxWidth = int(position.get('appearance', 'boxwidth'))
        horizontalSeperation = int(position.get('appearance', 'horizontalseperation'))
        boxLength = int(position.get('appearance', 'boxlength'))
        sepInput = int(position.get('appearance', 'sepinput'))

        # the only way to get changes made here to appear on screen is to 'change tabs'.
        # this tab changing isn't visible but it seems to clear the memory
        window.tabWidget.setCurrentIndex(0)
        # calls updateControls to put all the controls in the right place
        if loadpath1 == 'empty':
             window.updateControls(loadpath)
        else:
             loadpath1 = re.sub('/BOUT.inp', '', loadpath1)
             window.updateControls(loadpath1 + '/BOUT.inp')
        # return to original tab
        window.tabWidget.setCurrentIndex(1)


####################################### NEW CLASS #######################################

class dialogsave(QtGui.QMainWindow, Ui_Dialog):
        """
        called when either write, run simulation or run scanned simulation buttons are clicked in the change inputs tab
        the general order for saving goes... the user can either choose to run simulation or to write a new file. This changes the global variable run to True if running,
        scan if scanned running or false if not. The new path for saving to is set by default other older. This path is used as the default text in the dialog box. This can be
        changed. Create is then called. This checks to see if the path already exists and will create a new directory if not. It then copies all the files from the old folder
        into the new one. This ensures that all the dmp, log and restart files can be accessed for each run. Then the BOUT.inp, usernotes.ini and record.ini files are replaced
        with the new ones, created accorinding to the user inputs. The save function also calls the restart function. If run == True then this will test whether a restart
        is required and call tunit with either 'y' or 'n'. If scanned runs are required then runScan is called rather than restart. 
        """
        
        def __init__(self, parent=None):
                """
                Initialisation routine
                """
                # These calls set up the window
                super(dialogsave, self).__init__(parent)
                self.setupUi(self)
                # codes the button box of the dialog box                
                self.buttonBox.accepted.connect(self.save)
                self.buttonBox.rejected.connect(self.close)
                self.buttonBox.accepted.connect(self.close)

        
        def simulationCode(self):
                """
                called by changescan and change run if no simulation code is detetected. brings up a dialogbox leading to the load simulation code box
                """
                dialogSimulation.show()

        def loadSimCode(self):
                """
                called when file-> simulation code is clicked rather than dialogSimulation which pops up if a run is attempted without .
                also brings up file explorer to choose the filepath of the simulaiton code
                """
                # brings up file dialog
                codeFile = QtGui.QFileDialog.getOpenFileNames(self, "Load simulation code file", QtCore.QDir.currentPath())
                codeFile = codeFile[0][0]
                # sets the codeFile to the config parser
                position.set('exe', 'path', codeFile)
                # saves changes to position
                with open(config, 'w') as configfile:
                    position.write(configfile)
                # sets label at bottom of change inputs tab
                if os.path.isfile(codeFile):
                    window.simulationFile.setText(codeFile)
                else:
                    window.simulationFile.setText('None or bad filepath')
                        

        def updatepath(self):
                """
                defined because the path in the save box wasn't updating after multiple clicks
                """
                savepath = re.sub('/BOUT.inp', '', loadpath1)
                self.lineEdit.setText(savepath)
        
        def save(self):
                """
                called by clicking save in the button box of dialog save uses the displayed text to create a path to save to, so may be different
                to the automatic inital path
                """
                #path of new file
                path = self.lineEdit.displayText()  
                # calls create with the path in the lineEdit
                self.create(path)
                #adds the new file to the table in tab 1
                window.list_archive('inp')      
                global run
                # looks at global run to see whether scan or run was clicked
                if run == 'scan':
                  # if scan calls runScan and closes dialog
                  scan.runScan()
                  self.close()
                else:
                  # if True/ other calls restart and closes
                  self.restart(path)
                  self.close()
        
        def create(self, path):
                """
                creates a new folder in the archive for the next run to store config file, record.ini and usernotes.ini
                """
                # path = the path input in the save dialog box
                oldfolder = re.sub('/BOUT.inp', '', loadpath1)
                # if destination is different to source
                if path != oldfolder:
                      # if destination is new creates it
                      if not os.path.isdir(path):       
                            os.makedirs(path)        
                      newfolder = path      
                      oldfiles = os.listdir(oldfolder)
                      # copies all files from the old file path to the new folder
                      for file in oldfiles:
                        oldfilepath = oldfolder + '/' + file
                        newfilepath = newfolder + '/' + file
                        shutil.copy(oldfilepath, newfilepath)
                      # updates the usernotes after copying
                      if os.path.isfile(oldfolder + '/usernotes.ini'):      
                          shutil.copy(oldfolder + '/usernotes.ini', newfolder + '/usernotes.ini')
                          with open(newfolder + '/usernotes.ini', 'wt') as file:
                              file.write(window.plainTextEdit.toPlainText())
                          file.close()
                      # unless already exist in which case overwrites them
                      if not os.path.isfile(oldfolder + '/usernotes.ini'):
                          with open(newfolder + '/usernotes.ini', 'wt') as file:
                              file.write(window.plainTextEdit.toPlainText())
                          file.close()
                      # updates the history file, function called from GUI functions    
                      parentDir(loadpath1, path)  
                      path = path + '/' + 'BOUT.inp'
                      # write an updated BOUT control file by calling to save
                      window.saveSettings(path)       
                else:
                      # if same folder selceted update BOUT file
                      path = path + '/' + 'BOUT.inp'    
                      window.saveSettings(path)
                      # overwrite comments
                      with open(oldfolder + '/usernotes.ini', 'wt') as file:
                          file.write(window.plainTextEdit.toPlainText())
                      file.close()
                      
                # reset the table     
                window.tableWidget.clearContents()
                window.tableWidget.setRowCount(0)
                        
                      

        def restart(self, path):
                """
                called by save if the run button was intially pressed.
                determines whether the restart box has been ticked and changes the arguments received by mpi run, i.e. 'y' or 'n'
                then calls the runit function
                """
                global run, loadpath1
                if run == 'true':
                    # runfolder maybe the same or different to loadpath
                    runfolder = re.sub('/BOUT.inp', '', path)
                    loadpath = re.sub('/BOUT.inp', '', loadpath1)
                    # test restart and set
                    restart = window.checkBox.isChecked()
                    # set no proc
                    numProc = window.procSpin.value()
                    # set nice level
                    nice = window.niceSpin.value()
                    # if not restart then all runit to start the subprocess
                    if restart == False:
                        self.runit(runfolder, 'n', numProc, nice)
                    else:
                    # if restart true then test to see if there are restart files
                        inputfiles = os.listdir(runfolder)
                        for restartfile in inputfiles:
                            filepath = os.path.join(loadpath, 'BOUT.restart.0.nc')
                            # if yes then proceed
                            if os.path.isfile(filepath):
                                restart = 'y'
                            # if not then display dialog to say no restart files
                            else:
                              # change text of general dialog
                                generalDialog.label.setText(QtGui.QApplication.translate("Dialog", "No restart files in folder!" , None, QtGui.QApplication.UnicodeUTF8))
                              # set window title
                                generalDialog.setWindowTitle(QtGui.QApplication.translate("Dialogcompare", "No restart files", None, QtGui.QApplication.UnicodeUTF8))
                                generalDialog.show()
                        # if yes to restart files then proceed with run 
                        if restart == 'y':
                                self.runit(runfolder, 'y', numProc, nice)

                    run = 'false'


        def runit(self, path, restart, numProc, nice):
                """
                called by restart. Starts the worker thread to start running in the background the subprocess of the simulation
                """
                # call to the worker
                self.worker = Worker(path, restart, numProc, nice, window.outputStream)
                # moves to the output tab
                window.tabWidget.setCurrentIndex(2)
                # if not already running then starts the thread 
                if not self.worker.isRunning():
                        self.worker.exiting= False
                        self.worker.start()
                        # this line links the output of the code to the printit function
                        self.worker.dataLine1.connect(self.printit)


        def printit(self, value):
                """
                connected to worker.dataLine1 by runit. everytime that there is a printable output from the proc subprocess this printit functions is called
                sends the signalled text from the worker to the output stream and appends to the text browser
                """
                
                if value == '' and proc.poll() is not None:
                        # if reaches the end of the process stop printing black space
                        pass
                else:
                        # prints to the text edit
                        window.outputStream.insertPlainText(value)
                        # this means that as stuff is added to the screen the cursor follows it 
                        window.outputStream.ensureCursorVisible()
                        
   
####################################### NEW CLASS #######################################

class dialogSimulation(QtGui.QMainWindow, Ui_dialogSimulation):
    """
    This class is written to be called if the code is attempted to be run without a correct simulation file in place
    and is called by dialogsave
    """
    def __init__(self, parent=None):
        """
        Initialisation routine
        """
        # These calls set up the window
        super(dialogSimulation, self).__init__(parent)
        # makes the dialog appear above the rest
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setupUi(self)
        # when ok is clicked calls chooseSimulation
        self.pushButton.clicked.connect(self.chooseSimulation)
        

    def chooseSimulation(self):
        """
        called when ok of dialog simulation is clicked, brings up a file explorer to select simulation code 
        """
        global codeFile
        self.close()
        # load simulation code
        codeFile = QtGui.QFileDialog.getOpenFileNames(self, "Load simulation code file", QtCore.QDir.currentPath())
        codeFile = codeFile[0][0]
        # set exe in config file to codeFile path
        position.set('exe', 'path', codeFile)
        with open(config, 'w') as configfile:
            position.write(configfile)
        # if file set label to simulation file else display the error message
        if os.path.isfile(codeFile):
            window.simulationFile.setText(codeFile)
        else:
            window.simulationFile.setText('None or bad file path')
                                   
####################################### NEW CLASS #######################################

class Scandialog(QtGui.QMainWindow, Ui_ScanDialog):
    """
    This loads up the dialog box which contains all the inputs for the scanned runs. Scanned runs differ to normal runs in that they allow the user to run multiple runs
    using similar settings but for an increment on one or two of the variables. This is useful if you want to do a powering up sort of thing or look at how one variable
    changes another. it should be possible to increase by 'raw' amount where basically the specified number is added each run or by a percentage where it is multipled by
    the number each time.
    """
    def __init__(self, parent=None):
        """
        Initialisation routine
        """
        # These calls set up the window
        super(Scandialog, self).__init__(parent)
        self.setupUi(self)

        # when the comboboxes are changed in scandialog connect to these functions
        self.sectionCombo.currentIndexChanged.connect(self.appendItems)
        self.indexCombo.currentIndexChanged.connect(self.loadInitial)
        self.sectionCombo_2.currentIndexChanged.connect(self.appendItems2)
        self.indexCombo_2.currentIndexChanged.connect(self.loadInitial2)

        # calls to close and run 
        self.pushButton.clicked.connect(self.run)
        self.pushButton_2.clicked.connect(self.close)
        
    """
    The append functions and loadInitial functions read the config file and build up combo boxes based on the headings and options within the file.
    Clicking on a heading for the first combo box loads its options to the second combo box. The value of that option is then
    displayed in the line. There are two of each function to make it possible to scan two variables at once
    """
    try:
        # changes the headings so that they can be read be config parser
        changeHeadings(loadpath1)
        # tells parser to read the file
        with open(loadpath1) as fp:
            parser = configparser.ConfigParser()
            parser.optionxform = str
            parser.readfp(fp)
    # this only happens if a file has been loaded otherwise get an error and make an exception 
    except IOError:
        pass

    def runScan(self):
          """
          runScan is called in the savedialog once the path has been selected. it is used to setup the scandialog with initial values and sections by using loadpath1
          """
          self.show()
          # clears all previous sections
          self.sectionCombo.clear()
          self.sectionCombo_2.clear()
          # changesheadings in BOUT.inp incase not readable by config parser
          changeHeadings(loadpath1)
          parser.read(loadpath1)
          # reads all the sections and adds them to the combo box
          global sections
          sections = parser.sections()
          for section in sections:
            self.sectionCombo.addItem(section)
            items = parser.items(section)
          scan.appendItems()
          # reads all the sections and adds them to the combo box2
          for section in sections:
            self.sectionCombo_2.addItem(section)
            items = parser.items(section)
          self.appendItems2()
        
    def appendItems(self):
        # clears the index combobox
        self.indexCombo.clear()
        # finds all the indexs for the section selected in the section combox
        index = self.sectionCombo.currentIndex()
        currentSection = parser.items(sections[index])
        # for each item they are appended to the index combobox
        for item in currentSection:
          self.indexCombo.addItem(str(item[0]))
          
    def appendItems2(self):
        # clears the index combobox
        self.indexCombo_2.clear()
        # finds all the indexs for the section selected in the section combox
        index = self.sectionCombo_2.currentIndex()
        currentSection = parser.items(sections[index])
        # for each item they are appended to the index combobox
        for item in currentSection:
          self.indexCombo_2.addItem(str(item[0]))
          
    def loadInitial2(self):
        # gets the index of section combobox2
        index = self.sectionCombo_2.currentIndex()
        # and the index of index combobox2
        index2= self.indexCombo_2.currentIndex()
        # uses parser to list sections and items
        sections = parser.sections()
        items = parser.items(sections[index])
        # in list of items finds specified item and removes comments
        item = items[index2]
        item = str(item[1])
        item = window.clean(item,'#')
        # displays the item in the line edit
        self.initialLine2.setText(item)

    def loadInitial(self):
        # gets the index of section combobox2
        index = self.sectionCombo.currentIndex()
        # and the index of index combobox2
        index2= self.indexCombo.currentIndex()
        # uses parser to list sections and items
        sections = parser.sections()
        items = parser.items(sections[index])
        # in list of items finds specified item and removes comments
        item = items[index2]
        item = str(item[1])
        item = window.clean(item,'#')
        # displays the item in the line edit       
        self.initialLine.setText(item)
        

          
    def run(self):
        """
        called by clicking scan in scandialog. Once the user has selected all the options that they want and inputed in all the increment type information then sends all the
        variable information to runitscan
        """
        path = loadpath1
        path = re.sub('/BOUT.inp', '', loadpath1)
        restart = 'n'

        # first variable to scan, collects all the variable values from the user inputs
        key = self.sectionCombo.itemText(self.sectionCombo.currentIndex())
        subkey = self.indexCombo.itemText(self.indexCombo.currentIndex())
        initial  = self.initialLine.text()
        limit = self.finalLine.text()
        increment = self.incrementLine.text()

        # second variable to scan, collects all the variable values from the user inputs
        key2 = self.sectionCombo_2.itemText(self.sectionCombo_2.currentIndex())
        subkey2 = self.indexCombo_2.itemText(self.indexCombo_2.currentIndex())
        initial2 = self.initialLine2.text()
        limit2 = self.finalLine2.text()
        # None is used in scanboutSim.py tp determine whether one or two arguments should be used
        if limit2 == '':
            limit2 = 'NONE'
        increment2 = self.incrementLine2.text()
        if increment2 == '':
            increment2 = 'NONE'

        # change whether the inputed increment is added to the initial or is percentage change
        if self.comboBox_2.currentText() == 'Raw':
            incrementType = '+'
        else:
            incrementType = 'other'

        # change the type of scan dependent on the user input
        if self.comboBox.currentIndex() == 0:
            scanType = 'power'
        else:
            scanType = 'full'
            
        # test whether to restart
        if window.checkBox.isChecked() == True:
          restart = 'y'
        else:
          restart = 'n'

        numProc = window.procSpin.value()
        nice = window.niceSpin.value()

        # call to runitscan with all the variables that were user input 
        self.runitscan(path, key, subkey, initial, limit, increment, restart, key2, subkey2, initial2, limit2, increment2, incrementType, scanType, numProc, nice)
        self.close()

    def runitscan(self, path, key, subkey, initial, limit, increment, restart, key2, subkey2, initial2, limit2, increment2, incrementType, scanType, numProc, nice):
        """
        called  by run above.
        this function start the worker thread using the scanWorker class. All the variables are passed as arguments to scanbout.py. If scanbout doesn't recieve
        enough arguments then BOUT will fail to run. This means that if the  user doesn't input all the increment info extra an error will occur an by seen in the
        output stream
        """
        # start the worker thread with all arguments
        self.worker = scanWorker(path, key, subkey, initial, limit, increment, restart, incrementType, scanType, key2, subkey2, initial2, limit2, increment2, numProc, nice, window.outputStream)
        # move to the output stream tab
        window.tabWidget.setCurrentIndex(2)
        if not self.worker.isRunning():
                self.worker.exiting= False
                self.worker.start()
                 # this line links the output of the code to the printit function
                self.worker.dataLine1.connect(self.printit)

    def printit(self, value):
            """
            this picks up the signal from the scan worker thread as the variable value and prints it to the output stream
            """
            if value == '' and proc.poll() is not None:
                    v = 1
            else:
                    # if reaches the end of the process stop printing black space
                    window.outputStream.ensureCursorVisible()
                    # prints to the text edit
                    window.outputStream.insertPlainText(value)
                    # this means that as stuff is added to the screen the cursor follows it 
                    window.outputStream.ensureCursorVisible()

                    


                    
####################################### NEW CLASS #######################################


class defaultsave(QtGui.QMainWindow, Ui_defaultsave):

        def __init__(self, parent=None):
                """
                Initialsation routine
                """
                # These calls set up the window
                super(defaultsave, self).__init__(parent)
                self.setupUi(self)
                self.buttonBox.accepted.connect(self.save)
                self.buttonBox.rejected.connect(self.close)
                self.buttonBox.accepted.connect(self.close)
                

        def save(self):
                """
                called when ok is clicked in the default save dialog which is created when save is clicked on the graphing tab under the defaults.
                This saves to a .ini file in the defaults folder containing all the variable information
                about the spin boxes and tickboxes used to create graphs so that a user can give a name to
                default and save it for quick loading. Makes it easy to load commonly used graphs
                """
                # gets the name as input into the line edit by the user
                name = self.defaultLine.displayText()
                # collect the 4d values from the combo boxes
                x = window.xspin.value()
                y = window.yspin.value()
                z = window.zspin.value()
                t = window.tspin.value()
                # saves index of current variable
                variable = window.variableCombo.currentIndex()
                
                ## these will be True/False
                # saves whether check boxes are checked
                xall = str(window.xall.isChecked())
                yall = str(window.yall.isChecked())
                zall = str(window.zall.isChecked())
                tall = str(window.tall.isChecked())

                # creates the new .ini file in the defaults folder
                if name != "":
                        parser3 = configparser.ConfigParser()
                        # add section for title
                        parser3.add_section('heading')
                        # give it the file name as title
                        parser3.set('heading', 'title', str(name))
                        #  add section for main variable
                        parser3.add_section('main')
                        # add main variable
                        parser3.set('main', 'variable', variable)
                        # add section for all other variables
                        parser3.add_section('others')
                        # add all other variables
                        parser3.set('others', 'time', t)
                        parser3.set('others', 'x', x)
                        parser3.set('others', 'y', y)
                        parser3.set('others', 'z', z)
                        # add section for checkboxes
                        parser3.add_section('checkboxes')
                        # add checkboxes
                        parser3.set('checkboxes', 'time', tall)
                        parser3.set('checkboxes', 'x', xall)
                        parser3.set('checkboxes', 'y', yall)
                        parser3.set('checkboxes', 'z', zall)
                        # save configfile to defaults folder with file name = default name as given by the user
                        with open(currentDir+ '/Defaults/' + str(name) + '.ini', 'w') as configfile:
                                parser3.write(configfile)
                        # relist the defaults to include the new default
                        window.list_defaults()
                        # repopulate the defaults combobox
                        window.appendToCombo()

####################################### NEW CLASS #######################################

class addDefaultVar(QtGui.QMainWindow, Ui_addDefaultVar):
    """
    This class represents the main window
    which inherits from Qt's QMainWindow and from
    the class defined in mainwindow (called Ui_MainWindow)
    """
    def __init__(self, parent=None):
        """
        Initialisation routine
        """
        # These calls set up the window
        super(addDefaultVar, self).__init__(parent)
        self.setupUi(self)
        self.addToTable()
        self.addVariableButton.clicked.connect(self.getVar)
        self.variableTable.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.otherVariablesTable.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.otherVariablesTable.cellDoubleClicked.connect(self.varClicked)
        self.variableTable.cellDoubleClicked.connect(self.varDeleted)
        self.closeButton.clicked.connect(self.Close)
        
    def insertTableRow(self, *args):
        """
        Inserts a row into the table at row 0
        The inputs to this function will be inserted in order as
        columns in this new row. Need one of these functions for each table. 
        """
        # First disable sorting, so table won't rearrange itself
        self.variableTable.setSortingEnabled(False)
        
        # Insert a row at 0, i.e. the top
        self.variableTable.insertRow(0)
        
        # Loop over all arguments, inserting into rows
        for col, value in enumerate(args):
            # col is the column number, value is the value to set to
            # Note that the values should be strings
            item = QTableWidgetItem(toStr(value))
            self.variableTable.setItem(0,col, item)
            
        # Re-enable sorting
        self.variableTable.setSortingEnabled(True)
        
    def addToTable(self):

        """
        called when this class is initialised.
        adds all the defaults stored in the config file to the table of default variables 
        """
        global defaultLst
        # clears the defaults table
        self.variableTable.clearContents()
        self.variableTable.setRowCount(0)
        # collect the default variables, which will be a long string
        defaultLst =  position.get('defaultVars', 'vars')
        # get list turns the long string into an actual lst at each comma
        def getlist(option, sep=',', chars=None):
            """Return a list from a ConfigParser option. By default, 
               split on a comma and strip whitespaces."""
            return [ chunk.strip(chars) for chunk in option.split(sep) ]
        
        defaultLst = getlist(defaultLst)    
        # for each item in the list a new row is inserted into the default table 
        for item in defaultLst:
            self.insertTableRow(item)

    def varDeleted(self, x):
        """
        called when a row is double clicked in the defaults table
        """
        global defaultLst
        defaultLst = []
        # does the same as above, collects the long string and then turns it into a lists
        defaultLst =  position.get('defaultVars', 'vars')

        
        def getlist(option, sep=',', chars=None):
            """Return a list from a ConfigParser option. By default, 
               split on a comma and strip whitespaces."""
            return [ chunk.strip(chars) for chunk in option.split(sep) ]
        defaultLst = getlist(defaultLst)
        # the iten in the list is then delete
        delVar = self.variableTable.currentItem().text()
        length  = len(defaultLst)
        
        # deletes the item from the list
        for i in range(length-1):
            print i
            if defaultLst[i] == delVar:
                del defaultLst[i]
        # resets allVars
        allVars = ''
        # finds the length of defaultLst to iterate over
        length  = len(defaultLst)
        for i in range(length):
          # minus 1 because of deletion, creates a string from list
            if i < length-1:
                allVars = allVars + defaultLst[i] + ','
            else:
                allVars = allVars + defaultLst[i]
                
        singleDefaultLst = allVars
        # write to position the new defaultLst
        position.set('defaultVars', 'vars', singleDefaultLst)
        with open(config, 'w') as configfile:
            position.write(configfile)
        # call add to table to refresh the table
        self.addToTable()

         

    def varClicked(self):
        """
        called when a variable is double clicked in the top variable table, calls add to add to the default lst
        """
        variable = self.otherVariablesTable.currentItem().text()
        self.add(variable)

    def getVar(self):
        """
        called when a variable is written in the text edit and 'add variable'. it double clicked in the top variable table, calls add to add to the default lst
        """
        variable = self.addVariable.text()
        self.add(variable)


    def add(self, variable):
        """
        called by varClicked and getVar and goes through the same process as in getlist
        """     
        global defaultLst
        allVars = ''
        defaultLst.append(variable)
        length  = len(defaultLst)
        for i in range(length):
          # minus 1 because of deletion, creates a string from list
            if i < length-1:
                allVars = allVars + defaultLst[i] + ','
            else:
                allVars = allVars + defaultLst[i]
                
        singleDefaultLst = allVars
        # write to position the new defaultLst
        position.set('defaultVars', 'vars', singleDefaultLst)
        with open(config, 'w') as configfile:
            position.write(configfile)
        # call add to table to refresh the table
        self.addToTable()

    def Close(self):
        self.close()
        sleep(0.1)
        global loadpath1
        loadpath1 = re.sub('/BOUT.inp', '', loadpath1)
        window.collect(loadpath1)

####################################### NEW CLASS #######################################

class textdisplay(QtGui.QMainWindow, Ui_TextWindow):
    def __init__(self, parent=None):
        """
        Initialisation routine
        """
        # These calls set up the window
        super(textdisplay, self).__init__(parent)
        self.setupUi(self)
        
####################################### NEW CLASS #######################################

class textdisplayhistory(QtGui.QMainWindow, Ui_TextWindowHistory):
    def __init__(self, parent=None):
        """
        Initialisation routine
        """
        # These calls set up the window
        super(textdisplayhistory, self).__init__(parent)
        self.setupUi(self)
        self.pushButton_2.clicked.connect(self.loadcopied)

    def loadcopied(self):
        """
        called when the load button in the text display history window is clicked
        allows the user to copy a filepath from the history and load it into the GUI
        for editing
        """
        global loadpath1
        try:
            # sets global loadpath1 = whatever has been put into the text editer
            loadpath1 = self.lineEdit.displayText()+ '/BOUT.inp'
            # changes the headings in it to make it parser friendly
            changeHeadings(loadpath1)
            # change tabs to update controls otherwise the screen doesn't refresh, user can't see this happening
            window.tabWidget.setCurrentIndex(0)
            window.updateControls(loadpath1)
            window.tabWidget.setCurrentIndex(1)
            self.close()
            
        # if user doesn't copy the path exactly throws out an IOError, asked to check their input and try again
        except IOError:
          # show the dialog
            generalDialog.show()
            # change the displayed text
            generalDialog.label.setText(QtGui.QApplication.translate("Dialog", "Try removing whitespace and additional \n characters from path" , None, QtGui.QApplication.UnicodeUTF8))
            # change the window name
            generalDialog.setWindowTitle(QtGui.QApplication.translate("Dialogcompare", "Bad File Path", None, QtGui.QApplication.UnicodeUTF8))
            




if __name__ == "__main__":
    import sys
    
    # Create a Qt application
    app = QtGui.QApplication(sys.argv)
    
    # Create the window
    dialogSimulation = dialogSimulation()
    dialogsave = dialogsave()
    generalDialog = generalDialog()
    defaultSave = defaultsave()
    window = MainWindow()
    txt =textdisplay()
    window.list_archive('inp')
    window.show()
    txthist = textdisplayhistory()
    scan = Scandialog()
    resize = resize()
    addDefaultVar = addDefaultVar()
    # Run the application then exit    
    sys.exit(app.exec_())
    

    
