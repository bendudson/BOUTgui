# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './oldfiles/textdisplayhistory.ui'
#
# Created: Fri Jul 10 10:18:01 2015
#      by: pyside-uic 0.2.15 running on PySide 1.2.1
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_TextWindowHistory(object):
    def setupUi(self, TextWindowHistory):
        TextWindowHistory.setObjectName("TextWindowHistory")
        TextWindowHistory.resize(795, 426)
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
        TextWindowHistory.setWindowTitle(QtGui.QApplication.translate("TextWindowHistory", "MainWindow", None, QtGui.QApplication.UnicodeUTF8))
        self.textBrowser.setToolTip(QtGui.QApplication.translate("TextWindowHistory", "Text display of the current files history", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton.setToolTip(QtGui.QApplication.translate("TextWindowHistory", "Close window", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton.setText(QtGui.QApplication.translate("TextWindowHistory", "Exit", None, QtGui.QApplication.UnicodeUTF8))
        self.lineEdit.setToolTip(QtGui.QApplication.translate("TextWindowHistory", "Copy file path to here", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_2.setToolTip(QtGui.QApplication.translate("TextWindowHistory", "Loads the copied file path if correct type", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_2.setText(QtGui.QApplication.translate("TextWindowHistory", "Load", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("TextWindowHistory", "Copy file path here from history to load:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("TextWindowHistory", "File History", None, QtGui.QApplication.UnicodeUTF8))

