"""
Edit controller for managing inventory item edits in the Stock Management Application.

This module provides the Edit class, which handles the UI and logic for editing inventory items,
including updating item details, validating user input, and saving changes to the database.
"""

from functools import partial
from typing import override, TYPE_CHECKING

from PyQt6.QtWidgets import QLineEdit, QSpinBox, QTextEdit

from stock_manager.model.item import Item
from .abstract_controller import AbstractController

if TYPE_CHECKING:
	from stock_manager import App


class Edit(AbstractController):
	"""Controller for editing inventory items in the Stock Management Application."""
	
	@override
	def __init__(self, app: 'App'):
		"""
		Initialize the Edit controller, load the UI, set up the table, and connect signals for user interactions.
		
		:param app: Reference to the main application instance.
		"""
		
		super().__init__('edit', app)
		
		self._selected_item: Item | None = None
		self._total = self._excess = 0
		self._spinners: list[QSpinBox] = [
			self.b750_spinner,
			self.b757_spinner,
			self.min_750_spinner,
			self.min_757_spinner
		]
		self._text_fields: list[QLineEdit | QTextEdit] = [self.manufacturer, self.desc]
		
		self.search.textChanged.connect(partial(self.filter_table, table=self.table))
		self.table.cellClicked.connect(self._on_cell_clicked)
		self.clear_btn.clicked.connect(self._clear_form)
		self.submit_btn.clicked.connect(self._submit_form)
		
		for spinner in self._spinners:
			spinner.valueChanged.connect(self._on_spinner_change)
	
	@staticmethod
	def _parse_field(text: str) -> int | str | None:
		"""
		Convert text from a table cell into the appropriate type (int, str, or None).
		
		:param text: The text to parse.
		:return: The parsed value.
		"""
		
		if text in ['None', '']:
			return None
		elif text.isdigit():
			return int(text)
		return text
	
	def _get_selected_item(self, row: int) -> Item:  # TODO: delete this method if not needed
		"""
		Construct and return an Item instance from the data in the specified table row.
		
		:param row: The index of the table row to extract item data from.
		:return: The Item instance constructed from the row's values.
		"""
		
		info: list[int | str | None] = []
		
		try:
			info = [
				self._parse_field(self.table.item(row, i).text())
				for i in range(len(Item))
			]
		except Exception as e:
			print(f"Item parsing error: {e}")
			self.app.log.error_log(f"Item parsing error: {e}")
		
		temp_item = Item(*info)
		self._selected_item = temp_item
		return temp_item
	
	def _on_cell_clicked(self, row: int, _) -> None:
		"""
		Populate the edit form fields with data from the selected item when a table row is clicked.
		
		:param row: The index of the clicked table row.
		:param _: The column index (unused).
		"""
		
		try:
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
		except Exception as e:
			print(f"Failed to populate fields: {e}")
			self.app.log.error_log(f"Failed to populate fields: {e}")
	
	def _on_spinner_change(self, _) -> None:
		"""
		Update the total and excess labels when any spinner value changes.
		
		:param _: The value emitted by the spinner (unused)
		"""
		
		try:
			from stock_manager import EXCESS_EQUATION, TOTAL_EQUATION
			self._total = TOTAL_EQUATION(self.b750_spinner.value(), self.b757_spinner.value())
			self._excess = EXCESS_EQUATION(
					self._total, self.min_750_spinner.value(), self.min_757_spinner.value()
			)
			
			self.total_lbl.setText("Total: " + str(self._total))
			self.excess_lbl.setText("Excess: " + str(self._excess))
		except Exception as e:
			print(f"Spinner change error: {e}")
			self.app.log.error_log(f"Spinner change error: {e}")
	
	def _clear_form(self) -> None:
		"""Clear all fields in the edit form and reset spinners and labels."""
		
		if not self._selected_item:
			return
		
		self.part_num.setText("Part Number...")
		
		text_field: QLineEdit | QTextEdit
		for text_field in self._text_fields:
			text_field.clear()
		for spinner in self._spinners:
			spinner.setValue(0)
		
		self._selected_item = None
		self._total = self._excess = 0
	
	def _submit_form(self) -> None:
		"""
		Validate form data, update the selected item if it has changed,
		update the tables and database, and clear the form.
		"""
		
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
		
		i: int
		field_val: str | int | None
		for i, field_val in enumerate(field_vals):
			if isinstance(field_val, str):
				field_vals[i] = self._parse_field(field_val)
		
		if (new_item := Item(*field_vals)) != self._selected_item:
			try:
				idx = next(
						i for i, old_item in enumerate(self.app.all_items) if old_item.part_num == new_item.part_num
				)
				self.app.all_items[idx] = new_item
			except StopIteration:
				print("Item with this part number does not exist.")
				return
			
			# confirmation popup
			
			# if yes
			self.app.update_tables()
			self.app.db.update_database()
			self._clear_form()
		else:
			print("Items are identical")
