from PyQt6.QtWidgets import QMainWindow
from PyQt6.uic import loadUi


class App(QMainWindow):
	def __init__(self):
		from controllers import View, Scanner
		from utils import Logger
		super(App, self).__init__()
		self.log = Logger()
		loadUi('ui/main.ui', self)
		self._view: View = View(self)
		self._qr: Scanner = Scanner(self)
		self.screens.addWidget(self._view)
		self.screens.addWidget(self._qr)
		self.screens.currentChanged.connect(self._on_page_changed)
	
	def run(self):
		self.log.info_log("App Started")
		self.screens.setCurrentIndex(0)
		self._on_page_changed()
		
	def _on_page_changed(self):
		title = {0: "View", 1: "QR Scanner"}.get(self.screens.currentIndex(), "ERROR")
		base = " | SLAC Inventory Management Application"
		self.setWindowTitle(title + base)
		if self.screens.currentIndex() == 1:
			self._qr.start_video()
		else:
			self._qr.stop_video()
	
	def closeEvent(self, event):
		self.log.info_log("App Exited")
		super().closeEvent(event)
