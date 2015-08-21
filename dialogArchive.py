# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dialogArchive.ui'
#
# Created: Thu Aug 20 18:29:06 2015
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

class Ui_dialogArchive(object):
    def setupUi(self, dialogArchive):
        dialogArchive.setObjectName("dialogArchive")
        dialogArchive.resize(313, 93)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("BOUTguilogo.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        dialogArchive.setWindowIcon(icon)
        self.pushButton = QtGui.QPushButton(dialogArchive)
        self.pushButton.setGeometry(QtCore.QRect(110, 50, 75, 25))
        self.pushButton.setObjectName("pushButton")
        self.label = QtGui.QLabel(dialogArchive)
        self.label.setGeometry(QtCore.QRect(10, 10, 291, 41))
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")

        self.retranslateUi(dialogArchive)
        QtCore.QMetaObject.connectSlotsByName(dialogArchive)

    def retranslateUi(self, dialogArchive):
        dialogArchive.setWindowTitle(QtGui.QApplication.translate("dialogArchive", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton.setText(QtGui.QApplication.translate("dialogArchive", "Ok", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("dialogArchive", "Please choose a folder to use as an archive", None, QtGui.QApplication.UnicodeUTF8))

