#!/usr/bin/env python
import configparser, sys, os,  difflib, subprocess, threading, signal
from datetime import *
from PySide.QtGui import *
from PySide.QtCore import *
from mainwindow import *
from dialog import *
from dialogcompare import *
from guifunctions import *
from textdisplay import *
from textdisplayhistory import *
from defaultsave import *
from scanbout import *
from time import *
from helpView import *
from resize import *
from dialogSimulation import *
from dialogArchive import *

# pyxpad
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

# GLOBAL VARIABLES
# currentDir will always have the config files in it
currentDir = os.getcwd()
config = currentDir + '/config/config.ini'

# lists to hold infomation for automatic creation of inputs
inputsLst = []
sectionLst = []
inputsTupLst = []
groupbox = []
loadpath1= 'empty'
run = 'false'
cell =False 
parser2 = configparser.ConfigParser()

# Used to load data from the config folder as inital data


###################################################################
#   APPRARANCE
 # used to get the values for the automatic creation of input buttons, they are taken from the config file


with open(config) as fp:
    position = configparser.ConfigParser()
    position.optionxform = str
    position.readfp(fp)
leftBorder = int(position.get('appearance', 'leftborder'))
verticalSeperation = int(position.get('appearance', 'verticalseperation'))
topBorder = int(position.get('appearance', 'topborder'))
maxLength = int(position.get('appearance', 'maxlength'))
boxWidth = int(position.get('appearance', 'boxwidth'))
horizontalSeperation = int(position.get('appearance', 'horizontalseperation'))
xLabel = int(position.get('appearance', 'xlabel'))
xInput = int(position.get('appearance', 'xinput'))
labelWidth = int(position.get('appearance', 'labelwidth'))
sepInput = int(position.get('appearance', 'sepinput'))
########################################################################

"""
NOTE: BOUT.inp can not be passed through config parser unless it has a heading
for all sections. A default heading has been added at the start with addTiming if ther
isn't already a heading. This has to be removed for any simulations because BOUT++
will not run with an additional heading. The removeTiming function is used later in
the program for this, in the runbout and scanbout programs. It should also be noted that
the config parser doesn't like headings with numbers in them so in non sol1d control files
the 2fluid heading will need changing. This will at some point be automated. 
"""

archive = position.get('archive', 'path')
codeFile = position.get('exe', 'path')
loadpath = currentDir + '/config/BOUT.inp'
changeHeadings(loadpath)
tups = commentsTup(loadpath)
with open(loadpath) as fp:
    parser = configparser.ConfigParser()
    parser.optionxform = str
    parser.readfp(fp)
    
parser.read(loadpath)

####################################### NEW CLASS #######################################

class Worker(QThread):
##    """ 
##    This thread runs the simulations in the backgrounds so preventing the GUI from freezing while running
##    STDOUT is redirected to a signal which is collected by the text editor of the output stream
##        """

      dataLine1 = Signal(str)
      def __init__(self, path, restart, numProc, nice, outputStream,  parent = None):
              QThread.__init__(self, parent)
              self.path = path + '/'
              self.loadpath = path
              self.restart = restart
              self.outputStream = outputStream
              self.numProc = numProc
              self.exiting = False
              self.nice = nice
              window.tabWidget.setTabEnabled(2, True)
              # reattaches comments that would have been lost because of the config parser, tups is the list of tuples that they are saved within
              global tups
              addComments(self.path + 'BOUT.inp', tups)
                  


      def run(self):
          # proc runs the simulation
          global proc
          proc = subprocess.Popen([currentDir + '/runboutSim.py', str(self.path), str(self.restart), str(self.numProc), str(self.nice)],
                                  shell = False, stdout = subprocess.PIPE, stderr = subprocess.PIPE, preexec_fn=os.setsid)
            
          running = True
          while running == True:
              output = proc.stdout.readline()
              if output == '' and proc.poll() is not None:  # at the end of proc stops reading empty ines to allow the program to close
                       v =1
                       window.tabWidget.setTabEnabled(3, True)
                       window.tabWidget.setCurrentIndex(3)
                       proc.wait()
                       running = False
                       global loadpath1
                       loadpath1 = self.loadpath
              else:
                  self.dataLine1.emit(output) # lines of output are emited here


                  
####################################### NEW CLASS #######################################

