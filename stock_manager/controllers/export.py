"""
Controls exporting inventory data to various file formats
for the SLAC Inventory Management application.
"""

from pathlib import Path
from typing import override, TYPE_CHECKING

from PyQt6.QtWidgets import QFileDialog, QMessageBox

from .abstract import AbstractController

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
		self.PAGE_INDEX = 6
		
		self.handle_connections()
	
	@override
	def handle_connections(self) -> None:
		self.back_btn.clicked.connect(lambda: self.app.view.to_page())  # keep as lambda because of connect()
		self.location_btn.clicked.connect(self._get_directory)
		self.location_btn.setText(f'...{self._path[-6:]}')
		self.export_btn.clicked.connect(self._export_data)
	
	def _export_data(self) -> None:
		"""Export data based on the selected file type in the UI."""
		
		try:
			match self.export_combo.currentText():
				case 'PDF':
					self.app.file_exports.pdf_export()
				case 'CSV':
					self.app.file_exports.sv_export(self, 'csv', self._path)
				case 'TSV':
					self.app.file_exports.sv_export(self, 'tsv', self._path)
				case 'PSV':
					self.app.file_exports.sv_export(self, 'psv', self._path)
				case 'Select':
					QMessageBox.information(
							self,
							'Please Choose File Type',
							'Please Select A File Type Before Exporting',
							QMessageBox.StandardButton.Ok
					)
				case _ as unknown:
					print(f'Unknown Export Type: "{unknown}"')
					QMessageBox.warning(
							self,
							'Selection Error',
							'Please Select A Valid File Type To Export',
							QMessageBox.StandardButton.Ok
					)
		except Exception as e:
			print(f'Export Failed: {e}')
			self.logger.error_log(f'Export Failed: {e}')
			response = QMessageBox.critical(
					self,
					'Export Failure',
					'Failed To Export Data To File',
					QMessageBox.StandardButton.Ok,
					QMessageBox.StandardButton.Retry
			)
			
			if response == QMessageBox.StandardButton.Retry:
				self._export_data()
	
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
			print(f"Directory Selection Failure: {e}")
			self.logger.error_log(f"Directory Selection Failure: {e}")
			response = QMessageBox.critical(
					self,
					'Directory Selection Failure',
					'Failed To Select Directory',
					QMessageBox.StandardButton.Ok,
					QMessageBox.StandardButton.Retry
			)
			
			if response == QMessageBox.StandardButton.Retry:
				self._get_directory()
