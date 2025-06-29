from pathlib import Path

from PyQt6.QtGui import QCloseEvent
from PyQt6.QtWidgets import QMainWindow
from PyQt6.uic import loadUi


class App(QMainWindow):
	"""
	Main application window for SLAC Inventory Management.
	
	Handles UI loading, screen transitions, and application startup/shutdown events.
	"""
	
	def __init__(self):
		"""Initialize the main application window and setup screens."""
		from stock_manager.controllers import View, Scanner
		from stock_manager.utils import Logger
		super(App, self).__init__()
		self.log = Logger()
		
		try:
			ui_path = Path(__file__).resolve().parent.parent / 'ui' / 'main.ui'
			loadUi(str(ui_path), self)
		except Exception as e:
			self.log.error_log(f"Failed to load main UI file: {e}")
			raise SystemExit
		
		self._view: View = View(self)
		self._qr: Scanner = Scanner(self)
		self.screens.addWidget(self._view)
		self.screens.addWidget(self._qr)
		self.screens.currentChanged.connect(self._on_page_changed)
	
	def run(self) -> None:
		"""Start the application, show the initial screen, log app startup."""
		self.log.info_log("App Started")
		self.screens.setCurrentIndex(0)
		self._on_page_changed()
	
	def _on_page_changed(self) -> None:
		"""Update window title and manage QR scanner based on current screen."""
		title = {0: "View", 1: "QR Scanner"}.get(self.screens.currentIndex(), "ERROR")
		base = " | SLAC Inventory Management Application"
		self.setWindowTitle(title + base)
		
		if self.screens.currentIndex() == 1:
			try:
				self._qr.start_video()
			except Exception as e:
				self.log.error_log(f"Failed to start QR scanner: {e}")
		else:
			try:
				self._qr.stop_video()
			except Exception as e:
				self.log.error_log(f"Failed to stop QR scanner: {e}")
	
	def closeEvent(self, event: QCloseEvent) -> None:
		"""Handle the application close event and log exit."""
		self.log.info_log("App Exited")
		super().closeEvent(event)