class scanWorker(QThread):
##                """ 
##                This thread runs the simulations in the backgrounds so preventing the GUI from freezing while running
##                STDOUT is redirected to a signal which is collected by the text editor of the output stream
##                """

      dataLine1 = Signal(str)
      def __init__(self, path, key, subkey, initial, limit, increment, restart, incrementType, scanType, key2, subkey2, initial2, limit2, increment2, numProc, nice, outputStream, parent = None):
              QThread.__init__(self, parent)
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
              self.exiting = False
              self.numProc = numProc
              self.nice = nice
              window.tabWidget.setTabEnabled(2, True)


      def run(self):
          # proc runs the simulation
          global proc
          proc = subprocess.Popen([currentDir + '/scanboutSim.py', str(self.path), str(self.key), str(self.subkey), str(self.initial), str(self.limit), str(self.increment), str(self.restart), str(self.incrementType), str(self.scanType), str(self.numProc), str(self.nice), str(self.initial2), str(self.limit2), str(self.key2),str(self.subkey2),str(self.increment2)],
                                   shell = False, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
          global pid
          pid = proc.pid
          running = True
          while running == True:
              output = proc.stdout.readline()
              if output == '' and proc.poll() is not None:  # at the end of proc stops reading empty lines to allow the program to close
                       window.list_archive('inp')
                       window.tabWidget.setTabEnabled(3, True)
                       window.tabWidget.setCurrentIndex(3)
                       proc.wait()
                       running = False
                       global loadpath1
                       loadpath1 = self.path
              else:
                  self.dataLine1.emit(output) # lines of output are emited here 
                  


####################################### NEW CLASS #######################################

class Worker2(QThread):
    """
      This thread probably is no longer necessary and the task could be managed in the main thread,
      was put in place initially because GUI was freezing when loading graphs however they are now loaded
      within the GUI itself so this may no longer be a problem
    """

    def __init__(self, parent = None):
        QThread.__init__(self, parent)

    def run(self):
        self.creategraph()
              
    def creategraph(self):
        """
        sets the variables according to what has been user input, the multiple if
        statements are due to the variable needing to be input 
        """
        x = (window.xspin.text())
        y = (window.yspin.text())
        z = (window.zspin.text())
        t = (window.tspin.text())
        if window.variableCombo.currentIndex() == 0:
            variable = ne
            self.plotdata(variable, t, x, y, z)
        if window.variableCombo.currentIndex() == 1:
            variable = nvi
            self.plotdata(variable, t, x, y, z)
        if window.variableCombo.currentIndex() == 2:
            variable = p
            self.plotdata(variable, t, x, y, z)
        if window.variableCombo.currentIndex() == 3:
            variable = nn
            self.plotdata(variable, t, x, y, z)
        if window.variableCombo.currentIndex() == 4:
            variable = nvn
            self.plotdata(variable, t, x, y, z)
        if window.variableCombo.currentIndex() == 5:
            variable = pn
            self.plotdata(variable, t, x, y, z)
        if window.variableCombo.currentIndex() == 6:
            variable = temp
            self.plotdata(variable, t, x, y, z)
            
    def plotdata(self, variable, t, x, y, z):
        """
        Takes into account all of the possiblilties when it comes to spanning all variables
        - this may seem overcomplicated BUT cannot input colon as a string into plotdata so
        this is the only way!
        """
        from boututils import plotdata
        if window.tall.isChecked() == True:
            if window.xall.isChecked() == True:
                window.DataPlot.plotdata(variable[:,:,int(y),int(z)])
            if window.yall.isChecked() == True:
                window.DataPlot.plotdata(variable[:,int(x),:,int(z)])
            if window.zall.isChecked() == True:
                window.DataPlot.plotdata(variable[:,int(x),int(y),:])
            if window.xall.isChecked() == False and window.yall.isChecked() == False and window.zall.isChecked()== False:
                window.DataPlot.plotdata(variable[:,int(x),int(y),int(z)], title=None, xtitle=None, ytitle=None)
                
        if window.xall.isChecked() == True:
            if window.yall.isChecked() == True:
                window.DataPlot.plotdata(variable[int(t),:,:,int(z)])
            if window.zall.isChecked() == True:
                window.DataPlot.plotdata(variable[int(t),:,int(y),:])
            if window.tall.isChecked() == False and window.yall.isChecked() == False and window.zall.isChecked()== False:
                window.DataPlot.plotdata(variable[int(t),:,int(y),int(z)])
                
        if window.yall.isChecked() == True:

            if window.zall.isChecked() == True:
                window.DataPlot.plotdata(variable[int(t),int(x),:,:])
            if window.xall.isChecked() == False and window.tall.isChecked() == False and window.zall.isChecked()== False:
                window.DataPlot.plotdata(variable[int(t),int(x),:,int(z)])

        if window.zall.isChecked() == True:

            if window.xall.isChecked() == False and window.yall.isChecked() == False and window.tall.isChecked()== False:
                window.DataPlot.plotdata(variable[int(t),int(x),int(y),:])

####################################### NEW CLASS #######################################

class WorkerCollect(QThread):
    """
      This thread probably is no longer necessary and the task could be managed in the main thread,
      was put in place initially because GUI was freezing when loading graphs however they are now loaded
      within the GUI itself so this may no longer be a problem
    """

    def __init__(self, path,  parent = None):
        QThread.__init__(self, parent)
        self.path = path
        
    def run(self):
            """
            Runs the collect routine. Currently the python pyxpad part has to collect seperatly to the GUI features which is
            why all the imports have to happen twice. This is slow so have a thread - also adds stability. Sleep functions
            mean prevents all commands from being executed simulateously which crahses the system. 
            """
            window.textOutput.ensureCursorVisible()
            window.dataTable.clearContents()
            window.dataTable.setRowCount(0)
            window.data = {}  # resets the data stored in pyxpad as multiple collects would cause a crash otherwise.
            os.chdir(self.path)
            window.commandEntered('from boutdata import collect')
            sleep(0.1)    # stops simulataneous commands
            window.commandEntered('from boututils import plotdata')
            sleep(0.1)
            window.commandEntered('global p, ne, nvi, nn, nvn, pn, finalpath')
            window.commandEntered('p = collect("P")')
            sleep(0.1)
            window.commandEntered('ne = collect("Ne")')
            sleep(0.1)
            window.commandEntered('nvi = collect("Nvi")')
            sleep(0.1)
            window.commandEntered('nn = collect("Nn")')
            sleep(0.1)
            window.commandEntered('temp = 0.5*p/ne')
            sleep(0.1)
            window.commandEntered('nvn = collect("NVn")')
            sleep(0.1)
            window.commandEntered('pn = collect("Pn")')
            sleep(0.1)
            from boutdata import collect
            global p, ne, nvi, nn, nvn, pn, temp
            p = collect("P"); ne = collect("Ne"); nvi = collect("Nvi"); nn = collect("Nn"); temp = 0.5*p/ne
            nvn = collect("NVn"); pn = collect("Pn")
            window.collectedLabel.setText(str(self.path))
            self.exit()

####################################### NEW CLASS #######################################

class dialogcompare(QtGui.QMainWindow, Ui_Dialogcompare):
    def __init__(self, parent=None):
        """
        Initialisation routine
        """
        # These calls set up the window
        super(dialogcompare, self).__init__(parent)
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
        # These calls set up the window
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)

        """
        initialise all the console and graphing bits as used in some of Ben's bits.
        """
        global archive, config, codeFile
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

        # set the path indicator labels for archive and simulation code
        if os.path.isdir(archive):
            self.archivePath.setText(archive)
        if os.path.isfile(codeFile):
            self.simulationFile.setText(codeFile)
        
        ###################################################
        # allows the user to change the file path of the simlation code
        self.actionSimulation_Code.triggered.connect(dialog.loadSimCode)

        ###################################################
        # bring up the help text viewer
        self.actionHelp.triggered.connect(helpView.openHelp)

        ###################################################
        # bring up the help text viewer
        self.actionArchive.triggered.connect(self.archiveLoad)
                
        ###################################################
        # bring up the resize and reposition window
        self.actionPositioning.triggered.connect(self.showResize)
        
        ###################################################
        # exit the program
        self.actionExit.triggered.connect(self.close)

        ###################################################
        # compare
        self.actionCompare.triggered.connect(self.compareClicked)

        ###################################################
        # interupt simulation     
        self.stopSimulation.clicked.connect(self.STOP)
        self.actionStop_Simulation.triggered.connect(self.STOP)
        
        ###################################################
        # load file history
        self.actionFileHistory.triggered.connect(self.FileHistoryClicked)

        ###################################################
        # run simulation
        self.pushButton_3.clicked.connect(self.changerun)

        ####################################################
        # (file selection) Button            
        self.pushButton.clicked.connect(self.buttonAction)
        self.tableWidget.cellPressed.connect(self.cellAction)

        ####################################################
        # (file creation) Button 2
        self.pushButton_2.clicked.connect(self.showDialog)
        
        ####################################################
        # file selection) Double Click
        self.tableWidget.cellDoubleClicked.connect(self.loadinp)

        ###################################################
        # create a graph       
        self.createGraph.clicked.connect(self.rungraph)

        ###################################################
        # collect data
        self.pushButton_7.clicked.connect(self.collectit)
        
        ###################################################
        # get value
        self.valueButton.clicked.connect(self.value)

        ###################################################
        # divide 
        self.divideByButton.clicked.connect(self.divide)

        ###################################################
        # runScan
        self.runScanningSimulation.clicked.connect(self.changeScan)

        ###################################################
        # default load setttings for selected default graphs
        self.list_defaults()
        self.appendToCombo()
        self.defaultCombo.currentIndexChanged.connect(self.loadDefault)
        self.saveDefaultButton.clicked.connect(self.saveDefault)
    
        ###################################################
        # initialise the inputs creation (automatic)
        self.readConfig()
        self.rearrange()

        ###################################################
        # create an example folder in the archive folder
        self.actionCreate_Example.triggered.connect(self.createInitial)
        
        ###################################################
        # if restart is checked locks in number of processor to use
        self.checkBox.stateChanged.connect(self.disableProc)

        ###################################################
        # set niceness default
        self.niceSpin.setValue(10)

    def disableProc(self):
        """
        Don't want to be able to chose a different number of processors if restarting than was already used as this causes a crash
        so disables the combobox and resets to original value
        """
        if self.checkBox.isChecked() == True:
            global procNumber
            # disables combo and sets to original value
            try:
                self.procSpin.setValue(procNumber)
            except NameError:
                pass
            self.procSpin.setEnabled(False)
        else:
            self.procSpin.setEnabled(True)

        # the if not statement looks to see if the current archive is a folder and prompts the user to select one if not on initialisation
            
    def createInitial(self):
##        """"
##        This isn't the most useful feature. Adds an example folder in any archive is selected containing all the useful files
##        """"
        lst = os.listdir(archive)
        newlst = []
        for folder in lst:
            path = os.path.join(archive + '/' + folder)
            if os.path.isdir(path):
                newlst.append(folder)
        if not os.path.isdir(archive + '/example'):
            os.makedirs(archive + '/example')
        if len(newlst) == 0:
            shutil.copy(currentDir + '/example/BOUT.inp' , archive + '/example/BOUT.inp')
            shutil.copy(currentDir + '/example/record.ini' , archive + '/example/record.ini')
            shutil.copy(currentDir + '/example/usernotes.ini' , archive + '/example/usernotes.ini')
        self.tabWidget.setCurrentIndex(1)
        self.list_archive('.inp')
        self.tabWidget.setCurrentIndex(0)
        

    def archiveLoad(self):
        """
        This function calls a file viewer/ explorer window for the user to chose or create their archive folder
        """
        global archive
        archive = QtGui.QFileDialog.getExistingDirectory(self, "Choose or Create Archive",
                QtCore.QDir.currentPath())
        position.set('archive', 'path', str(archive))

        with open (config, 'w') as configfile:
            position.write(configfile)
        self.clearTable()
        self.tabWidget.setCurrentIndex(1)
        self.list_archive('.inp')
        self.tabWidget.setCurrentIndex(0)
        if os.path.isdir(archive):
            self.archivePath.setText(archive)
        
        

    def showResize(self):
        resize.show()

