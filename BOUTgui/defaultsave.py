# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'defaultsave.ui'
#
# Created: Mon Jul 20 11:35:14 2015
#      by: pyside-uic 0.2.15 running on PySide 1.2.1
#
# WARNING! All changes made in this file will be lost!
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

class Ui_defaultsave(object):
    def setupUi(self, defaultsave):
        defaultsave.setObjectName("defaultsave")
        defaultsave.resize(392, 94)
        self.buttonBox = QtGui.QDialogButtonBox(defaultsave)
        self.buttonBox.setGeometry(QtCore.QRect(40, 60, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.defaultLine = QtGui.QLineEdit(defaultsave)
        self.defaultLine.setGeometry(QtCore.QRect(10, 30, 371, 21))
        self.defaultLine.setObjectName("defaultLine")
        self.label = QtGui.QLabel(defaultsave)
        self.label.setGeometry(QtCore.QRect(10, 10, 241, 16))
        self.label.setObjectName("label")
        self.retranslateUi(defaultsave)
        QtCore.QMetaObject.connectSlotsByName(defaultsave)

    def retranslateUi(self, defaultsave):
        defaultsave.setWindowTitle(QtGui.QApplication.translate("defaultsave", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("defaultsave", "Name of New Default", None, QtGui.QApplication.UnicodeUTF8))

