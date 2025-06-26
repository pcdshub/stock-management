import sys

from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.uic import loadUi


class App(QMainWindow):
	def __init__(self):
		super(App, self).__init__()
		loadUi("ui/stock_manager.ui", self)
		# self._handle_side_ui()
		
		self.view_btn.clicked.connect(lambda: self._change_screens(self.view_btn))
		self.add_btn.clicked.connect(lambda: self._change_screens(self.add_btn))
		self.edit_btn.clicked.connect(lambda: self._change_screens(self.edit_btn))
		self.remove_btn.clicked.connect(lambda: self._change_screens(self.remove_btn))
		self.exit_btn.clicked.connect(lambda: sys.exit())
	
	def _handle_side_ui(self):
		pass
	
	def _change_screens(self, src):
		print(src)
		print(src in [self.view_btn, self.add_btn, self.edit_btn, self.remove_btn])
		return
		
		title = ' | SLAC Inventory Management Application'
		match src:
			case self.view_btn:
				self.screens.setCurrentIndex(0)
				self.MainWindow.setWindowTitle('View' + title)
			case self.add_btn:
				self.screens.setCurrentIndex(1)
				self.MainWindow.setWindowTitle('Add' + title)
			case self.edit_btn:
				self.screens.setCurrentIndex(2)
				self.MainWindow.setWindowTitle('Edit' + title)
			case self.remove_btn:
				self.screens.setCurrentIndex(3)
				self.MainWindow.setWindowTitle('Remove' + title)
			case _:
				print(src)
			# case self.exit_btn:
			# 	sys.exit()
			

def main():
	app = QApplication([])
	# app = QApplication(sys.argv)
	window = App()
	window.show()
	sys.exit(app.exec())


if __name__ == '__main__':
	main()
