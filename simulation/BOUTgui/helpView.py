# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'helpView.ui'
#
# Created: Tue Aug  4 14:29:13 2015
#      by: pyside-uic 0.2.15 running on PySide 1.2.1
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_helpViewer(object):
    def setupUi(self, helpViewer):
        helpViewer.setObjectName("helpViewer")
        helpViewer.resize(1351, 701)
        self.centralwidget = QtGui.QWidget(helpViewer)
        self.centralwidget.setObjectName("centralwidget")
        self.pushButton = QtGui.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(1260, 630, 75, 25))
        self.pushButton.setObjectName("pushButton")
        self.textBrowser = QtGui.QTextEdit(self.centralwidget)
        self.textBrowser.setGeometry(QtCore.QRect(10, 10, 1331, 611))
        self.textBrowser.setObjectName("textBrowser")
        helpViewer.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(helpViewer)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1351, 20))
        self.menubar.setObjectName("menubar")
        helpViewer.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(helpViewer)
        self.statusbar.setObjectName("statusbar")
        helpViewer.setStatusBar(self.statusbar)

        self.retranslateUi(helpViewer)
        QtCore.QObject.connect(self.pushButton, QtCore.SIGNAL("clicked()"), helpViewer.close)
        QtCore.QMetaObject.connectSlotsByName(helpViewer)

    def retranslateUi(self, helpViewer):
        helpViewer.setWindowTitle(QtGui.QApplication.translate("helpViewer", "MainWindow", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton.setText(QtGui.QApplication.translate("helpViewer", "Exit", None, QtGui.QApplication.UnicodeUTF8))

