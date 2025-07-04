# TODO: add type annotation and docstrings to entire file
from dataclasses import fields
from functools import partial
from typing import TYPE_CHECKING

from PyQt6.QtWidgets import QLineEdit, QSpinBox, QTextEdit

from stock_manager.model import Item
from stock_manager.utils import EXCESS_EQUATION, TOTAL_EQUATION
from .abstract_controller import AbstractController

if TYPE_CHECKING:
	from stock_manager.app import App


class Edit(AbstractController):
	def __init__(self, app: 'App'):
		super().__init__('edit', app)
		
		self._selected_item: Item | None
		self._total: int
		self._excess: int
		
		self.update_table(app.all_items, self.table)
		self.search.textChanged.connect(partial(self.filter_table, table=self.table))
		self.table.cellClicked.connect(self._on_cell_clicked)
		self.clear_btn.clicked.connect(self._clear_form)
		self.submit_btn.clicked.connect(self._submit_form)
		
		spinner: QSpinBox
		for spinner in [self.b750_spinner, self.b757_spinner, self.min_750_spinner, self.min_757_spinner]:
			spinner.valueChanged.connect(self._on_spinner_change)
	
	def _get_selected_item(self, row: int) -> Item:  # TODO: delete this method if not needed
		info: list[str | int | None] = []
		for i in range(len(fields(Item))):
			item = self.table.item(row, i)
			if item.text().isdigit():
				info.append(int(item.text()))
			elif item.text() == 'None':
				info.append(None)
			else:
				info.append(item.text())
		
		temp_item = Item(*info)
		self._selected_item = temp_item
		return temp_item
	
	def _on_cell_clicked(self, row: int, _) -> None:
		self._selected_item = item = self.app.all_items[row]
		# item = self._get_selected_item(row)
		self._total = item.total
		self._excess = item.excess
		
		self.part_num.setText(str(item.part_num))
		self.manufacturer.setText(item.manufacturer)
		self.desc.setText(item.description)
		self.total_lbl.setText("Total: " + str(self._total))
		self.excess_lbl.setText("Excess: " + str(self._excess))
		self.b750_spinner.setValue(item.stock_b750 if item.stock_b750 is not None else 0)
		self.b757_spinner.setValue(item.stock_b757 if item.stock_b757 is not None else 0)
		self.min_750_spinner.setValue(item.minimum if item.minimum is not None else 0)
		self.min_757_spinner.setValue(item.minimum_sallie if item.minimum_sallie is not None else 0)
	
	def _on_spinner_change(self, _) -> None:
		self._total = TOTAL_EQUATION(self.b750_spinner.value(), self.b757_spinner.value())
		self._excess = EXCESS_EQUATION(self._total, self.min_750_spinner.value(), self.min_757_spinner.value())
		
		self.total_lbl.setText("Total: " + str(self._total))
		self.excess_lbl.setText("Excess: " + str(self._excess))
	
	def _clear_form(self) -> None:
		if not self._selected_item:
			return
		
		self.part_num.setText("Part Number...")
		
		text_field: QLineEdit | QTextEdit
		for text_field in [self.manufacturer, self.desc]:
			text_field.clear()
		
		spinner: QSpinBox
		for spinner in [self.b750_spinner, self.b757_spinner, self.min_750_spinner, self.min_757_spinner]:
			spinner.setValue(0)
		
		self._selected_item = self._total = self._excess = None
	
	def _submit_form(self) -> None:
		if not self._selected_item:
			print('please select an item')
			return
		
		field_vals: list[str | int | None] = [
			self.part_num.text(),
			self.manufacturer.text(),
			self.desc.toPlainText(),
			self._total,
			self.b750_spinner.value(),
			self.b757_spinner.value(),
			self.min_750_spinner.value(),
			self._excess,
			self.min_757_spinner.value()
		]
		
		for i, field_val in enumerate(field_vals):
			if isinstance(field_val, str) and field_val == '':
				field_vals[i] = None
		
		if (new_item := Item(*field_vals)) != self._selected_item:
			for old_item in self.app.all_items:
				if old_item.part_num == new_item.part_num:
					items = self.app.all_items
					items[items.index(old_item)] = new_item
					break
			
			# confirmation popup
			
			# if yes
			self.app.update_tables()
			self.app.db.update_database()
			self._clear_form()
		else:
			print("Items are identical")
