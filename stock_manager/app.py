"""
Instantiate and run the App class to start the SLAC Inventory Management application.
"""

import asyncio
from pathlib import Path
from typing import override

from PyQt6.QtCore import QCoreApplication
from PyQt6.QtGui import QCloseEvent, QFont
from PyQt6.QtWidgets import QMainWindow, QMessageBox, QPushButton, QStackedWidget
from PyQt6.uic import loadUi
from qasync import asyncSlot

import stock_manager
from stock_manager.model import Item


class App(QMainWindow):
	"""
	Main application window for SLAC Inventory Management.
	
	Handles UI loading, screen transitions, and application startup/shutdown events.
	"""
	
	def __init__(self):
		"""Initialize the main application window and setup screens."""
		
		from stock_manager import DBUtils, Logger, Edit, Export, Finish, Remove, ItemScanner, View, Add, Login, \
			FileExports, QRGenerator
		
		super(App, self).__init__()
		
		self.log = Logger()
		self.db = DBUtils()
		self.file_exports = FileExports()
		self.qr_generator = QRGenerator()
		self.export = Export(self)
		self.finish = Finish(self)
		self.login = Login(self)
		self.view = View(self)
		self.item_scanner = ItemScanner(self)
		self.add = Add(self)
		self.edit = Edit(self)
		self.remove = Remove(self)
		
		self.user: str | None = None
		self.all_items: list[Item] = []
		self.screens: QStackedWidget | None = None
		
		try:
			ui_path = Path(__file__).resolve().parent.parent / 'ui' / 'main.ui'
			loadUi(str(ui_path), self)
		except Exception as e:
			print(f"Failed To Load Main UI File: {e}")
			self.log.error_log(f"Failed To Load Main UI File: {e}")
			QMessageBox.critical(
					None,
					'UI Failure',
					'Failed To Load Main UI File',
					QMessageBox.StandardButton.Ok
			)
			raise SystemExit(1)
		
		def handle_screens() -> None:
			screens_to_add: list[stock_manager.AbstractController] = [
				self.login, self.view, self.item_scanner, self.add,
				self.edit, self.remove, self.export, self.finish
			]
			
			for screen in screens_to_add:
				self.screens.addWidget(screen)
			
			self.screens.currentChanged.connect(self._on_page_changed)
		
		def handle_connections() -> None:
			"""Connects sidebar buttons to the appropriate screen navigation actions."""
			
			self.view_btn.clicked.connect(self.view.to_page)
			self.qr_btn.clicked.connect(self.item_scanner.to_page)
			self.add_btn.clicked.connect(self.add.to_page)
			self.edit_btn.clicked.connect(self.edit.to_page)
			self.remove_btn.clicked.connect(self.remove.to_page)
			self.exit_btn.clicked.connect(QCoreApplication.quit)
		
		handle_screens()
		handle_connections()
	
	def run(self) -> None:
		self.log.info_log("App Started")
		self.login.to_page()
		self._on_page_changed()
		self._async_load()
	
	@asyncSlot()
	async def _async_load(self) -> None:
		async def create_all_items(gs_items: list[dict[str, int | float | str]]) -> list[Item]:
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
		
		try:
			gs_data: list[dict[str, int | float | str]] = await self.db.get_all_data()
			self.all_items = await create_all_items(gs_data)
			await self.update_tables()
		except Exception as e:
			print(f'Error Loading Data Asynchronously: {e}')
			self.log.error_log(f"Could not load data from database: {e}")
			response = QMessageBox.critical(
					self,
					'Data Load Failure',
					'Failed To Load Data From Database',
					QMessageBox.StandardButton.Ok,
					QMessageBox.StandardButton.Close
			)
			
			if response == QMessageBox.StandardButton.Close:
				raise SystemExit(1)
	
	def _on_page_changed(self) -> None:
		"""Update window title and manage QR scanner based on current screen."""
		
		from stock_manager import SIDEBAR_BUTTON_SIZE, PAGE_NAMES
		
		idx = self.screens.currentIndex()
		username = f' - {self.user}' if self.user else ''
		
		try:
			self.setWindowTitle(PAGE_NAMES[idx] + " | SLAC Inventory Management Application" + username)
		except IndexError as e:
			print(f'Page Index Not In constants.PAGE_NAMES: {e}')
			self.setWindowTitle("SLAC Inventory Management Application" + username)
		
		if idx != 1:
			try:
				self.item_scanner.stop_video()
			except Exception as e:
				print(f'Failed To Stop QR Scanner: {e}')
				self.log.error_log(f"Failed To Stop QR Scanner: {e}")
				QMessageBox.critical(
						self,
						'QR Scanner Error',
						'Failed To Stop QR Scanner',
						QMessageBox.StandardButton.Ok
				)
		
		buttons: list[QPushButton] = self.sideUI.children()[1:]  # exclude QVBox
		
		active = QFont()
		active.setPointSize(SIDEBAR_BUTTON_SIZE)
		active.setBold(True)
		inactive = QFont()
		inactive.setPointSize(SIDEBAR_BUTTON_SIZE)
		
		i: int
		button: QPushButton
		for i, button in enumerate(buttons, start=1):
			button.setFont(active if i == idx else inactive)
	
	@override
	def closeEvent(self, event: QCloseEvent) -> None:
		"""Handle the application close event and log exit."""
		
		self.log.info_log("App Exited\n")
		super().closeEvent(event)
	
	@asyncSlot()
	async def update_tables(self) -> None:
		"""
		Refreshes or updates the displayed tables in the UI to reflect the latest inventory data.
		
		This method should be called after making changes to the inventory or data source.
		"""
		
		await asyncio.gather(
				*(controller.update_table(controller.table) for controller in [self.view, self.edit, self.remove])
		)
