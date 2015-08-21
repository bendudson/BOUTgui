# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'textdisplay.ui'
#
# Created: Thu Aug 20 18:31:15 2015
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

class Ui_TextWindow(object):
    def setupUi(self, TextWindow):
        TextWindow.setObjectName("TextWindow")
        TextWindow.resize(795, 428)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("BOUTguilogo.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        TextWindow.setWindowIcon(icon)
        self.centralwidget = QtGui.QWidget(TextWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.textBrowser = QtGui.QTextBrowser(self.centralwidget)
        self.textBrowser.setGeometry(QtCore.QRect(20, 30, 741, 321))
        self.textBrowser.setObjectName("textBrowser")
        self.pushButton = QtGui.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(710, 360, 75, 25))
        self.pushButton.setObjectName("pushButton")
        TextWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(TextWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 795, 20))
        self.menubar.setObjectName("menubar")
        TextWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(TextWindow)
        self.statusbar.setObjectName("statusbar")
        TextWindow.setStatusBar(self.statusbar)

        self.retranslateUi(TextWindow)
        QtCore.QObject.connect(self.pushButton, QtCore.SIGNAL("clicked()"), TextWindow.close)
        QtCore.QMetaObject.connectSlotsByName(TextWindow)

    def retranslateUi(self, TextWindow):
        TextWindow.setWindowTitle(QtGui.QApplication.translate("TextWindow", "Results of Comparison", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton.setText(QtGui.QApplication.translate("TextWindow", "Exit", None, QtGui.QApplication.UnicodeUTF8))

