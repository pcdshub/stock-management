import sys

from PyQt6.QtCore import QCoreApplication
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton
from PyQt6.uic import loadUi

from utils.logger import Logger


class App(QMainWindow):
	def __init__(self):
		super(App, self).__init__()
		self._log = Logger()
		self._log.info_log("App Started")
		loadUi("ui/stock_manager.ui", self)
		self._handle_side_ui()
		self._change_screens(self.view_btn)
	
	def _handle_side_ui(self):
		self.view_btn.clicked.connect(lambda: self._change_screens(self.view_btn))
		self.qr_btn.clicked.connect(lambda: self._change_screens(self.qr_btn))
		self.edit_btn.clicked.connect(lambda: self._change_screens(self.edit_btn))
		self.remove_btn.clicked.connect(lambda: self._change_screens(self.remove_btn))
		self.exit_btn.clicked.connect(QCoreApplication.quit)
	
	def _change_screens(self, src: QPushButton):
		title = ' | SLAC Inventory Management Application'
		buttons: list[QPushButton] = [self.view_btn, self.qr_btn, self.edit_btn, self.remove_btn]
		
		for i, btn in enumerate(buttons):
			if src == btn:
				self.screens.setCurrentIndex(i)
				self.setWindowTitle(btn.text() + title)
				font = src.font()
				font.setBold(True)
				src.setFont(font)
			else:
				font = btn.font()
				font.setBold(False)
				btn.setFont(font)
	
	def closeEvent(self, event):
		self._log.info_log("App Exited")
		super().closeEvent(event)


def main():
	app = QApplication([])
	# app = QApplication(sys.argv)
	window = App()
	window.show()
	sys.exit(app.exec())


if __name__ == '__main__':
	main()
