"""
Abstract base controller for Stock Management Application.

Provides static methods to handle common UI control logic shared
across controllers, such as navigation sidebar button behavior,
table filtering and updating.
"""

from abc import ABC, ABCMeta
from pathlib import Path
from typing import TYPE_CHECKING

from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QWidget
from PyQt6.uic import loadUi

if TYPE_CHECKING:
	from stock_manager import App
	from stock_manager import Item


class CombinedMeta(type(QWidget), ABCMeta):
	"""
	A metaclass combining PyQts QWidget metaclass and Python's ABCMeta.
	
	This enables the AbstractController to inherit from both PyQt widgets and Python abstract base classes,
	resolving metaclass conflicts that would otherwise occur with multiple inheritance.
	"""
	pass


class AbstractController(ABC, QWidget, metaclass=CombinedMeta):
	"""Abstract controller with common UI behavior for the application."""
	
	def __init__(self, file_name: str, app: 'App'):
		"""
		Initialize the abstract controller, load its UI, and set up sidebar navigation handlers.
		
		:param file_name: The name of the .ui file (without extension) to load for this controller.
		:param app: Reference to the main application instance
		"""
		
		super(AbstractController, self).__init__()
		
		self.app = app
		self.logger = app.log
		
		try:
			ui_path = Path(__file__).resolve().parent.parent.parent / 'ui' / f'{file_name}.ui'
			loadUi(str(ui_path), self)
		except Exception as e:
			app.log.error_log(f"Failed to load view UI file: {e}")
			raise
		
	@staticmethod
	def filter_table(text: str, table: QTableWidget) -> None:
		"""
		Filter the rows of a QTableWidget to show only those matching the search text.
		
		:param text: Search string to filter rows by. Only rows that contain this text will be shown.
		:param table: The table widget to filter.
		"""
		
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
	
	def update_table(self, table: QTableWidget) -> None:
		"""
		Initializes the table widget with all inventory data from the database.
		"""
		
		all_data = self.app.all_items
		table.setRowCount(len(all_data))
		
		row_num: int
		item: 'Item'
		for row_num, item in enumerate(all_data):
			for col_num in range(len(item)):
				table.setItem(row_num, col_num, QTableWidgetItem(str(item[col_num])))
