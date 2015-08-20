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
from PySide import QtCore, QtGui

# Import PySide Ui_Resize
from resize import *

class resize(QtGui.QMainWindow, Ui_Resize):
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
        global config
        with open (config, 'w') as configfile:
            position.write(configfile)
        self.updateValues()


    def updateValues(self):
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
        window.tabWidget.setCurrentIndex(0)

        if loadpath1 == 'empty':
             window.updateControls(loadpath)
        else:
             loadpath1 = re.sub('/BOUT.inp', '', loadpath1)
             window.updateControls(loadpath1 + '/BOUT.inp')

        window.tabWidget.setCurrentIndex(1)

        
