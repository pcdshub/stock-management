import sys

from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PyQt6.uic import loadUi

from ui_stock_manager import Ui_MainWindow


class App(QMainWindow, Ui_MainWindow):
	def __init__(self):
		super(App, self).__init__()
		loadUi("ui/stock_manager.ui", self)
		
		for x in self.children():
			print(x.objectName())
			
		self.view_btn.clicked.connect(self.change_screens(self.view_btn))
		self.add_btn.clicked.connect(self.change_screens(self.add_btn))
	
	def change_screens(self, src):
		print(self.screens.currentIndex())
		match src:
			case self.view_btn:
				self.screens.setCurrentIndex(0)
			case self.add_btn:
				self.screens.setCurrentIndex(1)
		# print(self.screens.currentIndex())
		# self.screens.setCurrentIndex(param)
		# print(self.screens.currentIndex())


if __name__ == '__main__':
	app = QApplication(sys.argv)
	ui = App()
	ui.show()
	app.exec()
