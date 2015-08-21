# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './UIfiles/dialogcompare.ui'
#
# Created: Thu Aug 20 19:27:37 2015
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

class Ui_Dialogcompare(object):
    def setupUi(self, Dialogcompare):
        Dialogcompare.setObjectName("Dialogcompare")
        Dialogcompare.resize(284, 99)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("BOUTguilogo.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Dialogcompare.setWindowIcon(icon)
        self.label = QtGui.QLabel(Dialogcompare)
        self.label.setGeometry(QtCore.QRect(0, 10, 271, 41))
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.pushButton = QtGui.QPushButton(Dialogcompare)
        self.pushButton.setGeometry(QtCore.QRect(90, 60, 75, 25))
        self.pushButton.setObjectName("pushButton")

        self.retranslateUi(Dialogcompare)
        QtCore.QObject.connect(self.pushButton, QtCore.SIGNAL("clicked()"), Dialogcompare.close)
        QtCore.QMetaObject.connectSlotsByName(Dialogcompare)

    def retranslateUi(self, Dialogcompare):
        Dialogcompare.setWindowTitle(QtGui.QApplication.translate("Dialogcompare", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialogcompare", "Select two files to compare", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton.setText(QtGui.QApplication.translate("Dialogcompare", "Ok", None, QtGui.QApplication.UnicodeUTF8))

