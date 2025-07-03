"""Controls exporting inventory data to various file formats for the SLAC Inventory Management application."""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING

from PyQt6.QtWidgets import QWidget, QFileDialog
from PyQt6.uic import loadUi

from .abstract_controller import AbstractController

if TYPE_CHECKING:
	from stock_manager.app import App


class Export(QWidget, AbstractController):
	"""UI controller for data export functionality."""
	
	def __init__(self, app: 'App'):
		"""
		Initialize the Export controller.
		
		:param app: Reference to the main application instance.
		"""
		super(Export, self).__init__()
		
		self._path = str(Path(__file__).resolve().parent.parent.parent / 'exports')
		self._app = app
		
		try:
			ui_path = Path(__file__).resolve().parent.parent.parent / 'ui' / 'export.ui'
			loadUi(str(ui_path), self)
		except Exception as e:
			app.log.error_log(f"Failed to load scanner UI file: {e}")
			raise
		
		self.handle_side_ui(self.view_btn, self.qr_btn, self.edit_btn, self.remove_btn, self.exit_btn, app.screens)
		
		self.back_btn.clicked.connect(lambda: app.screens.setCurrentIndex(0))
		self.location_btn.clicked.connect(self._get_directory)
		self.location_btn.setText(f'...{self._path[-6:]}')
		self.export_btn.clicked.connect(self._export_data)
	
	def _export_data(self) -> None:
		"""Export data based on the selected file type in the UI."""
		
		match self.export_combo.currentText():
			case 'PDF':
				self._pdf_export()
			case 'CSV':
				self._sv_export('csv')
			case 'TSV':
				self._sv_export('tsv')
			case 'PSV':
				self._sv_export('psv')
	
	def _get_directory(self) -> None:
		"""Open a dialog to select the export directory and update the UI."""
		
		response = QFileDialog.getExistingDirectory(self, 'Select A Folder',
				str(Path(__file__).resolve().parent.parent.parent / 'exports'))
		response = str(response)
		self.location_btn.setText(f'...{response[-6:]}' if len(response) > 6 else response)
		self._path = response
	
	def _pdf_export(self) -> None:
		"""Export current data to PDF format."""
		
		pass  # TODO: add pdf generation
	
	def _sv_export(self, ext: str) -> None:
		"""
		Export current data to a delimited text file (CSV, TSV, PSV).
		
		:param ext: The file extension (e.g., 'csv', 'tsv', 'psv').
		"""
		
		delimiter = {
			'CSV': ',',
			'TSV': '\t',
			'PSV': ' | '
		}.get(ext)
		
		with open(self._get_valid_path(ext), 'x') as f:
			for item in self._app.all_items:
				line = ''
				for var in item:
					line += (str(var) if var else '') + delimiter
				f.write(line[:-1] + '\n')
	
	def _get_valid_path(self, ext: str) -> str:
		"""
		Generate a unique file path for the export file.
		
		:param ext: The desired file extension.
		:return: A unique file path as a string.
		"""
		name = f'{ext}_export'
		path = f'{self._path}/{name}.{ext}'
		
		count = 1
		while os.path.exists(path):
			path = f'{self._path}/{name}{count}.{ext}'
			count += 1
		
		return path
