"""
View controller for displaying inventory data in the Stock Management Application.

Handles the main table display and integrates with the database utility.
"""

from pathlib import Path

from PyQt6.QtWidgets import QWidget, QTableWidgetItem, QTableWidget
from PyQt6.uic import loadUi

from stock_manager.model.item import Item
from stock_manager.utils import DBUtils
from .abstract_controller import AbstractController


class View(QWidget, AbstractController):
	"""
	View controller for displaying and managing inventory data.
	"""
	
	def __init__(self, app):
		"""
		Initializes the View controller, loads the UI, and sets up the table.
		
		:param app: Reference to the main application instance.
		"""
		super(View, self).__init__()
		self._database = DBUtils()
		self._logger = app.log
		self._app = app
		
		try:
			ui_path = Path(__file__).resolve().parent.parent.parent / 'ui' / 'view.ui'
			loadUi(str(ui_path), self)
		except Exception as e:
			app.log.error_log(f"Failed to load view UI file: {e}")
			raise
		
		self.handle_side_ui(self.view_btn, self.qr_btn, self.edit_btn, self.remove_btn, self.exit_btn, app.screens)
		self.update_table(app.all_items)
		self.search.textChanged.connect(self._filter_table)
		self.export_btn.clicked.connect(lambda: app.screens.setCurrentIndex(1))
	
	def update_table(self, all_data: list[Item]) -> None:
		"""
		Initializes the table widget with all inventory data from the database.
		"""
		self.table.setRowCount(len(all_data))
		
		row_num: int
		item: Item
		for row_num, item in enumerate(all_data):
			for col_num in range(len(item)):
				self.table.setItem(row_num, col_num, QTableWidgetItem(str(item[col_num])))

	def _filter_table(self, text: str) -> None:
		table: QTableWidget = self.table
		
		if text == '':
			for row in range(table.rowCount()):
				table.setRowHidden(row, False)
			return
				
		for row in range(table.rowCount()):
			match = False
			for col in range(table.columnCount()):
				item = table.item(row, col)
				if item and text.lower() in item.text().lower():
					match = True
					break
			
			table.setRowHidden(row, not match)
