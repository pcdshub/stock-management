"""
Remove page controller for removing inventory data in the Stock Management Application.

Provides functionality for removing stock items from the database.
Includes search filtering and confirmation dialogs for safe item removal.
"""

from typing import override, TYPE_CHECKING

from PyQt6.QtWidgets import QMessageBox

import stock_manager
from .abstract import AbstractController

if TYPE_CHECKING:
	from stock_manager import App


class Remove(AbstractController):
	"""
	Controller for the 'Remove' page of the stock management application.
	
	Handles user interactions for searching and removing stock items
	from the database.
	"""
	
	def __init__(self, app: 'App'):
		"""
		Initialize the Remove page.
		
		:param app: Reference to the main application instance.
		"""
		
		page = stock_manager.Pages.REMOVE
		super().__init__(page.value.FILE_NAME, app)
		self.PAGE_NAME = page
		self.handle_connections()
	
	@override
	def handle_connections(self) -> None:
		self.search.textChanged.connect(self.filter_table)
		self.table.cellClicked.connect(self._on_cell_clicked)
	
	def _on_cell_clicked(self, row: int, _) -> None:
		"""
		Confirms and deletes item after user confirmation
		when a table row is clicked.
		
		:param row: The index of the clicked table row.
		:param _: The column index (unused).
		"""
		selected_item = self.app.all_items[row]
		
		response = QMessageBox.warning(
				self,
				'Item Removal Confirmation',
				f'Are You Sure You Want To Remove {selected_item.part_num} '
				'From The Database?\n\nThis Action Cannot Be Undone.',
				QMessageBox.StandardButton.Yes,
				QMessageBox.StandardButton.No
		)
		
		if response == QMessageBox.StandardButton.Yes:
			self.app.all_items.remove(selected_item)
			self.logger.info_log(f'Item Removed From Database: {selected_item.part_num}')
			self.app.update_tables()
			self.database.update_database(stock_manager.DatabaseUpdateType.REMOVE, selected_item)