##################################################################################################################
####################################### AUTOMATIC CREATION OF INPUTS STARTS ######################################
    def updateControls(self, inpfile):
        global inputsLst, sectionLst, inputsTupLst, groupbox, parser, tups
        
        #self.delete()
        inputsLst = []
        sectionLst = []
        inputsTupLst = []
        groupbox = []
        
        folder = re.sub('/BOUT.inp', '', inpfile)
        text = open(folder + '/usernotes.ini').read()
        self.plainTextEdit.setPlainText(text)
        tups = commentsTup(inpfile)
        with open(inpfile) as fp:
            parser = configparser.ConfigParser()
            changeHeadings(inpfile)
            
            parser.optionxform = str
            parser.readfp(fp)
        
        self.fileLabel.setText(QtGui.QApplication.translate("MainWindow", str(inpfile), None, QtGui.QApplication.UnicodeUTF8))
        self.readConfig()
        self.rearrange()
        
        
    def readConfig(self):
        """
        Reads the contents of the selected config file. For each section it creates a new frame to insert controls.
        It then finds all the items within that section and test the data type of that value, inserting either a combobox,
        double combobox or line edit depending.
        """
        global n, m, sections
 
        sections = parser.sections()
        
        for section in sections:
            
            items = parser.items(section)
            y =len(items) 
            self.createGroupBox(section, y)
            n = 1   
            for i in range(len(items)):
                subkey = items[i][0]
                value = self.clean(items[i][1], '#')    # removes comments
                try:
                    int(value)                  
                    self.createBox(n , subkey, value, section)
                except ValueError:
                    try:
                        float(value)
                        if float(value) > 1000000:
                            self.createLine(n , subkey, value,section)
                        else:
                            self.createDoubleSpin(n , subkey, value, section)
                    except ValueError:
                        if value == 'true' or value == 'false':
                            self.createTorF(n , subkey, value, section)
                        else:
                            self.createLine(n , subkey, value, section)
                n = n + 1   # the n count is used so that each succesivly created input is created a factor n pixels lower than the previous


    def rearrange(self):
        global leftBorder, topBorder, verticalSeperation, maxLength, boxWidth, horizontalSeperation
        """
        The groupbox list contains the names of all the group boxes and the length of the inputs in that section, stored as a list of tuples,
        it then works out the best arrangement for these by finding frames of sizes that add together to a defined limit,
        this will be eventually a user input. The frames are then moved around the screen in their groups that add nicely
        so that they are distributed evenly and made a length comparable to the inputs within them. 
        """
        groupbox2 = groupbox
        n = 0
        while len(groupbox2) > 0:
            k = 0
            newLst = [] # newLst is cleared each time a group of suitable length is found 
            newLst.append(groupbox2[0])
            del groupbox2[0]
            total = self.total(newLst)
            for i in range(len(groupbox2)):
                if total + int(groupbox2[i-k][1]) < maxLength:
                    newLst.append(groupbox2[i-k])
                    total = self.total(newLst)
                    del groupbox2[i-k]
                    k = k + 1   #this k makes up for a deleted value
            length = 0
            m = 0
            for obj in newLst:      # for the group of good length they are sorted
                mycode = 'self.' + obj[0] + '.setGeometry(QtCore.QRect(leftBorder + horizontalSeperation*n, length + verticalSeperation*m + topBorder, boxWidth, obj[1]))'     
                exec mycode
                length = length + int(obj[1])   # length means length of previous frame, so current frame is positioned after it
                m = m+1
            n = n +1

            
    def total(self, Lst):
        """
        is just used to find the total of the current newLst
        """
        total = 0
        for x in range(len(Lst)):
            total = total + int(Lst[x][1])
        return total

    """""""""""""""""""""""
    The exec parts of the code in the create functions are used because I couldn't find a way of using a variable within a line such as self.objectName.setText (etc)
    and so all inputs called objectName which won't work for updating the control file. Object name takes the form of subkey value + section name. This is to make sure
    that when two objects of the same name in different sections are created they are unique and so can have their own behaviour. 
    """""""""""""""""""""""
    def delete(self):
        for item in inputsLst:
          mycode = 'self.' + item + '.deleteLater()'
          exec mycode
          fg = 3

        for section in sections:
          objectName = section
          mycode = 'self.' + objectName + '.deleteLater()'
          exec mycode

    def createGroupBox(self, section, y):
        """
        creates a new frame for each section. 
        """
        global sepInput
        objectName = section
        sectionLst.append(sectionLst)
        ylength = 28 + y *sepInput    # finds the length of all the input controls in this section
        mycode = 'self.' + objectName + ' = QtGui.QGroupBox(self.tab_2)'
        exec mycode
        mycode = 'self.' + objectName + '.setGeometry(QtCore.QRect(10, 10, 210, ylength))'  # rearrange function called later, these values are just placeholders
        exec mycode
        mycode = 'self.' + objectName + ' .setTitle(QtGui.QApplication.translate("MainWindow", section, None, QtGui.QApplication.UnicodeUTF8))'
        exec mycode
        tup = (section, ylength)    #this list of tuples is used later to reorganise position
        groupbox.append(tup)
        
      

    def createDoubleSpin(self, n, subkey, value, section):
        """
        creates a new double spin for each input item that is a float. 
        """
        global xLabel, xInput, labelWidth, sepInput
        objectName = subkey + 'Double' + section
        inputsLst.append(objectName)
        tup = (section, objectName)
        inputsTupLst.append(tup)
        mycode = 'self.' + objectName + ' = QtGui.QDoubleSpinBox(self.' + section +')'
        exec mycode
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
        mycode =  'self.' + objectName + '.setGeometry(QtCore.QRect(xInput, sepInput*n, 100, 22))'
        exec mycode
        mycode = 'self.label = QtGui.QLabel(self.' +section + ')'
        exec mycode

        # adds an automatic tooltip based on the comments in the control file
        for i in range(len(tups)):
            line = tups[i][0].split()[0]
            if line == subkey:
                tooltip = right(str(tups[i][1]), '#')
                if tooltip != 'None':
                  mycode = 'self.' +objectName + '.setToolTip(tooltip)'
                  exec mycode     
        #labels
        self.label.setGeometry(QtCore.QRect(xLabel, sepInput*n, labelWidth, 15))
        self.label.setObjectName("label_n")
        self.label.setText(QtGui.QApplication.translate("MainWindow", subkey, None, QtGui.QApplication.UnicodeUTF8))


    def createTorF(self, n, subkey, value, section):
        """
        creates a new double spin for each input item that is a float. 
        """
        global xLabel, xInput, labelWidth, sepInput
        objectName = subkey + 'TorF' + section
        inputsLst.append(objectName)
        tup = (section, objectName)
        inputsTupLst.append(tup)
        mycode = 'self.' + objectName + ' = QtGui.QComboBox(self.' + section +')'
        exec mycode
        mycode = 'self.' + objectName + '.addItem("true")'
        exec mycode
        mycode = 'self.' + objectName + '.addItem("false")'
        exec mycode
        mycode = 'self.' + objectName + '.setObjectName(objectName)'
        exec mycode
        mycode =  'self.' + objectName + '.setGeometry(QtCore.QRect(xInput, sepInput*n, 100, 22))'
        exec mycode
        mycode = 'self.label = QtGui.QLabel(self.' +section + ')'
        exec mycode
        if value == 'true':
            mycode = 'self.' + objectName + '.setCurrentIndex(0)'
            exec mycode
        else:
            mycode = 'self.' + objectName + '.setCurrentIndex(1)'
            exec mycode
            
        # adds an automatic tooltip based on the comments in the control file
        for i in range(len(tups)):
            line = tups[i][0].split()[0]
            if line == subkey:
                tooltip = right(str(tups[i][1]), '#')
                if tooltip != 'None':
                  mycode = 'self.' +objectName + '.setToolTip(tooltip)'
                  exec mycode            
        #labels
        self.label.setGeometry(QtCore.QRect(xLabel, sepInput*n, labelWidth, 15))
        self.label.setObjectName("label_n")
        self.label.setText(QtGui.QApplication.translate("MainWindow", subkey, None, QtGui.QApplication.UnicodeUTF8))
            
    def createBox(self, n, subkey, value, section):
        """
        creates a new spin box for each input item that is an integer. 
        """
        global xLabel, xInput, labelWidth, sepInput
        objectName = subkey + 'Spin' + section
        inputsLst.append(objectName)
        tup = (section, objectName)
        inputsTupLst.append(tup)
        mycode = 'self.' + objectName + ' = QtGui.QSpinBox(self.' +section + ')'
        exec mycode
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
        mycode =  'self.' + objectName + '.setGeometry(QtCore.QRect(xInput, sepInput*n, 100, 22))'
        exec mycode
        mycode = 'self.label = QtGui.QLabel(self.' +section + ')'
        exec mycode
        
        # adds an automatic tooltip based on the comments in the control file
        for i in range(len(tups)):
            line = tups[i][0].split()[0]
            if line == subkey:
                tooltip = right(str(tups[i][1]), '#')
                if tooltip != 'None':
                  mycode = 'self.' +objectName + '.setToolTip(tooltip)'
                  exec mycode     
        # labels
        self.label.setGeometry(QtCore.QRect(xLabel, sepInput*n, labelWidth, 15))
        self.label.setObjectName("label_n")
        self.label.setText(QtGui.QApplication.translate("MainWindow", subkey, None, QtGui.QApplication.UnicodeUTF8))
        

        
    def createLine(self, n, subkey, value, section):
        """
        creates a new line for each input item that is text. 
        """
        global xLabel, xInput, labelWidth, sepInput
        objectName = subkey + 'Line' + section
        inputsLst.append(objectName)
        tup = (section, objectName)
        inputsTupLst.append(tup)
        mycode = 'self.' + objectName + ' = QtGui.QLineEdit(self.' + section + ')'
        exec mycode   
        mycode =  'self.' + objectName + '.setGeometry(QtCore.QRect(xInput, sepInput*n, 100, 22))'
        exec mycode        
        mycode = 'self.' + objectName + '.setObjectName(objectName)'
        exec mycode        
        mycode = 'self.' + objectName + '.setText( str(value))'
        exec mycode
        mycode = 'self.label = QtGui.QLabel(self.' +section + ')'
        exec mycode
        
        # adds an automatic tooltip based on the comments in the control file
        for i in range(len(tups)):
            line = tups[i][0].split()[0]
            if line == subkey:
                tooltip = right(str(tups[i][1]), '#')
                if tooltip != 'None':
                  mycode = 'self.' +objectName + '.setToolTip(tooltip)'
                  exec mycode                     
        # labels
        self.label.setGeometry(QtCore.QRect(xLabel, sepInput*n, labelWidth, 15))
        self.label.setObjectName("label_n")
        self.label.setText(QtGui.QApplication.translate("MainWindow", subkey, None, QtGui.QApplication.UnicodeUTF8))

    def saveSettings(self, path):

        """
        the for loops in this function go through the whole lit of inputs and removes either 'line', 'double' or 'spin'.
        in comparing to the original inputLst values this allows function to know what sort of data input it is. i.e a line input
        or a spin box of some sort. The change function is then used to update the config file with new values. 
        """
        
        for item in inputsTupLst:
            stripitem = re.sub('Line', '', item[1])
            if stripitem != item[1]:
                stripitem = re.sub(item[0], '', stripitem)
                mycode = 'self.change(item[0], stripitem, self.' + item[1] + '.text())'
                exec mycode
                
                
        for item in inputsTupLst:
            stripitem = re.sub('Double', '', item[1])
            if stripitem != item[1]:
                stripitem = re.sub(item[0], '', stripitem)
                mycode = 'self.change(item[0], stripitem, self.' + item[1] + '.value())'
                exec mycode
                
        for item in inputsTupLst:
            stripitem = re.sub('Spin', '', item[1])
            if stripitem != item[1]:
                stripitem = re.sub(item[0], '', stripitem)
                mycode = 'self.change(item[0], stripitem, self.' + item[1] + '.value())'
                exec mycode
         
        with open (path, 'w') as configfile:
            parser.write(configfile)

