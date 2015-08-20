# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'textdisplay.ui'
#
# Created: Tue Aug 18 12:42:25 2015
#      by: pyside-uic 0.2.15 running on PySide 1.2.1
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_TextWindow(object):
    def setupUi(self, TextWindow):
        TextWindow.setObjectName("TextWindow")
        TextWindow.resize(795, 426)
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

