#!/usr/bin/env python
import configparser, sys, os,  difflib, subprocess, threading
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
from scanboutwindow import *
from time import *
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

# Import Global Variables
#archive = 'C:\Python34\Archive'
archive = '/hwdisks/data/bd512/sol1d-scans/5e8'
loadpath1= 'empty'
run = 'false'
cell =False
parser = configparser.ConfigParser()
parser2 = configparser.ConfigParser()
parser.optionxform = str

# Used to load data from the config folder as inital data
loadpath = archive+ '/config/BOUT.inp'
addTiming(loadpath)
"""
NOTE: BOUT.inp can not be passed through config parser unless it has a heading
for all sections. A default heading has been added at the start with addTiming if ther
isn't already a heading. This has to be removed for any simulations because BOUT++
will not run with an additional heading. The removeTiming function is used later in
the program for this. 
"""
parser.read(loadpath)

####################################### NEW CLASS #######################################

class Worker(QThread):
##    """ 
##    This thread runs the simulations in the backgrounds so preventing the GUI from freezing while running
##    STDOUT is redirected to a signal which is collected by the text editor of the output stream
##        """

      dataLine1 = Signal(str)
      def __init__(self, path, restart, outputStream, parent = None):
              QThread.__init__(self, parent)
              self.path = path + '/'
              self.loadpath = path
              self.restart = restart
              self.outputStream = outputStream
              self.exiting = False
              window.tabWidget.setTabEnabled(2, True)

      def run(self):
          # proc runs the simulation
          proc = subprocess.Popen(['/hwdisks/home/jh1479/python/simulation/runboutSim.py', str(self.path), str(self.restart)],
                                  shell = False, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
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
      def __init__(self, path, key, subkey, initial, limit, increment, restart, outputStream, parent = None):
              QThread.__init__(self, parent)
              self.path = path
              self.key = key
              self.subkey = subkey
              self.initial = initial
              self.limit = limit
              self.increment = increment
              self.restart = restart
              self.outputStream = outputStream
              self.exiting = False
              window.tabWidget.setTabEnabled(2, True)

      def run(self):
          # proc runs the simulation
          proc = subprocess.Popen(['/hwdisks/home/jh1479/python/simulation/scanboutSim.py', str(self.path), str(self.key), str(self.subkey), str(self.initial), str(self.limit), str(self.increment), str(self.restart)],
                                  shell = False, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
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
            window.dataTable.clearContents()
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
            window.commandEntered('t = 0.5*p/ne')
            sleep(0.1)
            window.commandEntered('nvn = collect("NVn")')
            sleep(0.1)
            window.commandEntered('pn = collect("Pn")')
            sleep(0.1)
            from boutdata import collect
            global p, ne, nvi, nn, nvn, pn
            p = collect("P"); ne = collect("Ne"); nvi = collect("Nvi"); nn = collect("Nn"); t = 0.5*p/ne
            nvn = collect("NVn"); pn = collect("Pn")
            window.collectedLabel.setText(str(self.path))
            self.exit()
            
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
        
        ###################################################
        # exit the program
        self.actionExit.triggered.connect(self.close)
        
        ###################################################
        # compare
        self.actionCompare.triggered.connect(self.compareClicked)

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
        # Run counter
        
        self.runid = 0 # Keeps track of highest ID number
        
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
       
        ###################################################################################################################
        # CHANGE CONTROL FILE WITH SPINNER INPUTS

        #timing
        self.NoutSpin.valueChanged.connect(lambda: self.change('timing', 'NOUT', self.NoutSpin.value()))
        self.TimeStepSpin.valueChanged.connect(lambda: self.change('timing', 'TIMESTEP', self.TimeStepSpin.value()))
        self.MzSpin.valueChanged.connect(lambda: self.change('timing', 'MZ', self.MzSpin.value()))
        self.MXGSpin.valueChanged.connect(lambda: self.change('timing', 'MXG', self.MXGSpin.value()))

        # mesh spinners      
        self.nxSpin.valueChanged.connect(lambda: self.change('mesh', 'nx', self.nxSpin.value()))
        self.nySpin.valueChanged.connect(lambda: self.change('mesh', 'ny', self.nySpin.value()))
        self.lengthSpin.valueChanged.connect(lambda: self.change('mesh', 'length', self.lengthSpin.value()))
        self.dxSpin.valueChanged.connect(lambda: self.change('mesh', 'dx', self.dxSpin.value()))
        self.ixseps1Spin.valueChanged.connect(lambda: self.change('mesh', 'ixseps1', self.ixseps1Spin.value()))
        self.ixseps2Spin.valueChanged.connect(lambda: self.change('mesh', 'ixseps2', self.ixseps2Spin.value()))
        self.rxySpin.valueChanged.connect(lambda: self.change('mesh', 'Rxy', self.rxySpin.value()))
        self.bpxySpin.valueChanged.connect(lambda: self.change('mesh', 'Bpxy', self.bpxySpin.value()))
        self.btxySpin.valueChanged.connect(lambda: self.change('mesh', 'Btxy', self.btxySpin.value()))
        self.bxySpin.valueChanged.connect(lambda: self.change('mesh', 'Bxy', self.bxySpin.value()))
        self.htheSpin.valueChanged.connect(lambda: self.change('mesh', 'hthe', self.htheSpin.value()))
        self.sintySpin.valueChanged.connect(lambda: self.change('mesh', 'sinty', self.sintySpin.value()))
        # mesh line edit
        self.dyLine.textChanged.connect(lambda: self.change('mesh', 'dy', self.dyLine.text()))

        # ddy text edit
        self.firstLine.textChanged.connect(lambda: self.change('ddy', 'first', self.firstLine.text()))
        self.secondLine.textChanged.connect(lambda: self.change('ddy', 'second', self.secondLine.text()))
        self.upwindLine.textChanged.connect(lambda: self.change('ddy', 'upwind', self.upwindLine.text()))
    
        # solver spinner
        self.mxstepSpin.valueChanged.connect(lambda: self.change('solver', 'mxstep', self.mxstepSpin.value()))

        # SOL1D
            #spinners
        self.TnormSpin.valueChanged.connect(lambda: self.change('SOL1D', 'Tnorm', self.TnormSpin.value()))
        self.BnormdoubleSpin.valueChanged.connect(lambda: self.change('SOL1D', 'Bnorm', self.BnormdoubleSpin.value()))
        self.AAdoubleSpin.valueChanged.connect(lambda: self.change('SOL1D', 'AA', self.AAdoubleSpin.value()))
        self.EionizeSpin.valueChanged.connect(lambda: self.change('SOL1D', 'Eionize', self.EionizeSpin.value()))
        self.vwallSpin.valueChanged.connect(lambda: self.change('SOL1D', 'vwall', self.vwallSpin.value()))
        self.frecycleSpin.valueChanged.connect(lambda: self.change('SOL1D', 'frecycle', self.frecycleSpin.value()))
        self.fredistributeSpin.valueChanged.connect(lambda: self.change('SOL1D', 'fredistribute', self.fredistributeSpin.value()))
        self.gaspuffSpin.valueChanged.connect(lambda: self.change('SOL1D', 'gaspuff', self.gaspuffSpin.value()))
        self.dneutSpin.valueChanged.connect(lambda: self.change('SOL1D', 'dneut', self.dneutSpin.value()))
        self.fimpSpin.valueChanged.connect(lambda: self.change('SOL1D', 'fimp', self.fimpSpin.value()))
        self.sheath_gammaSpin.valueChanged.connect(lambda: self.change('SOL1D', 'sheath_gamma', self.sheath_gammaSpin.value()))
        self.hyperSpin.valueChanged.connect(lambda: self.change('SOL1D', 'hyper', self.hyperSpin.value()))
            #text edit        
        self.redist_weightLine.textChanged.connect(lambda: self.change('SOL1D', 'redist_weight', self.redist_weightLine.text()))
        self.areaLine.textChanged.connect(lambda: self.change('SOL1D', 'area', self.areaLine.text()))
        self.NnormLine.textChanged.connect(lambda: self.change('SOL1D', 'Nnorm', self.NnormLine.text()))
        self.nlossLine.textChanged.connect(lambda: self.change('SOL1D', 'nloss', self.nlossLine.text()))
            #spin boxes
        self.diagnoseCombo.currentIndexChanged.connect(lambda: self.change('SOL1D', 'diagnose', self.diagnoseCombo.currentText()))
        self.atomicCombo.currentIndexChanged.connect(lambda: self.change('SOL1D', 'atomic', self.atomicCombo.currentText()))
        
        # All
            #spinner
        self.scaleDoubleSpin.valueChanged.connect(lambda: self.change('All', 'scale', self.scaleDoubleSpin.value()))
            #text edit
        self.bndry_allLine.textChanged.connect(lambda: self.change('All', 'bndry_all', self.bndry_allLine.text()))
     
        # Ne
            #spinners
        self.scale2Spin.valueChanged.connect(lambda: self.change('Ne', 'scale', self.scale2Spin.value()))
        self.functionDoubleSpin2.valueChanged.connect(lambda: self.change('Ne', 'function', self.functionDoubleSpin2.value()))
            #text edit
        self.sourceNeLine.textChanged.connect(lambda: self.change('Ne', 'source', self.sourceNeLine.text()))
        self.fluxLine.textChanged.connect(lambda: self.change('Ne', 'flux', self.fluxLine.text()))
        
        # NVi spinner
            #spinner
        self.scale3Spin.valueChanged.connect(lambda: self.change('NVi', 'scale', self.scale3Spin.value()))
            #text edits
        self.functionNViLine.textChanged.connect(lambda: self.change('NVi', 'function', self.functionNViLine.text()))
        self.bndry_targetLine.textChanged.connect(lambda: self.change('NVi', 'bndry_target', self.bndry_targetLine.text()))

        # P
            #spinners
        self.scale4Spin.valueChanged.connect(lambda: self.change('P', 'scale', self.scale4Spin.value()))
        self.functionDoubleSpin4.valueChanged.connect(lambda: self.change('P', 'function', self.functionDoubleSpin4.value()))
            #text edit
        self.sourceLine.textChanged.connect(lambda: self.change('P', 'source', self.sourceLine.text()))
        self.powerfluxLine.textChanged.connect(lambda: self.change('P', 'powerflux', self.powerfluxLine.text()))  

        # Nn
            #spinner
        self.scale5Spin.valueChanged.connect(lambda: self.change('Nn', 'scale', self.scale5Spin.value()))
            #text edit
        self.functionNnLine.textChanged.connect(lambda: self.change('Nn', 'function', self.functionNnLine.text()))

        #Nvn
            #combobox
        self.evolveNVnCombo.currentIndexChanged.connect(lambda: self.change('NVn', 'evolve', self.evolveNVnCombo.currentText()))
        
        # Pn
            #spinners
        self.TstartDoubleSpin.valueChanged.connect(lambda: self.change('Pn', 'Tstart', self.TstartDoubleSpin.value()))
        self.scaleDoubleSpin6.valueChanged.connect(lambda: self.change('Pn', 'scale', self.scaleDoubleSpin6.value()))
            #text edit
        self.funcitonPnLine.textChanged.connect(lambda: self.change('Pn', 'function', self.funcitonPnLine.text()))
            #combox
        self.evolvePnCombo.currentIndexChanged.connect(lambda: self.change('Pn', 'evolve', self.evolvePnCombo.currentText()))


    def changerun(self):
        """
        creates a global variable run that changes the save dialog boxes function so
        that clicking on run causes simualtion not just saving
        """
        dialog.label.setText(QtGui.QApplication.translate("Dialog", "Save path for control file and comments file:" , None, QtGui.QApplication.UnicodeUTF8))
        global run
        run = 'true'
        self.showDialog()

    def changeScan(self):
        """
        creates a global variable run that changes the save dialog boxes function so
        that clicking on run causes simualtion not just saving
        """
        dialog.label.setText(QtGui.QApplication.translate("Dialog", "General Save Path for Mulitple Runs:" , None, QtGui.QApplication.UnicodeUTF8))
        global run
        run = 'scan'
        self.showDialog()
    
    def updateControls(self, inpfile):
        """
        when a new file is loaded the spinners in the GUI are updated to start on the same value
        as that in the new file
        """
        folder = re.sub('/BOUT.inp', '', loadpath1)
        text = open(folder + '/usernotes.ini').read()
        self.plainTextEdit.setPlainText(text)
        parser.read(inpfile)
        self.fileLabel.setText(QtGui.QApplication.translate("MainWindow", str(loadpath1), None, QtGui.QApplication.UnicodeUTF8))

        # timing section 
        self.NoutSpin.setValue(float(self.clean(parser.get('timing','NOUT'),'#')))
        self.TimeStepSpin.setValue(float(self.clean(parser.get('timing','TIMESTEP'),'.')))     # for some reason this has a dot after the value which confuses the spin boxes
        self.MzSpin.setValue(float(self.clean(parser.get('timing','MZ'), '#')))
        self.MXGSpin.setValue(float(self.clean(parser.get('timing','MXG'),'#')))

        # mesh section 
        self.nxSpin.setValue(float(self.clean(parser.get('mesh','nx'),'#')))
        self.nySpin.setValue(float(self.clean(parser.get('mesh','ny'),'#')))
        self.lengthSpin.setValue(float(self.clean(parser.get('mesh','length'), '#')))
        self.dxSpin.setValue(float(self.clean(parser.get('mesh','dx'),'#')))
        self.ixseps1Spin.setValue(float(self.clean(parser.get('mesh','ixseps1'),'#')))
        self.ixseps2Spin.setValue(float(self.clean(parser.get('mesh','ixseps2'), '#')))
        self.rxySpin.setValue(float(self.clean(parser.get('mesh','Rxy'),'#')))
        self.bpxySpin.setValue(float(self.clean(parser.get('mesh','Bpxy'),'#')))
        self.btxySpin.setValue(float(self.clean(parser.get('mesh','Btxy'),'#'))) 
        self.bxySpin.setValue(float(self.clean(parser.get('mesh','Bxy'),'#')))
        self.htheSpin.setValue(float(self.clean(parser.get('mesh','hthe'), '#')))
        self.sintySpin.setValue(float(self.clean(parser.get('mesh','sinty'),'#')))
        # mesh line
        self.dyLine.setText(str(self.clean(parser.get('mesh','dy'),'#')))        

        # ddy section
        self.firstLine.setText(str(self.clean(parser.get('ddy','first'),'#')))
        self.secondLine.setText(str(self.clean(parser.get('ddy','second'),'#')))
        self.upwindLine.setText(str(self.clean(parser.get('ddy','upwind'),'#')))


        # solver section
        self.mxstepSpin.setValue(float(self.clean(parser.get('solver','mxstep'),'#')))

        # SOL1D section
            #spinner
        self.TnormSpin.setValue(float(self.clean(parser.get('SOL1D','Tnorm'),'#')))
        self.BnormdoubleSpin.setValue(float(self.clean(parser.get('SOL1D','Bnorm'),'#')))
        self.AAdoubleSpin.setValue(float(self.clean(parser.get('SOL1D','AA'), '#')))
        self.EionizeSpin.setValue(float(self.clean(parser.get('SOL1D','Eionize'),'#')))
        self.vwallSpin.setValue(float(self.clean(parser.get('SOL1D','vwall'),'#')))
        self.frecycleSpin.setValue(float(self.clean(parser.get('SOL1D','frecycle'), '#')))
        self.fredistributeSpin.setValue(float(self.clean(parser.get('SOL1D','fredistribute'),'#')))
        self.gaspuffSpin.setValue(float(self.clean(parser.get('SOL1D','gaspuff'),'#')))
        self.dneutSpin.setValue(float(self.clean(parser.get('SOL1D','dneut'),'#'))) 
        self.fimpSpin.setValue(float(self.clean(parser.get('SOL1D','fimp'),'#')))
        self.sheath_gammaSpin.setValue(float(self.clean(parser.get('SOL1D','sheath_gamma'), '#')))
        self.hyperSpin.setValue(float(self.clean(parser.get('SOL1D','hyper'),'#')))
            #text edit
        self.redist_weightLine.setText(str(self.clean(parser.get('SOL1D','redist_weight'),'#')))
        self.areaLine.setText(str(self.clean(parser.get('SOL1D','area'),'#')))
        self.NnormLine.setText(str(self.clean(parser.get('SOL1D','Nnorm'),'#')))
        self.nlossLine.setText(str(self.clean(parser.get('SOL1D','nloss'),'#')))
            #combo boxes
        self.atomicCombo.setCurrentIndex(self.TorF('SOL1D', 'atomic'))
        self.diagnoseCombo.setCurrentIndex(self.TorF('SOL1D', 'diagnose'))
              
        # All section
            #spinner
        self.scaleDoubleSpin.setValue(float(self.clean(parser.get('All','scale'),'#')))
            #text edit
        self.bndry_allLine.setText(str(self.clean(parser.get('All','bndry_all'),'#')))

        # Ne section
            #spinner
        self.scale2Spin.setValue(float(self.clean(parser.get('Ne','scale'),'#')))
        self.functionDoubleSpin2.setValue(float(self.clean(parser.get('Ne','function'),'#')))
            #text
        self.sourceNeLine.setText(str(self.clean(parser.get('Ne','source'),'#')))
        self.fluxLine.setText(str(self.clean(parser.get('Ne','flux'),'#')))

        #NVi section
            #spinner
        self.scale3Spin.setValue(float(self.clean(parser.get('NVi','scale'),'#')))
            #text edit
        self.functionNViLine.setText(str(self.clean(parser.get('NVi','function'),'#')))
        self.bndry_targetLine.setText(str(self.clean(parser.get('NVi','bndry_target'),'#')))

        #P section
            #spinners
        self.scale4Spin.setValue(float(self.clean(parser.get('P','scale'),'#')))
        self.functionDoubleSpin4.setValue(float(self.clean(parser.get('P','function'),'#')))
            #text edit
        self.sourceLine.setText(str(self.clean(parser.get('P','source'),'#')))
        self.powerfluxLine.setText(str(self.clean(parser.get('P','powerflux'),'#')))

        # Nn section
            #spinner
        self.scale5Spin.setValue(float(self.clean(parser.get('Nn','scale'),'#')))
            #text edit
        self.functionNnLine.setText(str(self.clean(parser.get('Nn','function'),'#')))

        #NVn section
            #combo box
        self.evolveNVnCombo.setCurrentIndex(self.TorF('NVn', 'evolve'))      

        # Pn section
            #spinners
        self.TstartDoubleSpin.setValue(float(self.clean(parser.get('Pn','Tstart'),'#')))
        self.scaleDoubleSpin6.setValue(float(self.clean(parser.get('Pn','scale'),'#')))
            #text edit
        self.funcitonPnLine.setText(str(self.clean(parser.get('Pn','function'),'#')))
            #combo box
        self.evolvePnCombo.setCurrentIndex(self.TorF('Pn', 'evolve'))


        

# These functions control the command line part of the graphing tab
#**************************************************************************************************#   
    def write(self, text):
        """
        Write some log text to output text widget
        """
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

#***************************************************************************************************#     
# end of command line functions - from pyxpad...




    def collectit(self):
      """
    Triggered by clicking on the collect button. Checks to see is anything has been loaded, and if not shows a dialog, if so then runs the collect function
      """
      if loadpath1 == 'empty':
        generalDialog.label.setText(QtGui.QApplication.translate("Dialog", "Please load file to collect from" , None, QtGui.QApplication.UnicodeUTF8))
        generalDialog.show()
      else:
            global loadpath1
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
        global loadpath1, loadpath2
        loadpath = str(archive) + str(directory[x])
        addTiming(loadpath)
        # generally loading will proceed to load from the parser and update the controls
        if 'loadpath2' not in globals():
            loadpath1 = loadpath
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
        window.tableWidget.clearContents()
        lst = os.listdir(archive)
        list.sort(lst)
        #directory is a global variable used in many functions
        global directory
        directory = []
        #look in each folder
        for folder in lst:
            path = os.path.join(archive, str(folder))
            # if finds files of correct type finds there attributes
            if os.path.isdir(path):
              for file in os.listdir(path):
                  allpaths = path + '/' + file
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
                              directory.append(('/' + folder + '/' + file + '/' + files,a,b, filedata))
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
                          directory.append(('/'+str(folder)+'/'+str(file),a,b, filedata))
                          # lists the found files attributes from directory in table in the GUI 
        for i in range(len(directory)):
            filenumber = str(i+1)
            pathname = str(directory[i][0])
            self.insertTableRow(pathname, directory[i][1], directory[i][2], directory[i][3])

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
        folder within the archive
         """
        global defaultLst
        defaultLst = []
        defaultLst = os.listdir(archive+ '/Defaults')
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
                    parser2.read(archive+ '/Defaults/' + str(file))
                    name = parser2.get('heading', 'title')
                    self.defaultCombo.addItem(name)

    def loadDefault(self):
            index = int(self.defaultCombo.currentIndex())
            lst = (self.list_defaults())
            default = lst[index]
            parser2.read(archive+ '/Defaults/' + default)
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


####################################### NEW CLASS #######################################

class defaultsave(QtGui.QMainWindow, Ui_defaultsave):

        def __init__(self, parent=None):
                """
                Initialisation routine
                """
                # These calls set up the window
                super(defaultsave, self).__init__(parent)
                self.setupUi(self)
                self.buttonBox.accepted.connect(self.save)
                self.buttonBox.rejected.connect(self.close)
                self.buttonBox.accepted.connect(self.close)
                

        def save(self):
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
                        with open(archive+ '/Defaults/' + str(name) + '.ini', 'w') as configfile:
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
                self.updatepath()

                
                # couldn't input the function directly into line edit
                
                self.buttonBox.accepted.connect(self.save)
                self.buttonBox.rejected.connect(self.close)
                self.buttonBox.accepted.connect(self.close)

        def calculatePath(self):
                
                """
                calculates the initial path as an automatic being related to date
                """

                # calculates the path for next folder in the archive and names it
                lst = os.listdir(str(archive))
                name = datetime.now().strftime('%d-%m-%y at %H-%M')
                newpath = os.path.join(archive, name)
                return str(newpath)        

        def updatepath(self):
                """
                defined because the path in the save box wasn't updating after multiple clicks
                """
                path = self.calculatePath()
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
                      
                      print 'path different', path, loadpath1
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
                      
                      path = path + '/' + 'BOUT.inp'    # write an updated BOUT control file
                      with open (path, 'w') as configfile:
                              parser.write(configfile)

                else:
                      path = path + '/' + 'BOUT.inp'    # if same folder selceted update BOUT file
                      with open (path, 'w') as configfile:
                              parser.write(configfile)
                window.tableWidget.clearContents()
                        
                        


##                
##                if path != loadpath1:  
##                    if not os.path.isdir(path):
##                        os.makedirs(path)
##                    oldfolder = re.sub('/BOUT.inp', '', loadpath1)
##                    newfolder = re.sub('/BOUT.inp', '', path)
##                    global finalpath
##                    finalpath = newfolder
##                    inputfiles = os.listdir(oldfolder)
##                    for runfile in inputfiles:
##                        
##                        newpath = os.path.join(newfolder, runfile)
##                        oldpath = os.path.join(oldfolder, runfile)
##                        print oldpath+'/'+ runfile
##                        if os.path.isfile(str(runfile)) == True:                  
##                          shutil.copy(oldpath, newpath)
##                          newfolder = re.sub(runfile, '', newpath) 
##                          oldfolder = re.sub(runfile, '', oldpath)
##
##
##                          
##                    if os.path.isfile(oldfolder + '/usernotes.ini'):
##                        shutil.copy(oldfolder + '/usernotes.ini', newfolder + '/usernotes.ini')
##                        with open(newfolder + '/usernotes.ini', 'wt') as file:
##                            file.write(window.plainTextEdit.toPlainText())
##                        file.close()
##                    if not os.path.isfile(oldfolder + '/usernotes.ini'):
##                        with open(newfolder + '/usernotes.ini', 'wt') as file:
##                            file.write(window.plainTextEdit.toPlainText())
##                        file.close()   
##                    parentDir(loadpath1, path)
##                    path = path + '/' + 'BOUT.inp'
##                    with open (path, 'w') as configfile:
##                            parser.write(configfile)
##
##                else:
##                      path = path + '/' + 'BOUT.inp'
##                      with open (path, 'w') as configfile:
##                              parser.write(configfile)
##                window.tableWidget.clearContents()

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
                    if restart == False:
                        self.runit(runfolder, 'n')
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
                                self.runit(runfolder, 'y')

                    run = 'false'


        def runit(self, path, restart):
                self.worker = Worker(path, restart, window.outputStream)
                window.tabWidget.setCurrentIndex(2)
                if not self.worker.isRunning():
                        self.worker.exiting= False
                        self.worker.start()
                        self.worker.dataLine1.connect(self.printit)


        def printit(self, value):
                if value == '' and proc.poll() is not None:
                        v = 1
                else:
                        window.outputStream.insertPlainText(value)
                        window.outputStream.ensureCursorVisible()

####################################### NEW CLASS #######################################

class dialogcompare(QtGui.QMainWindow, Ui_Dialogcompare):
    def __init__(self, parent=None):
        """
        Initialisation routine
        """
        # These calls set up the window
        super(dialogcompare, self).__init__(parent)
        self.setupUi(self)

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
            loadpath1 = self.lineEdit.displayText()
            parser.read(str(loadpath1))
            window.updateControls(loadpath1)
            window.tabWidget.setCurrentIndex(1)
            self.close()
        # if user doesn't copy the path exactly throws out a TypeError, asked to check their input and try again
        except TypeError:
            generalDialog.show()
            generalDialog.label.setText(QtGui.QApplication.translate("Dialog", "Try removing whitespace and additional \n characters from path" , None, QtGui.QApplication.UnicodeUTF8))

####################################### NEW CLASS #######################################

class Scandialog(QtGui.QMainWindow, Ui_ScanDialog):
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
        super(Scandialog, self).__init__(parent)
        self.setupUi(self)
        self.sectionCombo.currentIndexChanged.connect(self.appendItems)
        self.indexCombo.currentIndexChanged.connect(self.loadInitial)
        self.pushButton.clicked.connect(self.run)
        self.pushButton_2.clicked.connect(self.close)

    def appendItems(self):
        self.indexCombo.clear()
        index = self.sectionCombo.currentIndex()
        currentSection = parser.items(sections[index])
        for item in currentSection:
          self.indexCombo.addItem(str(item[0]))

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
        path = loadpath1
        path = re.sub('/BOUT.inp', '', loadpath1)
        restart = 'n'
        key = self.sectionCombo.itemText(self.sectionCombo.currentIndex())
        subkey = self.indexCombo.itemText(self.indexCombo.currentIndex())
        initial  = self.initialLine.text()
        limit = self.finalLine.text()
        increment = self.incrementLine.text()
        if self.checkBox.isChecked() == True:
          restart = 'y'
        else:
          restart = 'n'
        self.runitscan(path, key, subkey, initial, limit, increment, restart)
        self.close()

    def runitscan(self, path, key, subkey, initial, limit, increment, restart):
        self.worker = scanWorker(path, key, subkey, initial, limit, increment, restart, window.outputStream)
        window.tabWidget.setCurrentIndex(2)
        if not self.worker.isRunning():
                self.worker.exiting= False
                self.worker.start()
                self.worker.dataLine1.connect(self.printit)

    def printit(self, value):
            if value == '' and proc.poll() is not None:
                    v = 1
            else:
                    window.outputStream.ensureCursorVisible()
                    window.outputStream.insertPlainText(value)
                    window.outputStream.ensureCursorVisible()    
        
if __name__ == "__main__":
    import sys
    
    # Create a Qt application
    app = QtGui.QApplication(sys.argv)
    
    # Create the window
    dialog = dialogsave()
    window = MainWindow()
    defaultSave = defaultsave()
    generalDialog = dialogcompare()
    txt =textdisplay()
    window.list_archive('inp')
    window.show()
    txthist = textdisplayhistory()
    scan = Scandialog()
    # Run the application then exit    
    sys.exit(app.exec_())
    

    