####################################### AUTOMATIC CREATION OF INPUTS ENDS ########################################           
##################################################################################################################

    def STOP(self):
        global proc
        try:
            os.killpg(proc.pid, signal.SIGINT)
        except OSError:
            proc.terminate()
      
      
    def changerun(self):
        """
        creates a global variable run that changes the save dialog boxes function so
        that clicking on run causes simualtion not just saving
        """
        if not os.path.isfile(codeFile):
            dialog.simulationCode()
        dialog.label.setText(QtGui.QApplication.translate("Dialog", "Save path for control file and comments file:" , None, QtGui.QApplication.UnicodeUTF8))
        global run
        run = 'true'
        self.showDialog()

    def changeScan(self):
        """
        creates a global variable run that changes the save dialog boxes function so
        that clicking on run causes simualtion not just saving
        """
        if not os.path.isfile(codeFile):
            dialog.simulationCode()
        dialog.label.setText(QtGui.QApplication.translate("Dialog", "General Save Path for Mulitple Runs:" , None, QtGui.QApplication.UnicodeUTF8))
        global run
        run = 'scan'
        self.showDialog()

        
           
##################################################################################################################
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
        # Evaluate the command, catching any exceptions
        # Local scope is set to self.data to allow access to user data
        self.runSandboxed(self._runExec, args=(cmd, glob, self.data))
        self.updateDataTable()
        
