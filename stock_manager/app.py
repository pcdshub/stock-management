"""
Instantiate and run the App class to start the SLAC Inventory Management application.
"""

from pathlib import Path

from PyQt6.QtCore import QCoreApplication
from PyQt6.QtGui import QCloseEvent, QFont
from PyQt6.QtWidgets import QMainWindow, QPushButton
from PyQt6.uic import loadUi

import stock_manager
from stock_manager.model import Item


class App(QMainWindow):
	"""
	Main application window for SLAC Inventory Management.
	
	Handles UI loading, screen transitions, and application startup/shutdown events.
	"""
	
	def __init__(self):
		"""Initialize the main application window and setup screens."""
		
		from stock_manager import DBUtils, Logger
		
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
		
		self._handle_screens()
		self._handle_side_ui()
	
	def run(self) -> None:
		"""Start the application, show the initial screen, log app startup."""
		
		self.log.info_log("App Started")
		self.screens.setCurrentIndex(0)
		self._on_page_changed()
	
	def _on_page_changed(self) -> None:
		"""Update window title and manage QR scanner based on current screen."""
		
		from stock_manager import SIDEBAR_BUTTON_SIZE, PAGE_NAMES
		
		idx = self.screens.currentIndex()
		
		self.setWindowTitle(PAGE_NAMES[idx] + " | SLAC Inventory Management Application")
		
		if idx == 1:
			try:
				self._qr.start_video()
			except Exception as e:
				self.log.error_log(f"Failed to start QR scanner: {e}")
		else:
			try:
				self._qr.stop_video()
			except Exception as e:
				self.log.error_log(f"Failed to stop QR scanner: {e}")
		
		buttons: list[QPushButton] = self.sideUI.children()[1:]  # exclude QVBox
		
		active = QFont()
		active.setPointSize(SIDEBAR_BUTTON_SIZE)
		active.setBold(True)
		inactive = QFont()
		inactive.setPointSize(SIDEBAR_BUTTON_SIZE)
		
		i: int
		button: QPushButton
		for i, button in enumerate(buttons):
			button.setFont(active if i == idx else inactive)
	
	def _handle_screens(self) -> None:
		from stock_manager import Edit, Export, Finish, Remove, Scanner, View, Add
		
		self.screens.addWidget(View(self))
		self._qr = Scanner(self)
		self.screens.addWidget(self._qr)
		self.screens.addWidget(Add(self))
		self.screens.addWidget(Edit(self))
		self.screens.addWidget(Remove(self))
		self.screens.addWidget(Export(self))
		self.screens.addWidget(Finish(self))
		
		self.screens.currentChanged.connect(self._on_page_changed)
	
	def _handle_side_ui(self) -> None:
		"""Connects sidebar buttons to the appropriate screen navigation actions."""
		
		self.view_btn.clicked.connect(lambda: self.screens.setCurrentIndex(0))
		self.qr_btn.clicked.connect(lambda: self.screens.setCurrentIndex(1))
		self.add_btn.clicked.connect(lambda: self.screens.setCurrentIndex(2))
		self.edit_btn.clicked.connect(lambda: self.screens.setCurrentIndex(3))
		self.remove_btn.clicked.connect(lambda: self.screens.setCurrentIndex(4))
		self.exit_btn.clicked.connect(QCoreApplication.quit)
	
	@staticmethod
	def _create_all_items(gs_items: list[dict[str, int | float | str]]) -> list['Item']:
		"""
		Creates and populates the internal list of all inventory items from the data source.
		
		This method parses raw data and instantiates Item objects accordingly.
		"""
		
		obj_items: list[Item] = []
		for item in gs_items:
			vals: list[int | float | str | None] = [
				None if val is None or val == ''
				else val
				for val in list(item.values())
			]
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
		
		controller: stock_manager.AbstractController
		for controller in [self._view, self._edit, self._remove]:
			controller.update_table(controller.table)
