# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '../dialogSimulation.ui'
#
# Created: Mon Aug 17 16:20:29 2015
#      by: pyside-uic 0.2.15 running on PySide 1.2.1
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_dialogSimulation(object):
    def setupUi(self, dialogSimulation):
        dialogSimulation.setObjectName("dialogSimulation")
        dialogSimulation.resize(312, 93)
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