############################################## COMMAND LINE CODE ENDS ############################################
##################################################################################################################

    def collectit(self):
      """
      Triggered by clicking on the collect button. Checks to see is anything has been loaded, and if not shows a dialog, if so then runs the collect function
      """
      if loadpath1 == 'empty':
        generalDialog.label.setText(QtGui.QApplication.translate("Dialog", "Please load file to collect from" , None, QtGui.QApplication.UnicodeUTF8))
        generalDialog.show()
      else:
            newpath = re.sub('/BOUT.inp', '', loadpath1)
            self.collect(newpath)

    def collect(self, path):
     #starts a thread to run the collect routines, stops the gui from sticking
        self.workercollect = WorkerCollect(path)
        if self.workercollect.isRunning():
                self.workercollect.quit()
        if not self.workercollect.isRunning():
            self.workercollect.exiting= False
            self.workercollect.start()

            
    def FileHistoryClicked(self):
        """
        loads the record.ini file into a new window if a control file has been loaded to show that files history
        """
        if loadpath1 == 'empty':
            generalDialog.show()
            generalDialog.label.setText(QtGui.QApplication.translate("Dialog", "Please load initial file first" , None, QtGui.QApplication.UnicodeUTF8))
        else:
            newpath = re.sub('/BOUT.inp', '', loadpath1)
            newpath = newpath + '/record.ini'
            f = open(newpath, 'r')
            data = f.read()
            f.close
            txthist.textBrowser.clear()
            txthist.textBrowser.setPlainText(data)      #if PlainText not used then get strange formatting
            txthist.show()

    def TorF(self, section, index):
        """
        this function is used so that the correct value in the true or false combos is loaded
        and sets the index of the box accordingly
        """
        
        if str(self.clean(parser.get(section,index),'#')) == 'true':
            return 0
        else:
            return 1
        
    def clean(self,line, sep):
        """
        used because of compatibitilty issues with old and new config parser,
        old config parser kept returning comments when using parser.get, this removes
        anything after sep term
        """
        for s in sep:
            line = line.split(s)[0]
        return line.strip()
    

    def change(self, section, index, value):
        parser.set(section, index, value)

    def loadinp(self,x):
        """
        This will be called if the button is clicked and a file is selected or
        if a file is double clicked
        """
        self.sortdir()      #sorts the directory into onscreen order before loading
        try:
            window.delete()
        except RuntimeError:
            pass
                      
        global loadpath1, loadpath2
        try:
            global procNumber
            procNumber = int(self.tableWidget.item(x,3).text())
        except ValueError:
            procNumber = 5
        
        loadpath = str(archive) + str(directory[x])
        changeHeadings(loadpath)

        # generally loading will proceed to load from the parser and update the controls
        if 'loadpath2' not in globals():
            loadpath1 = loadpath
            self.procSpin.setValue(procNumber)
            parser.read(str(loadpath))
            self.updateControls(loadpath)
            self.tabWidget.setTabEnabled(1, True)
            self.tabWidget.setCurrentIndex(1)

        # if compare is selected and so loadpath2 declared then only loadpath2 will be changed on file selection
        else:
            loadpath2 = loadpath
            self.comparefiles(loadpath1, loadpath2)
            self.pushButton.setText(QtGui.QApplication.translate("MainWindow", "Load", None, QtGui.QApplication.UnicodeUTF8))
            self.tabWidget.setCurrentIndex(2)
            del loadpath2



    def compareClicked(self):
        """
        This function will be called when the button compare is clicked, it changes the load table to compare mode while a second file is chosen
        this creates the loadpath2 global variable open which loadinp is dependent in its if/ else statement and loadpath1 and loadpath2 can be
        fed into the compare function, after this reverts the table back to load mode
        """
        if loadpath1 == 'empty':
            generalDialog.show()
            generalDialog.label.setText(QtGui.QApplication.translate("Dialog", "Please load initial file before comparison" +'\n' + "can be made", None, QtGui.QApplication.UnicodeUTF8))

        else:  
            generalDialog.show()  #creates dialog box and switches the gui to compare mode
            self.tabWidget.setCurrentIndex(0)
            generalDialog.label.setText(QtGui.QApplication.translate("Dialog", "Choose a file to compare with", None, QtGui.QApplication.UnicodeUTF8))
            self.pushButton.setText(QtGui.QApplication.translate("MainWindow", "Compare", None, QtGui.QApplication.UnicodeUTF8))
            global loadpath2        # creation of loadpath 2, causes loadinp to follow compare routines not load 
            loadpath2 = 'x'

    def cellAction(self,x):
        """
        This function will be called if the button is clicked
        """
        # creates global cell which stores the current selected cell
        global cell
        cell = x


        
    def buttonAction(self):
        """ this function changes the use of the button depending on variable button

            if button = load and a cell has been selected on
            click, if so it will load the selected file
            if
            = compare then will load compare routines
        """
        if cell != False:
            self.loadinp(cell)
 
    def clearTable(self):
        """
        Clears the table contents
        """ 
        self.tableWidget.clearContents()
        self.tableWidget.setRowCount(0)
        
        
    def insertTableRow(self, *args):
        """
        Inserts a row into the table at row 0
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
        given a files type then this is a versatile function which creates a list of files stored in a list. This list then is
        used to create directory which contains date created, date modified, shortened file path aswell as the comment data
        for that file if any
        """

        #loads all the files from the archive
        oldpath = ''
        window.tableWidget.clearContents()
        window.tableWidget.setRowCount(0)
        if os.path.isdir(archive):
              lst = os.listdir(archive)
              list.sort(lst)
              #directory is a global variable used in many functions
              global directory
              directory = []
              subdirectory = []
              
              #look in each folder
              for folder in lst:
                  path = os.path.join(archive, str(folder))
                  # if finds files of correct type finds there attributes
                  if os.path.isdir(path):
                      sublst = os.listdir(path)
                      for file in sublst:
                          filepath = os.path.join(path, file)
                          if os.path.isfile(filepath) and filepath.endswith('.nc'):
                              subdirectory.append(filepath)
                  procNumber = len(subdirectory)/2
                  if procNumber == 0:
                      procNumber = 'No restart files'
                  
                  if os.path.isdir(path):
                    for file in os.listdir(path):
                        allpaths = path + '/' + file

                        # checks to see if the folder has a usernotes or record file and if not copies them from the main config folder
                        checknotes = path + '/usernotes.ini'
                        checkhistory = path + '/record.ini'
                        try:
                            if not os.path.isfile(checknotes):
                                shutil.copy(currentDir+'/config/usernotes.ini', checknotes)
                            if not os.path.isfile(checkhistory):
                                shutil.copy(currentDir+'/config/record.ini', checkhistory)
                        except IOError:
                            pass
                          
                        if os.path.isdir(allpaths):
                          for files in os.listdir(allpaths):
                            allfilepaths = allpaths + '/' + files
                            if allfilepaths.endswith(filetype):
                                Time1 = os.path.getctime(allfilepaths)
                                Time2 = os.path.getmtime(allfilepaths)
                                global a
                                a = datetime.fromtimestamp(Time1).strftime("%d %b %Y  %H:%M:%S")
                                global b
                                b = datetime.fromtimestamp(Time2).strftime("%d %b %Y  %H:%M:%S")
                                # adds comments to the directory
                                notespath =  allpaths + '/usernotes.ini'
                                if os.path.isfile(notespath):
                                    f= open(notespath, 'r')
                                    filedata = f.read()
                                    f.close
                                    directory.append(('/' + folder + '/' + file + '/' + files,a,b, filedata, procNumber))
                                    # lists the found files attributes from directory in table in the GUI                               
                                    
                        if file.endswith(filetype):
                            Time1 = os.path.getctime(path)
                            Time2 = os.path.getmtime(path)
                            #global a
                            a = datetime.fromtimestamp(Time1).strftime("%d %b %Y  %H:%M:%S")
                            #global b
                            b = datetime.fromtimestamp(Time2).strftime("%d %b %Y  %H:%M:%S")
                            # adds comments to the directory
                            notespath =  path + '/usernotes.ini'

                                
                            if os.path.isfile(notespath):
                                f= open(notespath, 'r')
                                filedata = f.read()
                                f.close
                                directory.append(('/'+str(folder)+'/'+str(file),a,b, filedata, procNumber))
                                                        

                  
                  subdirectory = []
                                
                                # lists the found files attributes from directory in table in the GUI 
              for i in range(len(directory)):
                  filenumber = str(i+1)
                  pathname = str(directory[i][0])
                  self.insertTableRow(pathname, directory[i][1], directory[i][2], directory[i][4], directory[i][3])

    def sortdir(self):
        """
        This function will sort the directory list so that it has the same order as those in the table
        when the table is resorted, i.e. by clicking on one of the headers to sort by file/ path...
        """
        
        global directory
        length = len(directory)
        directory = []
        # rebuilds the directory by cycling through the values of the cells in the y = 1 column
        for i in range(length):
            items = self.tableWidget.item(i,0)
            directory.append(str(items.text()))
        return directory

    def showDialog(self):
        """
        Brings up a dialog box in which the save file is chosen for the control file
        """
        dialog.updatepath()
        dialog.show()

       # Compare two data files and prints the differences between the two

    def comparefiles(self, loadpath1, loadpath2):
        self.tabWidget.setTabEnabled(2, True)
        with open(loadpath1, 'r') as sf1, open(loadpath2, 'r') as sf2:
            lineA = sf1.readlines()
            lineB = sf2.readlines()
        d = difflib.Differ()
        diff = d.compare(lineA, lineB)
        a =  '\n'.join(self.clean(str(x[0:]),'#') for x in diff if x.startswith('- '))           
        d = difflib.Differ()
        diff = d.compare(lineA, lineB)
        b = '\n'.join(self.clean(str(x[0:]), '#') for x in diff if x.startswith('+ '))

        # saves to the text edit tab
        txt.textBrowser.clear()
        txt.textBrowser.insertPlainText('\n' + 'Differences between files' + '\n')
        txt.textBrowser.insertPlainText('\n' + 'Content of File 1' + '\n' + str(loadpath1) + '\n'+ str(a) )
        txt.textBrowser.insertPlainText('\n' + '\n' + 'Content of File 2'+ '\n' + str(loadpath2) + '\n' + '\n' + str(b))
        txt.show()
        self.tabWidget.setCurrentIndex(1)

