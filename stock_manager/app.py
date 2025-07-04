"""
Instantiate and run the App class to start the SLAC Inventory Management application.
"""

from pathlib import Path

from PyQt6.QtGui import QCloseEvent
from PyQt6.QtWidgets import QMainWindow
from PyQt6.uic import loadUi

import stock_manager.controllers
from stock_manager.controllers import Edit, Export, Finish, Scanner, View
from stock_manager.model.item import Item
from stock_manager.utils import DBUtils, Logger


class App(QMainWindow):
	"""
	Main application window for SLAC Inventory Management.
	
	Handles UI loading, screen transitions, and application startup/shutdown events.
	"""
	
	def __init__(self):
		"""Initialize the main application window and setup screens."""
		
		super(App, self).__init__()
		self.log = Logger()
		self.db = DBUtils()
		
		try:
			ui_path = Path(__file__).resolve().parent.parent / 'ui' / 'main.ui'
			loadUi(str(ui_path), self)
		except Exception as e:
			self.log.error_log(f"Failed to load main UI file: {e}")
			raise SystemExit
		
		try:
			gs_data: list[dict[str, int | float | str]] = self.db.get_all_data()
			self.all_items = self._create_all_items(gs_data)
		except Exception as e:
			self.log.error_log(f"Could not load data from database: {e}")
		
		self._view: View = View(self)
		self._qr: Scanner = Scanner(self)
		self._export = Export(self)
		self.success = Finish(self)
		self._edit = Edit(self)
		self.screens.addWidget(self._view)
		self.screens.addWidget(self._export)
		self.screens.addWidget(self._qr)
		self.screens.addWidget(self.success)
		self.screens.addWidget(self._edit)
		self.screens.currentChanged.connect(self._on_page_changed)
	
	def run(self) -> None:
		"""Start the application, show the initial screen, log app startup."""
		
		self.log.info_log("App Started")
		self.screens.setCurrentIndex(0)
		self._on_page_changed()
	
	def _on_page_changed(self) -> None:
		"""Update window title and manage QR scanner based on current screen."""
		
		title = {
			0: "View",
			1: 'Export',
			2: "QR Scanner",
			3: 'Finished',
			4: 'Edit'
		}.get(self.screens.currentIndex(), "ERROR")
		self.setWindowTitle(title + " | SLAC Inventory Management Application")
		
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
	
	@staticmethod
	def _create_all_items(gs_items: list[dict[str, int | float | str]]) -> list[Item]:
		"""
		Creates and populates the internal list of all inventory items from the data source.
		
		This method parses raw data and instantiates Item objects accordingly.
		"""
		
		obj_items: list[Item] = []
		for item in gs_items:
			vals: list[int | float | str | None] = [None if val == '' else val for val in list(item.values())]
			obj_items.append(Item(*vals))
		return obj_items
	
	def closeEvent(self, event: QCloseEvent) -> None:
		"""Handle the application close event and log exit."""
		
		self.log.info_log("App Exited\n")
		super().closeEvent(event)
	
	def update_tables(self) -> None:
		"""
		Refreshes or updates the displayed tables in the UI to reflect the latest inventory data.
		
		This method should be called after making changes to the inventory or data source.
		"""
		
		controller: stock_manager.controllers.AbstractController
		for controller in [self._view, self._edit]:
			controller.update_table(self.all_items, controller.table)
