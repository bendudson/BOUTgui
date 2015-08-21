# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'textdisplayhistory.ui'
#
# Created: Thu Aug 20 18:29:53 2015
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

class Ui_TextWindowHistory(object):
    def setupUi(self, TextWindowHistory):
        TextWindowHistory.setObjectName("TextWindowHistory")
        TextWindowHistory.resize(795, 426)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("BOUTguilogo.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        TextWindowHistory.setWindowIcon(icon)
        self.centralwidget = QtGui.QWidget(TextWindowHistory)
        self.centralwidget.setObjectName("centralwidget")
        self.textBrowser = QtGui.QTextBrowser(self.centralwidget)
        self.textBrowser.setGeometry(QtCore.QRect(20, 30, 741, 301))
        self.textBrowser.setObjectName("textBrowser")
        self.pushButton = QtGui.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(710, 360, 75, 25))
        self.pushButton.setObjectName("pushButton")
        self.lineEdit = QtGui.QLineEdit(self.centralwidget)
        self.lineEdit.setGeometry(QtCore.QRect(20, 360, 581, 21))
        self.lineEdit.setObjectName("lineEdit")
        self.pushButton_2 = QtGui.QPushButton(self.centralwidget)
        self.pushButton_2.setGeometry(QtCore.QRect(630, 360, 75, 25))
        self.pushButton_2.setObjectName("pushButton_2")
        self.label = QtGui.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(20, 340, 331, 16))
        self.label.setObjectName("label")
        self.label_2 = QtGui.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(20, 10, 111, 16))
        self.label_2.setObjectName("label_2")
        TextWindowHistory.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(TextWindowHistory)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 795, 20))
        self.menubar.setObjectName("menubar")
        TextWindowHistory.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(TextWindowHistory)
        self.statusbar.setObjectName("statusbar")
        TextWindowHistory.setStatusBar(self.statusbar)

        self.retranslateUi(TextWindowHistory)
        QtCore.QObject.connect(self.pushButton, QtCore.SIGNAL("clicked()"), TextWindowHistory.close)
        QtCore.QMetaObject.connectSlotsByName(TextWindowHistory)

    def retranslateUi(self, TextWindowHistory):
        TextWindowHistory.setWindowTitle(QtGui.QApplication.translate("TextWindowHistory", "File History", None, QtGui.QApplication.UnicodeUTF8))
        self.textBrowser.setToolTip(QtGui.QApplication.translate("TextWindowHistory", "Text display of the current files history", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton.setToolTip(QtGui.QApplication.translate("TextWindowHistory", "Close window", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton.setText(QtGui.QApplication.translate("TextWindowHistory", "Exit", None, QtGui.QApplication.UnicodeUTF8))
        self.lineEdit.setToolTip(QtGui.QApplication.translate("TextWindowHistory", "Copy file path to here", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_2.setToolTip(QtGui.QApplication.translate("TextWindowHistory", "Loads the copied file path if correct type", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_2.setText(QtGui.QApplication.translate("TextWindowHistory", "Load", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("TextWindowHistory", "Copy file path here from history to load:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("TextWindowHistory", "File History", None, QtGui.QApplication.UnicodeUTF8))