##################################################################################################################
############################################## GRAPHING TAB CODE STARTS ##########################################
        
    def rungraph(self):
        """
        Starts the worker2 thread which creates graph, prevents the gui from freezing up when the graph is created
        """
        self.worker2 = Worker2()
        if self.worker2.isRunning():
                self.worker2.quit()
        if not self.worker2.isRunning():
            self.worker2.exiting= False
            self.worker2.start()

    def variable(self):     
        if self.variableCombo.currentIndex() == 0:
            variable = ne

        if self.variableCombo.currentIndex() == 1:
            variable = nvi
            
        if self.variableCombo.currentIndex() == 2:
            variable = p
            
        if self.variableCombo.currentIndex() == 3:
            variable = nn
            
        if self.variableCombo.currentIndex() == 4:
            variable = nvn
            
        if self.variableCombo.currentIndex() == 5:
            variable = pn        
        return variable

    def value(self):
        """
        Simple function to find the value of the point on the graph determined by user inputs
        Appends the value to a value line
        """
        x = (self.xspin.text())
        y = (self.yspin.text())
        z = (self.zspin.text())
        t = (self.tspin.text())
        variable = self.variable()
        self.valueLine.setText(str(variable[int(t),int(x),int(y),int(z)]))


    def divide(self):

        x = (self.xspin.text())
        y = (self.yspin.text())
        z = (self.zspin.text())
        t = (self.tspin.text())
        variable = self.variable()            
        self.divideByLine.setText(str(variable[int(t),int(x),int(y),int(z)]))
        divide = float(self.valueLine.text())/float(self.divideByLine.text())
        self.answerLine.setText(str(divide))


    def list_defaults(self):
        """
        Based on the list_archive function this finds all the files in the defaults
        folder within the config folder
         """
        global defaultLst
        defaultLst = []
        defaultLst = os.listdir(currentDir+ '/Defaults')
        iniLst = []
        for file in defaultLst:
            if file.endswith('ini'):
                iniLst.append(file)
        return iniLst


    def appendToCombo(self):
            global defaultLst
            lst = defaultLst
            self.defaultCombo.clear()
            for file in lst:
                    parser2.read(currentDir+ '/Defaults/' + str(file))
                    name = parser2.get('heading', 'title')
                    self.defaultCombo.addItem(name)

    def loadDefault(self):
            index = int(self.defaultCombo.currentIndex())
            lst = (self.list_defaults())
            default = lst[index]
            parser2.read(currentDir+ '/Defaults/' + default)
            self.xspin.setValue(int(parser2.get('others','x')))
            self.yspin.setValue(int(parser2.get('others','y')))
            self.zspin.setValue(int(parser2.get('others','z')))
            self.tspin.setValue(int(parser2.get('others','time')))
            self.variableCombo.setCurrentIndex(int(parser2.get('main', 'variable')))
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

    def saveDefault(self):
          defaultSave.show()
          
