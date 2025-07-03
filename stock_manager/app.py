"""
Instantiate and run the App class to start the SLAC Inventory Management application.
"""

from pathlib import Path

from PyQt6.QtGui import QCloseEvent
from PyQt6.QtWidgets import QMainWindow
from PyQt6.uic import loadUi

from stock_manager.controllers import Export
from stock_manager.model.item import Item
from stock_manager.utils.database import DBUtils


class App(QMainWindow):
	"""
	Main application window for SLAC Inventory Management.
	
	Handles UI loading, screen transitions, and application startup/shutdown events.
	"""
	
	def __init__(self):
		"""Initialize the main application window and setup screens."""
		from stock_manager.controllers import View, Scanner, Finish
		from stock_manager.utils import Logger
		super(App, self).__init__()
		self.log = Logger()
		self.db = DBUtils()
		self.all_items: list[Item] = []
		
		try:
			ui_path = Path(__file__).resolve().parent.parent / 'ui' / 'main.ui'
			loadUi(str(ui_path), self)
		except Exception as e:
			self.log.error_log(f"Failed to load main UI file: {e}")
			raise SystemExit
		
		try:
			gs_data: list[dict[str, int | float | str]] = self.db.get_all_data()
			self._create_all_items(gs_data)
		except Exception as e:
			self.log.error_log(f"Could not load data from database: {e}")
		
		self._view: View = View(self)
		self._qr: Scanner = Scanner(self)
		self._export = Export(self)
		self.success = Finish(self)
		self.screens.addWidget(self._view)
		self.screens.addWidget(self._export)
		self.screens.addWidget(self._qr)
		self.screens.addWidget(self.success)
		self.screens.currentChanged.connect(self._on_page_changed)
	
	def run(self) -> None:
		"""Start the application, show the initial screen, log app startup."""
		self.log.info_log("App Started")
		self.screens.setCurrentIndex(0)
		self._on_page_changed()
	
	def _on_page_changed(self) -> None:
		"""Update window title and manage QR scanner based on current screen."""
		title = {0: "View", 1: 'Export', 2: "QR Scanner", 3: 'Finished'}.get(self.screens.currentIndex(), "ERROR")
		base = " | SLAC Inventory Management Application"
		self.setWindowTitle(title + base)
		
		if self.screens.currentIndex() == 2:
			try:
				self._qr.start_video()
			except Exception as e:
				self.log.error_log(f"Failed to start QR scanner: {e}")
		else:
			try:
				self._qr.stop_video()
			except Exception as e:
				self.log.error_log(f"Failed to stop QR scanner: {e}")
	
	def _create_all_items(self, items: list[dict[str, int | float | str]]):
		for item in items:
			vals = list(item.values())
			for i, val in enumerate(vals):
				if val == '':
					vals[i] = None
			
			self.all_items.append(Item(
					part_num=vals[0],
					manufacturer=vals[1],
					description=vals[2],
					total=vals[3],
					stock_b750=vals[4],
					stock_b757=vals[5],
					minimum=vals[6],
					excess=vals[7],
					minimum_sallie=vals[8]
			))
	
	def closeEvent(self, event: QCloseEvent) -> None:
		"""Handle the application close event and log exit."""
		self.log.info_log("App Exited\n")
		super().closeEvent(event)
	
	def update_tables(self):
		self._view.update_table(self.all_items)
		# TODO: add more tables
