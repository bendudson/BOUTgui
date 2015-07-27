# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './oldfiles/dialogcompare.ui'
#
# Created: Thu Jul  9 13:28:11 2015
#      by: pyside-uic 0.2.15 running on PySide 1.2.1
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_Dialogcompare(object):
    def setupUi(self, Dialogcompare):
        Dialogcompare.setObjectName("Dialogcompare")
        Dialogcompare.resize(284, 99)
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

