"""Controls exporting inventory data to various file formats for the SLAC Inventory Management application."""

import os
from pathlib import Path
from typing import TYPE_CHECKING

from PyQt6.QtWidgets import QFileDialog

from .abstract_controller import AbstractController

if TYPE_CHECKING:
	from stock_manager import App


class Export(AbstractController):
	"""UI controller for data export functionality."""
	
	def __init__(self, app: 'App'):
		"""
		Initialize the Export controller.
		
		:param app: Reference to the main application instance.
		"""
		super().__init__('export', app)
		
		self._path = str(Path(__file__).resolve().parent.parent.parent / 'exports')
		
		self.back_btn.clicked.connect(lambda: app.screens.setCurrentIndex(0))
		self.location_btn.clicked.connect(self._get_directory)
		self.location_btn.setText(f'...{self._path[-6:]}')
		self.export_btn.clicked.connect(self._export_data)
	
	def _export_data(self) -> None:
		"""Export data based on the selected file type in the UI."""
		
		try:
			match self.export_combo.currentText():
				case 'PDF':
					self._pdf_export()
				case 'CSV':
					self._sv_export('csv')
				case 'TSV':
					self._sv_export('tsv')
				case 'PSV':
					self._sv_export('psv')
				case _:
					print("unknown export type")
		except Exception as e:
			print(f'Export Failed: {e}')
			self.app.log.error_log(f'Export Failed: {e}')
	
	def _get_directory(self) -> None:
		"""Open a dialog to select the export directory and update the UI."""
		
		try:
			response = QFileDialog.getExistingDirectory(
					self, 'Select A Folder',
					str(Path(__file__).resolve().parent.parent.parent / 'exports')
			)
			response = str(response)
			self.location_btn.setText(f'...{response[-6:]}' if len(response) > 6 else response)
			self._path = response
		except Exception as e:
			print(f"Directory selection failed: {e}")
			self.app.log.error_log(f"Directory selection failed: {e}")
	
	def _pdf_export(self) -> None:
		"""Export current data to PDF format."""
		
		pass  # TODO: add pdf generation
	
	def _sv_export(self, ext: str) -> None:
		"""
		Export current data to a delimited text file (CSV, TSV, PSV).
		
		:param ext: The file extension (e.g., 'csv', 'tsv', 'psv').
		"""
		
		delimiter = {
			'csv': ',',
			'tsv': '\t',
			'psv': ' | '
		}.get(ext)
		
		try:
			with open(self._get_valid_path(ext), 'x') as f:
				for item in self.app.all_items:
					line = ''
					for var in item:
						line += (str(var) if var else '') + delimiter
					f.write(line[:-1] + '\n')
		except FileExistsError:
			print("file already exists")
		except Exception as e:
			print(f'Failed To Export Data To {ext.upper()}: {e}')
			self.app.log.error_log(f'Failed To Export Data To {ext.upper()}: {e}')
	
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