############################################## GRAPHING TAB CODE ENDS ############################################
##################################################################################################################
          
    def runScan(self):
          scan.show()
          scan.sectionCombo.clear()
          parser.read(loadpath1)
          global sections
          sections = parser.sections()
          for section in sections:
            scan.sectionCombo.addItem(section)
            items = parser.items(section)
          scan.appendItems()
          for section in sections:
            scan.sectionCombo_2.addItem(section)
            items = parser.items(section)
          scan.appendItems2()  


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
                This saves to a .ini file in the defaults folder containing all the variable information
                about the spin boxes and tickboxes used to create graphs so that a user can give a name to
                default and save it for quick loading. Makes it easy to load commonly used graphs
                """
                name = self.defaultLine.displayText()
                x = window.xspin.value()
                y = window.yspin.value()
                z = window.zspin.value()
                t = window.tspin.value()
                variable = window.variableCombo.currentIndex()
                
                ## these will be True/False
                xall = str(window.xall.isChecked())
                yall = str(window.yall.isChecked())
                zall = str(window.zall.isChecked())
                tall = str(window.tall.isChecked())

                # creates the new .ini file in the defaults folder
                if name != "":
                        parser3 = configparser.ConfigParser()
                        parser3.add_section('heading')
                        parser3.set('heading', 'title', str(name))
                        parser3.add_section('main')
                        parser3.set('main', 'variable', variable)
                        parser3.add_section('others')
                        parser3.set('others', 'time', t)
                        parser3.set('others', 'x', x)
                        parser3.set('others', 'y', y)
                        parser3.set('others', 'z', z)
                        parser3.add_section('checkboxes')
                        parser3.set('checkboxes', 'time', tall)
                        parser3.set('checkboxes', 'x', xall)
                        parser3.set('checkboxes', 'y', yall)
                        parser3.set('checkboxes', 'z', zall)
                        with open(currentDir+ '/Defaults/' + str(name) + '.ini', 'w') as configfile:
                                parser3.write(configfile)
                        window.list_defaults()
                        window.appendToCombo()
                        
                        
                        

####################################### NEW CLASS #######################################

class dialogsave(QtGui.QMainWindow, Ui_Dialog):
        """
        the general order for saving goes... the user can either chose to run simulation or to write a new file. This changes the global variable run to True if running or false
        if not. The new path for saving to is calculated by using a date/time default as in calculate path. This path is used as the default text in the dialog box as in
        updatepath. On click of save button path is set equal to the string in the dialog box so the user can change their desired folder path for saving to. Create is then
        called. This checks to see is the path already exists and will create a new directory if not. It then copies all the files from the old folder into the new one. This
        ensures that all the dmp, log and restart files can be accessed for each run. Then the BOUT.inp, usernotes.ini and record.ini files are replaced with the new ones
        created accorinding to the user inputs. The save function also calls the restart function. If run == True then this will test whether a restart is required and call
        runit with either 'y' or 'n'.
        """
        
        def __init__(self, parent=None):
                """
                Initialisation routine
                """
                # These calls set up the window
                super(dialogsave, self).__init__(parent)
                self.setupUi(self)
                             
                # couldn't input the function directly into line edit
                
                self.buttonBox.accepted.connect(self.save)
                self.buttonBox.rejected.connect(self.close)
                self.buttonBox.accepted.connect(self.close)

        
        def simulationCode(self):
                """
                brings up a dialogbox leading to the load simulation code box
                """
                dialogSimulation.show()

        def loadSimCode(self):
                """
                when selected from the file menu it is annoying to pop up with a dialogbox so this runs without the
                dialog box created in the simulationCode function.
                """
                codeFile = QtGui.QFileDialog.getOpenFileNames(self, "Load simulation code file", QtCore.QDir.currentPath())
                codeFile = codeFile[0][0]
                position.set('exe', 'path', codeFile)
                with open(config, 'w') as configfile:
                    position.write(configfile)
                if os.path.isfile(codeFile):
                    window.simulationFile.setText(codeFile)
                        

        def updatepath(self):
                """
                defined because the path in the save box wasn't updating after multiple clicks
                """
                savepath = re.sub('/BOUT.inp', '', loadpath1)
                self.lineEdit.setText(savepath)
        
        def save(self):
                """
                uses the displayed text to createa path to sve to, so may be different
                to the automatic inital path
                """
                path = self.lineEdit.displayText()  #path of new file
                #global loadpath1 # path of original file
                self.create(path)
                        # the if not statement looks to see if the current source of code is a file and prompts the user to select one if not on initialisation

                window.list_archive('inp')      #adds the new file to the table in tab 1
                global run
                if run == 'scan':
                  window.runScan()
                  self.close()
                else:
                  self.restart(path)
                  self.close()
        
        def create(self, path):
                """
                creates a new folder in the archive for the next run to store config file, record.ini and usernotes.ini
                """
                # path = the paths given in the dave dialog box
                oldfolder = re.sub('/BOUT.inp', '', loadpath1)
                if path != oldfolder:               # if destination is different to source
                      
                      if not os.path.isdir(path):       # if destination is new creates it
                            os.makedirs(path)
                            
                      newfolder = path      # copies all files
                      oldfiles = os.listdir(oldfolder)
                      for file in oldfiles:
                        oldfilepath = oldfolder + '/' + file
                        newfilepath = newfolder + '/' + file
                        shutil.copy(oldfilepath, newfilepath)
                        
                      if os.path.isfile(oldfolder + '/usernotes.ini'):      # updates the usernotes
                          shutil.copy(oldfolder + '/usernotes.ini', newfolder + '/usernotes.ini')
                          with open(newfolder + '/usernotes.ini', 'wt') as file:
                              file.write(window.plainTextEdit.toPlainText())
                          file.close()
                      if not os.path.isfile(oldfolder + '/usernotes.ini'):
                          with open(newfolder + '/usernotes.ini', 'wt') as file:
                              file.write(window.plainTextEdit.toPlainText())
                          file.close()
                          
                      parentDir(loadpath1, path)      # updates the parentDir file
                      
                      path = path + '/' + 'BOUT.inp'
                      window.saveSettings(path)       # write an updated BOUT control file
                else:
                      path = path + '/' + 'BOUT.inp'    # if same folder selceted update BOUT file
                      window.saveSettings(path)
                      with open(oldfolder + '/usernotes.ini', 'wt') as file:
                          file.write(window.plainTextEdit.toPlainText())
                      file.close()
                      
                      
                window.tableWidget.clearContents()
                window.tableWidget.setRowCount(0)
                        
                      

        def restart(self, path):
                """
        determines whether the restart box has been ticked and changes the arguments received by mpi run, i.e. 'y' or 'n'
        then calls the runit function
        """
                global run, loadpath1
                if run == 'true':
                    runfolder = re.sub('/BOUT.inp', '', path)
                    loadpath = re.sub('/BOUT.inp', '', loadpath1)
                    
                    window.outputStream.clear()
                    restart = window.checkBox.isChecked()
                    numProc = window.procSpin.value()
                    nice = window.niceSpin.value()
                    if restart == False:
                        self.runit(runfolder, 'n', numProc, nice)
                    else:
                        inputfiles = os.listdir(runfolder)
                        for restartfile in inputfiles:
                            filepath = os.path.join(loadpath, 'BOUT.restart.0.nc')
                            if os.path.isfile(filepath):
                                restart = 'y'
                            else:
                                generalDialog.show()
                                generalDialog.label.setText(QtGui.QApplication.translate("Dialog", "No restart files in folder!" , None, QtGui.QApplication.UnicodeUTF8))
                        if restart == 'y':
                                self.runit(runfolder, 'y', numProc, nice)

                    run = 'false'


        def runit(self, path, restart, numProc, nice):
                self.worker = Worker(path, restart, numProc, nice, window.outputStream)
                window.tabWidget.setCurrentIndex(2)
                if not self.worker.isRunning():
                        self.worker.exiting= False
                        self.worker.start()
                        self.worker.dataLine1.connect(self.printit)


        def printit(self, value):
                # sends the signalled text from the worker to the output stream
                if value == '' and proc.poll() is not None:
                        v = 1
                else:
                        window.outputStream.insertPlainText(value)
                        window.outputStream.ensureCursorVisible()



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
        allows the user to copy a filepath from the history and load it into the GUI
        for editing
        """
        global loadpath1
        try:
            loadpath1 = self.lineEdit.displayText()+ '/BOUT.inp'
            changeHeadings(loadpath1)
            window.delete()
            window.tabWidget.setCurrentIndex(0)
            window.updateControls(loadpath1)
            window.tabWidget.setCurrentIndex(1)
            self.close()
            
        # if user doesn't copy the path exactly throws out an IOError, asked to check their input and try again
        except IOError:
            generalDialog.show()
            generalDialog.label.setText(QtGui.QApplication.translate("Dialog", "Try removing whitespace and additional \n characters from path" , None, QtGui.QApplication.UnicodeUTF8))

####################################### NEW CLASS #######################################

class Scandialog(QtGui.QMainWindow, Ui_ScanDialog):
    """
    This loads up the dialog box which contains all the inputs for the scanned runs. Scanned runs differ to normal runs in that they allow the user to run multiple runs
    using similar settings but for an increment on one or two of the variables. This is useful if you want to do a powering up sort of thing or look at how one variable
    changes another. it should be possible to increase by 'raw' amount were basically the specified number is added each run or by a percentage where it is multipled by
    the number each time.
    """
    def __init__(self, parent=None):
        """
        Initialisation routine
        """
        # These calls set up the window
        super(Scandialog, self).__init__(parent)
        self.setupUi(self)
        
        self.sectionCombo.currentIndexChanged.connect(self.appendItems)
        self.indexCombo.currentIndexChanged.connect(self.loadInitial)
        self.sectionCombo_2.currentIndexChanged.connect(self.appendItems2)
        self.indexCombo_2.currentIndexChanged.connect(self.loadInitial2)

        self.pushButton.clicked.connect(self.run)
        self.pushButton_2.clicked.connect(self.close)
        
    """
    The append functions and loadInitial functions read the config file and build up combo boxes based on the headings and options within the file.
    Clicking on a heading for the first combo box loads its options to the second combo box. The value of that option is then
    displayed in the line. There are two of each function to make it possible to scan two variables at once
    """
    def appendItems(self):
        self.indexCombo.clear()
        index = self.sectionCombo.currentIndex()
        currentSection = parser.items(sections[index])
        for item in currentSection:
          self.indexCombo.addItem(str(item[0]))
          
    def appendItems2(self):
        self.indexCombo_2.clear()
        index = self.sectionCombo_2.currentIndex()
        currentSection = parser.items(sections[index])
        for item in currentSection:
          self.indexCombo_2.addItem(str(item[0]))
          
    def loadInitial2(self):
        index = self.sectionCombo_2.currentIndex()
        index2= self.indexCombo_2.currentIndex()
        sections = parser.sections()
        items = parser.items(sections[index])
        item = items[index2]
        item = str(item[1])
        item = window.clean(item,'#')
        item= window.clean(item, '.')
        self.initialLine2.setText(item)

    def loadInitial(self):
        index = self.sectionCombo.currentIndex()
        index2= self.indexCombo.currentIndex()
        sections = parser.sections()
        items = parser.items(sections[index])
        item = items[index2]
        item = str(item[1])
        item = window.clean(item,'#')
        item= window.clean(item, '.')
        self.initialLine.setText(item)

    def run(self):
        """
        Once the user has selected all the options that they want and inputed in all the increment type information then sends all the
        variable information to runitscan
        """
        path = loadpath1
        path = re.sub('/BOUT.inp', '', loadpath1)
        restart = 'n'

        # first variable to scan
        key = self.sectionCombo.itemText(self.sectionCombo.currentIndex())
        subkey = self.indexCombo.itemText(self.indexCombo.currentIndex())
        initial  = self.initialLine.text()
        limit = self.finalLine.text()
        increment = self.incrementLine.text()

        # second variable to scan
        key2 = self.sectionCombo_2.itemText(self.sectionCombo_2.currentIndex())
        subkey2 = self.indexCombo_2.itemText(self.indexCombo_2.currentIndex())
        initial2 = self.initialLine2.text()
        limit2 = self.finalLine2.text()
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
        
        self.runitscan(path, key, subkey, initial, limit, increment, restart, key2, subkey2, initial2, limit2, increment2, incrementType, scanType, numProc, nice)
        self.close()

    def runitscan(self, path, key, subkey, initial, limit, increment, restart, key2, subkey2, initial2, limit2, increment2, incrementType, scanType, numProc, nice):
        """
        this function start the worker thread using the scanWorker class. All the variables are passed as arguments to scanbout.py. If scanbout doesn't recieve
        enough arguments then BOUT will fail to run. This means that if the  user doesn;t input all the increment info extra an error will occur an by seen in the
        output stream
        """
        self.worker = scanWorker(path, key, subkey, initial, limit, increment, restart, incrementType, scanType, key2, subkey2, initial2, limit2, increment2, numProc, nice, window.outputStream)
        window.tabWidget.setCurrentIndex(2)
        if not self.worker.isRunning():
                self.worker.exiting= False
                self.worker.start()
                self.worker.dataLine1.connect(self.printit)

    def printit(self, value):
            """
            this picks up the signal from the scan worker thread as the variable value and prints it to the output stream
            """
            if value == '' and proc.poll() is not None:
                    v = 1
            else:
                    window.outputStream.ensureCursorVisible()
                    window.outputStream.insertPlainText(value)
                    window.outputStream.ensureCursorVisible()
                    
