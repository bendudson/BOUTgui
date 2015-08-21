# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dialogSimulation.ui'
#
# Created: Thu Aug 20 18:32:48 2015
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

class Ui_dialogSimulation(object):
    def setupUi(self, dialogSimulation):
        dialogSimulation.setObjectName("dialogSimulation")
        dialogSimulation.resize(312, 93)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("BOUTguilogo.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        dialogSimulation.setWindowIcon(icon)
        self.pushButton = QtGui.QPushButton(dialogSimulation)
        self.pushButton.setGeometry(QtCore.QRect(113, 57, 75, 25))
        self.pushButton.setObjectName("pushButton")
        self.label = QtGui.QLabel(dialogSimulation)
        self.label.setGeometry(QtCore.QRect(-40, 0, 391, 61))
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")

        self.retranslateUi(dialogSimulation)
        QtCore.QMetaObject.connectSlotsByName(dialogSimulation)

    def retranslateUi(self, dialogSimulation):
        dialogSimulation.setWindowTitle(QtGui.QApplication.translate("dialogSimulation", "Choose simulation file", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton.setText(QtGui.QApplication.translate("dialogSimulation", "Ok", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("dialogSimulation", "Please choose a file containing the suitable \n"
"simulation code", None, QtGui.QApplication.UnicodeUTF8))

