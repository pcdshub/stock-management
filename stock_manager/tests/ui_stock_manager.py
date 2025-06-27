# -*- coding: utf-8 -*-
import PySide6
################################################################################
## Form generated from reading UI file 'stock_managerErWIcv.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


class Ui_MainWindow(object):
	def setupUi(self):
		MainWindow = QMainWindow()
		if not MainWindow.objectName():
			MainWindow.setObjectName(u"MainWindow")
		MainWindow.setWindowModality(Qt.WindowModality.NonModal)
		MainWindow.resize(1017, 800)
		icon = QIcon()
		icon.addFile(u"../../bin/images/slac_logo.jpg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
		MainWindow.setWindowIcon(icon)
		MainWindow.setStyleSheet(u"")
		self.centralwidget = QWidget(MainWindow)
		self.centralwidget.setObjectName(u"centralwidget")
		self.screens = QStackedWidget(self.centralwidget)
		self.screens.setObjectName(u"screens")
		self.screens.setGeometry(QRect(140, 0, 871, 751))
		self.page = QWidget()
		self.page.setObjectName(u"page")
		self.label = QLabel(self.page)
		self.label.setObjectName(u"label")
		self.label.setGeometry(QRect(20, 20, 221, 31))
		font = QFont()
		font.setPointSize(20)
		self.label.setFont(font)
		self.tableWidget = QTableWidget(self.page)
		if self.tableWidget.columnCount() < 8:
			self.tableWidget.setColumnCount(8)
		__qtablewidgetitem = QTableWidgetItem()
		self.tableWidget.setHorizontalHeaderItem(0, __qtablewidgetitem)
		__qtablewidgetitem1 = QTableWidgetItem()
		self.tableWidget.setHorizontalHeaderItem(1, __qtablewidgetitem1)
		__qtablewidgetitem2 = QTableWidgetItem()
		self.tableWidget.setHorizontalHeaderItem(2, __qtablewidgetitem2)
		__qtablewidgetitem3 = QTableWidgetItem()
		self.tableWidget.setHorizontalHeaderItem(3, __qtablewidgetitem3)
		__qtablewidgetitem4 = QTableWidgetItem()
		self.tableWidget.setHorizontalHeaderItem(4, __qtablewidgetitem4)
		__qtablewidgetitem5 = QTableWidgetItem()
		self.tableWidget.setHorizontalHeaderItem(5, __qtablewidgetitem5)
		__qtablewidgetitem6 = QTableWidgetItem()
		self.tableWidget.setHorizontalHeaderItem(6, __qtablewidgetitem6)
		__qtablewidgetitem7 = QTableWidgetItem()
		self.tableWidget.setHorizontalHeaderItem(7, __qtablewidgetitem7)
		self.tableWidget.setObjectName(u"tableWidget")
		self.tableWidget.setGeometry(QRect(10, 70, 861, 681))
		self.search_lineEdit = QLineEdit(self.page)
		self.search_lineEdit.setObjectName(u"search_lineEdit")
		self.search_lineEdit.setGeometry(QRect(662, 31, 201, 31))
		self.search_lineEdit.setStyleSheet(u"#search_lineEdit {\n"
										   "border: 1px solid black;\n"
										   "border-radius: 15px;\n"
										   "padding-left: 5%;\n"
										   "}")
		self.screens.addWidget(self.page)
		self.page_2 = QWidget()
		self.page_2.setObjectName(u"page_2")
		self.label_2 = QLabel(self.page_2)
		self.label_2.setObjectName(u"label_2")
		self.label_2.setGeometry(QRect(390, 200, 55, 16))
		self.screens.addWidget(self.page_2)
		self.sideUI = QWidget(self.centralwidget)
		self.sideUI.setObjectName(u"sideUI")
		self.sideUI.setGeometry(QRect(0, 0, 140, 771))
		self.sideUI.setStyleSheet(u"#sideUI {\n"
								  "	background-color: rgb(170, 0, 0);\n"
								  "}")
		self.verticalLayoutWidget = QWidget(self.sideUI)
		self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget")
		self.verticalLayoutWidget.setGeometry(QRect(0, 100, 141, 591))
		self.vertical_box = QVBoxLayout(self.verticalLayoutWidget)
		self.vertical_box.setObjectName(u"vertical_box")
		self.vertical_box.setContentsMargins(0, 0, 0, 0)
		self.view_btn = QPushButton(self.verticalLayoutWidget)
		self.view_btn.setObjectName(u"view_btn")
		font1 = QFont()
		font1.setPointSize(14)
		font1.setBold(False)
		font1.setWeight(PySide6.QtGui.QFont.Weight.Bold)
		self.view_btn.setFont(font1)
		self.view_btn.setStyleSheet(u"border-radius: 15;")
		
		self.vertical_box.addWidget(self.view_btn)
		
		self.add_btn = QPushButton(self.verticalLayoutWidget)
		self.add_btn.setObjectName(u"add_btn")
		self.add_btn.setFont(font1)
		self.add_btn.setStyleSheet(u"border-radius: 15;")
		
		self.vertical_box.addWidget(self.add_btn)
		
		self.edit_btn = QPushButton(self.verticalLayoutWidget)
		self.edit_btn.setObjectName(u"edit_btn")
		self.edit_btn.setFont(font1)
		self.edit_btn.setStyleSheet(u"border-radius: 15;")
		
		self.vertical_box.addWidget(self.edit_btn)
		
		self.remove_btn = QPushButton(self.verticalLayoutWidget)
		self.remove_btn.setObjectName(u"remove_btn")
		self.remove_btn.setFont(font1)
		self.remove_btn.setStyleSheet(u"border-radius: 15;")
		
		self.vertical_box.addWidget(self.remove_btn)
		
		self.exit_btn = QPushButton(self.verticalLayoutWidget)
		self.exit_btn.setObjectName(u"exit_btn")
		self.exit_btn.setFont(font1)
		self.exit_btn.setStyleSheet(u"border-radius: 15;")
		
		self.vertical_box.addWidget(self.exit_btn)
		
		MainWindow.setCentralWidget(self.centralwidget)
		self.menubar = QMenuBar(MainWindow)
		self.menubar.setObjectName(u"menubar")
		self.menubar.setGeometry(QRect(0, 0, 1017, 26))
		MainWindow.setMenuBar(self.menubar)
		self.statusbar = QStatusBar(MainWindow)
		self.statusbar.setObjectName(u"statusbar")
		MainWindow.setStatusBar(self.statusbar)
		
		self.retranslateUi(MainWindow)
		
		self.screens.setCurrentIndex(0)
		
		QMetaObject.connectSlotsByName(MainWindow)
	
	# setupUi
	
	def retranslateUi(self, MainWindow):
		MainWindow.setWindowTitle(
				QCoreApplication.translate("MainWindow", u"PAGE | SLAC Inventory Management Application", None))
		self.label.setText(QCoreApplication.translate("MainWindow", u"View All Items:", None))
		___qtablewidgetitem = self.tableWidget.horizontalHeaderItem(0)
		___qtablewidgetitem.setText(QCoreApplication.translate("MainWindow", u"Part #", None))
		___qtablewidgetitem1 = self.tableWidget.horizontalHeaderItem(1)
		___qtablewidgetitem1.setText(QCoreApplication.translate("MainWindow", u"Minimum", None))
		___qtablewidgetitem2 = self.tableWidget.horizontalHeaderItem(2)
		___qtablewidgetitem2.setText(QCoreApplication.translate("MainWindow", u"Total", None))
		___qtablewidgetitem3 = self.tableWidget.horizontalHeaderItem(3)
		___qtablewidgetitem3.setText(QCoreApplication.translate("MainWindow", u"B750 Stock", None))
		___qtablewidgetitem4 = self.tableWidget.horizontalHeaderItem(4)
		___qtablewidgetitem4.setText(QCoreApplication.translate("MainWindow", u"B757 Stock", None))
		___qtablewidgetitem5 = self.tableWidget.horizontalHeaderItem(5)
		___qtablewidgetitem5.setText(QCoreApplication.translate("MainWindow", u"Excess", None))
		___qtablewidgetitem6 = self.tableWidget.horizontalHeaderItem(6)
		___qtablewidgetitem6.setText(QCoreApplication.translate("MainWindow", u"Description", None))
		___qtablewidgetitem7 = self.tableWidget.horizontalHeaderItem(7)
		___qtablewidgetitem7.setText(QCoreApplication.translate("MainWindow", u"Manufacturer", None))
		self.search_lineEdit.setText(QCoreApplication.translate("MainWindow", u"Search...", None))
		self.label_2.setText(QCoreApplication.translate("MainWindow", u"page 2", None))
		self.view_btn.setText(QCoreApplication.translate("MainWindow", u"View", None))
		self.add_btn.setText(QCoreApplication.translate("MainWindow", u"Add", None))
		self.edit_btn.setText(QCoreApplication.translate("MainWindow", u"Edit", None))
		self.remove_btn.setText(QCoreApplication.translate("MainWindow", u"Remove", None))
		self.exit_btn.setText(QCoreApplication.translate("MainWindow", u"Exit", None))  # retranslateUi
