"""Abstract base controller for Stock Management Application.

Provides static methods to handle common UI control logic shared
across controllers, such as navigation sidebar button behavior,
table filtering and updating.
"""

from abc import ABC, ABCMeta
from pathlib import Path
from typing import TYPE_CHECKING

from PyQt6.QtCore import QCoreApplication
from PyQt6.QtWidgets import QPushButton, QStackedWidget, QTableWidget, QTableWidgetItem, QWidget
from PyQt6.uic import loadUi

from stock_manager.model import Item

if TYPE_CHECKING:
	from stock_manager.app import App


class CombinedMeta(type(QWidget), ABCMeta):
	pass


class AbstractController(ABC, QWidget, metaclass=CombinedMeta):
	"""Abstract controller with common UI behavior for the application."""
	
	def __init__(self, file_name: str, app: 'App'):
		super(AbstractController, self).__init__()
		
		self.app = app
		self.logger = app.log
		
		try:
			ui_path = Path(__file__).resolve().parent.parent.parent / 'ui' / f'{file_name}.ui'
			loadUi(str(ui_path), self)
		except Exception as e:
			app.log.error_log(f"Failed to load view UI file: {e}")
			raise
		
		self._handle_side_ui(self.view_btn, self.qr_btn, self.edit_btn, self.remove_btn, self.exit_btn, app.screens)
	
	@staticmethod
	def _handle_side_ui(
			view_btn: QPushButton,
			qr_btn: QPushButton,
			edit_btn: QPushButton,
			remove_btn: QPushButton,
			exit_btn: QPushButton,
			screens: QStackedWidget
	) -> None:
		"""
		Connects sidebar buttons to the appropriate screen navigation actions.
		
		:param view_btn: Button to switch to the View screen.
		:param qr_btn: Button to switch to the QR Scanner screen.
		:param edit_btn:
		:param remove_btn:
		:param exit_btn: Button to quit the application.
		:param screens: Stacked widget managing different application screens.
		"""
		view_btn.clicked.connect(lambda: screens.setCurrentIndex(0))
		qr_btn.clicked.connect(lambda: screens.setCurrentIndex(2))
		edit_btn.clicked.connect(lambda: screens.setCurrentIndex(4))
		# remove_btn.clicked.connect(lambda: screens.setCurrentIndex(3))
		exit_btn.clicked.connect(QCoreApplication.quit)
	
	@staticmethod
	def filter_table(text: str, table: QTableWidget) -> None:
		# TODO: add docstring
		
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
	
	@staticmethod
	def update_table(all_data: list[Item], table: QTableWidget) -> None:
		"""
		Initializes the table widget with all inventory data from the database.
		"""
		
		table.setRowCount(len(all_data))
		
		row_num: int
		item: Item
		for row_num, item in enumerate(all_data):
			for col_num in range(len(item)):
				table.setItem(row_num, col_num, QTableWidgetItem(str(item[col_num])))
