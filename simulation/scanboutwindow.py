# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'scanbout.ui'
#
# Created: Thu Jul 23 09:50:19 2015
#      by: pyside-uic 0.2.15 running on PySide 1.2.1
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_ScanDialog(object):
    def setupUi(self, ScanDialog):
        ScanDialog.setObjectName("ScanDialog")
        ScanDialog.resize(372, 186)
        self.sectionCombo = QtGui.QComboBox(ScanDialog)
        self.sectionCombo.setGeometry(QtCore.QRect(30, 40, 151, 22))
        self.sectionCombo.setObjectName("sectionCombo")
        self.indexCombo = QtGui.QComboBox(ScanDialog)
        self.indexCombo.setGeometry(QtCore.QRect(190, 40, 151, 22))
        self.indexCombo.setObjectName("indexCombo")
        self.label = QtGui.QLabel(ScanDialog)
        self.label.setGeometry(QtCore.QRect(30, 20, 56, 15))
        self.label.setObjectName("label")
        self.label_2 = QtGui.QLabel(ScanDialog)
        self.label_2.setGeometry(QtCore.QRect(190, 20, 56, 15))
        self.label_2.setObjectName("label_2")
        self.initialLine = QtGui.QLineEdit(ScanDialog)
        self.initialLine.setGeometry(QtCore.QRect(30, 100, 81, 21))
        self.initialLine.setObjectName("initialLine")
        self.finalLine = QtGui.QLineEdit(ScanDialog)
        self.finalLine.setGeometry(QtCore.QRect(144, 100, 81, 21))
        self.finalLine.setObjectName("finalLine")
        self.label_3 = QtGui.QLabel(ScanDialog)
        self.label_3.setGeometry(QtCore.QRect(30, 80, 81, 16))
        self.label_3.setObjectName("label_3")
        self.label_4 = QtGui.QLabel(ScanDialog)
        self.label_4.setGeometry(QtCore.QRect(144, 80, 71, 16))
        self.label_4.setObjectName("label_4")
        self.label_5 = QtGui.QLabel(ScanDialog)
        self.label_5.setGeometry(QtCore.QRect(260, 80, 81, 16))
        self.label_5.setObjectName("label_5")
        self.pushButton = QtGui.QPushButton(ScanDialog)
        self.pushButton.setGeometry(QtCore.QRect(200, 150, 75, 25))
        self.pushButton.setObjectName("pushButton")
        self.pushButton_2 = QtGui.QPushButton(ScanDialog)
        self.pushButton_2.setGeometry(QtCore.QRect(280, 150, 75, 25))
        self.pushButton_2.setObjectName("pushButton_2")
        self.incrementLine = QtGui.QLineEdit(ScanDialog)
        self.incrementLine.setGeometry(QtCore.QRect(260, 100, 81, 21))
        self.incrementLine.setObjectName("incrementLine")
        self.checkBox = QtGui.QCheckBox(ScanDialog)
        self.checkBox.setGeometry(QtCore.QRect(110, 150, 84, 20))
        self.checkBox.setObjectName("checkBox")

        self.retranslateUi(ScanDialog)
        QtCore.QMetaObject.connectSlotsByName(ScanDialog)

    def retranslateUi(self, ScanDialog):
        ScanDialog.setWindowTitle(QtGui.QApplication.translate("ScanDialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("ScanDialog", "Section", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("ScanDialog", "Index", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("ScanDialog", "Initial Value", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("ScanDialog", "Final Value", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("ScanDialog", "Increment", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton.setText(QtGui.QApplication.translate("ScanDialog", "Scan", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_2.setText(QtGui.QApplication.translate("ScanDialog", "Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox.setToolTip(QtGui.QApplication.translate("ScanDialog", "If this is checked then each subsequent run will use the restart files from the previous run", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox.setText(QtGui.QApplication.translate("ScanDialog", "Restart ", None, QtGui.QApplication.UnicodeUTF8))

