# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/lang/Desktop/des.ui'
#
# Created by: PyQt5 UI code generator 5.7
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_descbc(object):
    def setupUi(self, descbc):
        descbc.setObjectName("descbc")
        descbc.resize(543, 443)
        self.sure = QtWidgets.QPushButton(descbc)
        self.sure.setGeometry(QtCore.QRect(390, 110, 71, 61))
        self.sure.setObjectName("sure")
        self.label = QtWidgets.QLabel(descbc)
        self.label.setGeometry(QtCore.QRect(40, 30, 64, 18))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(descbc)
        self.label_2.setGeometry(QtCore.QRect(40, 100, 31, 18))
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(descbc)
        self.label_3.setGeometry(QtCore.QRect(40, 160, 21, 18))
        self.label_3.setObjectName("label_3")
        self.decod = QtWidgets.QLabel(descbc)
        self.decod.setGeometry(QtCore.QRect(10, 280, 71, 51))
        self.decod.setObjectName("decod")
        self.decoding = QtWidgets.QTextBrowser(descbc)
        self.decoding.setGeometry(QtCore.QRect(90, 220, 411, 211))
        self.decoding.setObjectName("decoding")
        self.mingwen = QtWidgets.QLineEdit(descbc)
        self.mingwen.setGeometry(QtCore.QRect(90, 20, 411, 41))
        self.mingwen.setObjectName("mingwen")
        self.key = QtWidgets.QLineEdit(descbc)
        self.key.setGeometry(QtCore.QRect(90, 90, 191, 41))
        self.key.setObjectName("key")
        self.VI = QtWidgets.QLineEdit(descbc)
        self.VI.setGeometry(QtCore.QRect(90, 150, 191, 41))
        self.VI.setObjectName("VI")

        self.retranslateUi(descbc)
        QtCore.QMetaObject.connectSlotsByName(descbc)

    def retranslateUi(self, descbc):
        _translate = QtCore.QCoreApplication.translate
        palette=QtGui.QPalette()
        icon=QtGui.QPixmap('1.jpg')
        palette.setBrush(self.backgroundRole(), QtGui.QBrush(icon)) #添加背景图片
        self.setPalette(palette)
        descbc.setWindowTitle(_translate("descbc", "des-cbc"))
        self.sure.setText(_translate("descbc", "运行"))
        self.label.setText(_translate("descbc", "明文"))
        self.label_2.setText(_translate("descbc", "key"))
        self.label_3.setText(_translate("descbc", "VI"))
        self.decod.setText(_translate("descbc", "解密过程"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    descbc = QtWidgets.QDialog()
    ui = Ui_descbc()
    ui.setupUi(descbc)
    descbc.show()
    sys.exit(app.exec_())