####################################### NEW CLASS #######################################

class helpView(QtGui.QMainWindow, Ui_helpViewer):
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
        super(helpView, self).__init__(parent)
        self.setupUi(self)

    def openHelp(self):
          """
          opens the help file which is stored as an HTML for loading within a text editior
          """
          with open('helpHTML.htm', 'r') as helpfile:
              
              self.textBrowser.insertHtml(helpfile.read())
              helpfile.close()
              self.show()
          # opens the file so that the top of the file is showing 
          self.textBrowser.moveCursor(QTextCursor.Start)
          # stops user editing
          self.textBrowser.setReadOnly(True)

####################################### NEW CLASS #######################################

class resize(QtGui.QMainWindow, Ui_Resize):
    """
    Creates a a small window which contains lots of variables to change the appearence of the control boxes as created automtically
    so that the user can make sure they are best organised. 
    """
    def __init__(self, parent=None):
        """
        Initialisation routine
        """
        # These calls set up the window
        super(resize, self).__init__(parent)
        self.setupUi(self)

        # initialise the resize window with values from the config file
        self.leftSpin.setValue(int(position.get('appearance', 'leftborder')))
        self.vSpin.setValue(int(position.get('appearance', 'verticalseperation')))
        self.topSpin.setValue(int(position.get('appearance', 'topborder')))
        self.maxSpin.setValue(int(position.get('appearance', 'maxlength')))
        self.widthSpin.setValue(int(position.get('appearance', 'boxwidth')))
        self.hSpin.setValue(int(position.get('appearance', 'horizontalseperation')))
        self.labelxSpin.setValue(int(position.get('appearance', 'xlabel')))
        self.inputxSpin.setValue(int(position.get('appearance', 'xinput')))
        self.labelWidthSpin.setValue(int(position.get('appearance', 'labelwidth')))
        self.inputSepSpin.setValue(int(position.get('appearance', 'sepinput')))

        # changes the config file that has been read into the system
        self.leftSpin.valueChanged.connect(lambda: position.set('appearance', 'leftborder',self.leftSpin.value()))
        self.vSpin.valueChanged.connect(lambda: position.set('appearance', 'verticalseperation',self.vSpin.value()))
        self.topSpin.valueChanged.connect(lambda: position.set('appearance', 'topborder',self.topSpin.value()))
        self.maxSpin.valueChanged.connect(lambda: position.set('appearance', 'maxlength',self.maxSpin.value()))
        self.widthSpin.valueChanged.connect(lambda: position.set('appearance', 'boxwidth',self.widthSpin.value()))
        self.hSpin.valueChanged.connect(lambda: position.set('appearance', 'horizontalseperation',self.hSpin.value()))
        self.labelxSpin.valueChanged.connect(lambda: position.set('appearance', 'xlabel',self.labelxSpin.value()))
        self.inputxSpin.valueChanged.connect(lambda: position.set('appearance', 'xinput',self.inputxSpin.value()))
        self.labelWidthSpin.valueChanged.connect(lambda: position.set('appearance', 'labelwidth',self.labelWidthSpin.value()))
        self.inputSepSpin.valueChanged.connect(lambda: position.set('appearance', 'sepinput',self.inputSepSpin.value()))

        #  configures the button box
        self.ok.clicked.connect(self.updateConfig)
        self.ok.clicked.connect(self.close)
        self.cancel.clicked.connect(self.close)
        self.apply.clicked.connect(self.updateConfig)

    def updateConfig(self):
        """
        Writes all changes that have been made in the dialog box to the config file
        """
        global config
        with open (config, 'w') as configfile:
            position.write(configfile)
        self.updateValues()


    def updateValues(self):
        """
        Updates the positions of the boxes and inputs in the inputs tab taknig into account the changes to the control file that have been made. 
        """
        global leftBorder, verticalSeperation, topBorder, maxLength, boxWidth, horizontalSeperation, xLabel, xInput, labelWidth, sepInput, loadpath1
        with open(config) as fp:
            position = configparser.ConfigParser()
            position.optionxform = str
            position.readfp(fp)
        leftBorder = int(position.get('appearance', 'leftborder'))
        verticalSeperation = int(position.get('appearance', 'verticalseperation'))
        topBorder = int(position.get('appearance', 'topborder'))
        maxLength = int(position.get('appearance', 'maxlength'))
        boxWidth = int(position.get('appearance', 'boxwidth'))
        horizontalSeperation = int(position.get('appearance', 'horizontalseperation'))
        xLabel = int(position.get('appearance', 'xlabel'))
        xInput = int(position.get('appearance', 'xinput'))
        labelWidth = int(position.get('appearance', 'labelwidth'))
        sepInput = int(position.get('appearance', 'sepinput'))

        # the only way to get changes made here to appear on screen is to 'change tabs'.
        # this tab changing isn't visible but it seems to clear the memory
        window.tabWidget.setCurrentIndex(0)

        if loadpath1 == 'empty':
             window.delete()
             window.updateControls(loadpath)
        else:
             window.delete()
             loadpath1 = re.sub('/BOUT.inp', '', loadpath1)
             window.updateControls(loadpath1 + '/BOUT.inp')
        # return to original tab
        window.tabWidget.setCurrentIndex(1)
        

####################################### NEW CLASS #######################################

class dialogSimulation(QtGui.QMainWindow, Ui_dialogSimulation):
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
        super(dialogSimulation, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setupUi(self)
        self.pushButton.clicked.connect(self.chooseSimulation)

    def chooseSimulation(self):
        self.close()
        codeFile = QtGui.QFileDialog.getOpenFileNames(self, "Load simulation code file", QtCore.QDir.currentPath())
        codeFile = codeFile[0][0]
        position.set('exe', 'path', codeFile)
        with open(config, 'w') as configfile:
            position.write(configfile)
        if os.path.isfile(codeFile):
            window.simulationFile.setText(codeFile)
        
        
        

if __name__ == "__main__":
    import sys
    
    # Create a Qt application
    app = QtGui.QApplication(sys.argv)
    
    # Create the window

    dialogSimulation = dialogSimulation()
    helpView = helpView()
    dialog = dialogsave()
    generalDialog = dialogcompare()
    defaultSave = defaultsave()
    window = MainWindow()
    txt =textdisplay()
    window.list_archive('inp')
    window.show()
    txthist = textdisplayhistory()
    scan = Scandialog()
    resize = resize()
    # Run the application then exit    
    sys.exit(app.exec_())
    

    
