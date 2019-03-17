# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'art.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.setFixedSize(1224, 850)
        self.mainContainer = QtGui.QWidget(MainWindow)
        self.mainContainer.setObjectName(_fromUtf8("mainContainer"))
        self.gridLayout = QtGui.QGridLayout(self.mainContainer)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.figContainer = QtGui.QWidget(self.mainContainer)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.figContainer.sizePolicy().hasHeightForWidth())
        self.figContainer.setSizePolicy(sizePolicy)
        self.figContainer.setObjectName(_fromUtf8("figContainer"))
        self.mplvl = QtGui.QHBoxLayout(self.figContainer)
        self.mplvl.setObjectName(_fromUtf8("mplvl"))
        self.gridLayout.addWidget(self.figContainer, 0, 1, 1, 1)

        self.treeWidget = QtGui.QTreeWidget(self.mainContainer)
        self.treeWidget.setMaximumSize(QtCore.QSize(200, 16777215))
        self.treeWidget.setObjectName(_fromUtf8("treeWidget"))
        self.treeWidget.headerItem().setText(0, _fromUtf8("1"))
        self.gridLayout.addWidget(self.treeWidget, 0, 2, 1, 1)

        self.leftTreeWidget = QtGui.QTreeWidget(self.mainContainer)
        self.leftTreeWidget.setMaximumSize(QtCore.QSize(200, 16777215))
        self.leftTreeWidget.setObjectName(_fromUtf8("leftTreeWidget"))
        self.leftTreeWidget.headerItem().setText(0, _fromUtf8("1"))
        self.gridLayout.addWidget(self.leftTreeWidget, 0, 0, 1, 1)

        MainWindow.setCentralWidget(self.mainContainer)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1024, 25))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menuFile = QtGui.QMenu(self.menubar)
        self.menuFile.setObjectName(_fromUtf8("menuFile"))
        self.menuEdit = QtGui.QMenu(self.menubar)
        self.menuEdit.setObjectName(_fromUtf8("menuEdit"))
        self.menuPresets = QtGui.QMenu(self.menubar)
        self.menuPresets.setObjectName(_fromUtf8("menuPresets"))
        self.menuTrajectoryOrder = QtGui.QMenu(self.menubar)
        self.menuTrajectoryOrder.setObjectName(_fromUtf8("menuTrajectoryOrder"))
        self.deleteLines = QtGui.QMenu(self.menubar)
        self.deleteLines.setObjectName(_fromUtf8("deleteLines"))
        self.menuAbout = QtGui.QMenu(self.menubar)
        self.menuAbout.setObjectName(_fromUtf8("menuAbout"))

        MainWindow.setMenuBar(self.menubar)
        self.about = QtGui.QAction(MainWindow)
        self.about.setObjectName(_fromUtf8("about"))

        self.open = QtGui.QAction(MainWindow)
        self.open.setObjectName(_fromUtf8("open"))
        self.saveAnimation = QtGui.QAction(MainWindow)
        self.saveAnimation.setObjectName(_fromUtf8("Save Animation"))
        self.saveData = QtGui.QAction(MainWindow)
        self.saveData.setObjectName(_fromUtf8("Save Data"))
        self.exit = QtGui.QAction(MainWindow)
        self.exit.setObjectName(_fromUtf8("exit"))

        self.menuFile.addAction(self.open)
        self.menuFile.addAction(self.saveAnimation)
        self.menuFile.addAction(self.saveData)
        self.menuFile.addAction(self.exit)

        self.trainingTimeOrder = QtGui.QAction(MainWindow)
        self.trainingTimeOrder.setObjectName(_fromUtf8("Training Time"))
        self.locationOrder = QtGui.QAction(MainWindow)
        self.locationOrder.setObjectName(_fromUtf8("Location"))
        self.menuTrajectoryOrder.addAction(self.trainingTimeOrder)
        self.menuTrajectoryOrder.addAction(self.locationOrder)

        self.deleteSelectedLine = QtGui.QAction(MainWindow)
        self.deleteSelectedLine.setObjectName(_fromUtf8("Delete Selected Lines"))
        self.deleteUnselectedLine = QtGui.QAction(MainWindow)
        self.deleteUnselectedLine.setObjectName(_fromUtf8("Delete Unselected Lines"))
        self.deleteLines.addAction(self.deleteSelectedLine)
        self.deleteLines.addAction(self.deleteUnselectedLine)

        self.addTitle = QtGui.QAction(MainWindow)
        self.addTitle.setObjectName(_fromUtf8("Add Title"))
        self.selectArea = QtGui.QAction(MainWindow)
        self.selectArea.setObjectName(_fromUtf8("Select Area"))
        self.hideFlag = QtGui.QAction(MainWindow)
        self.hideFlag.setObjectName(_fromUtf8("Hide Flag"))
        self.hideBorder = QtGui.QAction(MainWindow)
        self.hideBorder.setObjectName(_fromUtf8("Hide Border"))
        self.hideAuthors = QtGui.QAction(MainWindow)
        self.hideAuthors.setObjectName(_fromUtf8("Hide Authors"))
        self.backgroundColor = QtGui.QAction(MainWindow)
        self.backgroundColor.setObjectName(_fromUtf8("Background Color"))

        self.menuEdit.addAction(self.addTitle)
        self.menuEdit.addAction(self.selectArea)
        self.menuEdit.addAction(self.hideFlag)
        self.menuEdit.addAction(self.hideBorder)
        self.menuEdit.addAction(self.hideAuthors)
        self.menuEdit.addAction(self.backgroundColor)

        self.colorMenu = self.menuEdit.addMenu("Assign Color")
        self.rainbowColor = QtGui.QAction(MainWindow)
        self.rainbowColor.setObjectName(_fromUtf8("Rainbow Color Set"))
        self.rangeColor = QtGui.QAction(MainWindow)
        self.rangeColor.setObjectName(_fromUtf8("Range Color Set"))
        self.pickColor = QtGui.QAction(MainWindow)
        self.pickColor.setObjectName(_fromUtf8("Pick Color Set"))
        self.colorMenu.addAction(self.rainbowColor)
        self.colorMenu.addAction(self.rangeColor)
        self.colorMenu.addAction(self.pickColor)

        self.menuAbout.addAction(self.about)

        self.savePresets = QtGui.QAction(MainWindow)
        self.savePresets.setObjectName(_fromUtf8("Save"))
        self.storePresets = QtGui.QAction(MainWindow)
        self.storePresets.setObjectName(_fromUtf8("Restore"))

        self.menuPresets.addAction(self.savePresets)
        self.menuPresets.addAction(self.storePresets)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())
        self.menubar.addAction(self.menuPresets.menuAction())
        self.menubar.addAction(self.menuTrajectoryOrder.menuAction())
        self.menubar.addAction(self.deleteLines.menuAction())
        self.menubar.addAction(self.menuAbout.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "RL Visualizer", None))
        self.menuFile.setTitle(_translate("MainWindow", "File", None))
        self.menuEdit.setTitle(_translate("MainWindow", "Edit", None))
        self.menuPresets.setTitle(_translate("MainWindow", "Presets", None))
        self.menuAbout.setTitle(_translate("MainWindow", "Help", None))
        self.menuTrajectoryOrder.setTitle(_translate("MainWindow", "Trajectory Order", None))
        self.deleteLines.setTitle(_translate("MainWindow", "Delete Lines", None))
        self.about.setText(_translate("MainWindow", "About", None))
        self.open.setText(_translate("MainWindow", "Open", None))
        self.saveAnimation.setText(_translate("MainWindow", "Save Animation", None))
        self.saveData.setText(_translate("MainWindow", "Save Data", None))
        self.addTitle.setText(_translate("MainWindow", "Add Title", None))
        self.selectArea.setText(_translate("MainWindow", "Select Area", None))
        self.hideFlag.setText(_translate("MainWindow", "Hide Flag", None))
        self.hideBorder.setText(_translate("MainWindow", "Hide Border", None))
        self.hideAuthors.setText(_translate("MainWindow", "Hide Authors", None))
        self.backgroundColor.setText(_translate("MainWindow", "Background Color", None))
        self.rainbowColor.setText(_translate("MainWindow", "Rainbow Color Set", None))
        self.rangeColor.setText(_translate("MainWindow", "Range Color Set", None))
        self.pickColor.setText(_translate("MainWindow", "Pick Color Set (one-by-one)", None))
        self.exit.setText(_translate("MainWindow", "Exit", None))
        self.savePresets.setText(_translate("MainWindow", "Save", None))
        self.storePresets.setText(_translate("MainWindow", "Restore", None))
        self.locationOrder.setText(_translate("MainWindow", "Location Order", None))
        self.trainingTimeOrder.setText(_translate("MainWindow", "Training Time", None))
        self.deleteSelectedLine.setText(_translate("MainWindow", "Delete Selected Lines", None))
        self.deleteUnselectedLine.setText(_translate("MainWindow", "Delete Unselected Lines", None))