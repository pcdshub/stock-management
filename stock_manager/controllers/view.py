from PyQt6.QtWidgets import QMainWindow
from PyQt6.uic import loadUi


class View(QMainWindow):
	def __init__(self):
		super(View, self).__init__()
		loadUi(r"ui/view.ui")
		for x in self.children():
			print(x.objectName())
