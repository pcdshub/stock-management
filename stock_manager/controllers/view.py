from PyQt6.QtWidgets import QWidget, QTableWidgetItem
from PyQt6.uic import loadUi

import stock_manager
from stock_manager.utils import DBUtils
from .abstract_controller import AbstractController


class View(QWidget, AbstractController):
	def __init__(self, app: stock_manager.App):
		super(View, self).__init__()
		self._database = DBUtils()
		loadUi("ui/view.ui", self)
		self.handle_side_ui(self.view_btn, self.qr_btn, self.edit_btn, self.remove_btn, self.exit_btn, app.screens)
		self._init_table()
	
	def _init_table(self) -> None:
		all_data: list[dict[str, int | float | str]] = self._database.get_all_data()
		
		self.table.setRowCount(len(all_data))
		
		row: int
		row_data: dict[str, int | float | str]
		for row, row_data in enumerate(all_data):
			col: int
			value: int | float | str
			for col, value in enumerate(row_data.values()):
				self.table.setItem(row, col, QTableWidgetItem(str(value)))
