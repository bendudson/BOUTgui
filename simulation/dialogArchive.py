# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dialogArchive.ui'
#
# Created: Tue Aug  4 09:30:46 2015
#      by: pyside-uic 0.2.15 running on PySide 1.2.1
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_dialogArchive(object):
    def setupUi(self, dialogArchive):
        dialogArchive.setObjectName("dialogArchive")
        dialogArchive.resize(313, 93)
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

