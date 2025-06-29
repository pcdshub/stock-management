"""
View controller for displaying inventory data in the Stock Management Application.

Handles the main table display and integrates with the database utility.
"""
from pathlib import Path

from PyQt6.QtWidgets import QWidget, QTableWidgetItem
from PyQt6.uic import loadUi

import stock_manager
from stock_manager.utils import DBUtils
from .abstract_controller import AbstractController


class View(QWidget, AbstractController):
	"""
	View controller for displaying and managing inventory data.
	"""
	
	def __init__(self, app: stock_manager.App):
		"""
		Initializes the View controller, loads the UI, and sets up the table.
		
		:param app: Reference to the main application instance.
		"""
		super(View, self).__init__()
		self._database = DBUtils()
		self._logger = app.log
		
		try:
			ui_path = Path(__file__).resolve().parent.parent.parent / 'ui' / 'view.ui'
			loadUi(str(ui_path), self)
		except Exception as e:
			app.log.error_log(f"Failed to load view UI file: {e}")
			raise
		
		self.handle_side_ui(self.view_btn, self.qr_btn, self.edit_btn, self.remove_btn, self.exit_btn, app.screens)
		self._init_table()
	
	def _init_table(self) -> None:
		"""
		Initializes the table widget with all inventory data from the database.
		"""
		try:
			all_data: list[dict[str, int | float | str]] = self._database.get_all_data()
		except Exception as e:
			self._logger.error_log(f"Could not load data from the database: {e}")
			return
		
		self.table.setRowCount(len(all_data))
		
		row: int
		row_data: dict[str, int | float | str]
		for row, row_data in enumerate(all_data):
			col: int
			value: int | float | str
			for col, value in enumerate(row_data.values()):
				self.table.setItem(row, col, QTableWidgetItem(str(value)))
