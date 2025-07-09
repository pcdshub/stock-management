# TODO at home: add docstrings and type annotation
from typing import override, TYPE_CHECKING

from PyQt6.QtWidgets import QLineEdit, QSpinBox, QTextEdit

from .abstract_controller import AbstractController

if TYPE_CHECKING:
	from stock_manager import App


class Add(AbstractController):
	@override
	def __init__(self, app: 'App'):
		super().__init__('add', app)
		
		self._total = self._excess = 0
		self._spinners: list[QSpinBox] = [
			self.b750_spinner,
			self.b757_spinner,
			self.min_750_spinner,
			self.min_757_spinner
		]
		self._text_fields: list[QLineEdit | QTextEdit] = [
			self.part_num,
			self.manufacturer,
			self.desc
		]
		
		self.clear_btn.clicked.connect(self._clear_form)
		self.submit_btn.clicked.connect(self._submit_form)
		
		for spinner in self._spinners:
			spinner.valueChanged.connect(self._on_spinner_change)
	
	def _on_spinner_change(self, _) -> None:
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
		text_field: QLineEdit | QTextEdit
		for text_field in self._text_fields:
			text_field.clear()
		for spinner in self._spinners:
			spinner.setValue(0)
	
	def _submit_form(self) -> None:  # TODO: test this
		from stock_manager import Item
		
		self.app.all_items.append(
				Item(
						self.part_num.text(),
						self.manufacturer.text(),
						self.desc.toPlainText(),
						self._total,
						self.b750_spinner.value(),
						self.b757_spinner.value(),
						self.min_750_spinner.value(),
						self._excess,
						self.min_757_spinner.value()
				)
		)
		print(self.app.all_items[-1])
