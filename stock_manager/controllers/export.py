import os
from pathlib import Path

from PyQt6.QtWidgets import QWidget, QFileDialog
from PyQt6.uic import loadUi

from .abstract_controller import AbstractController


class Export(QWidget, AbstractController):
	def __init__(self, app):
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
	
	def _export_data(self):
		match self.export_combo.currentText():
			case 'PDF':
				self._pdf_export()
			case 'CSV':
				self._sv_export('csv', ',')
			case 'TSV':
				self._sv_export('tsv', '\t')
			case 'PSV':
				self._sv_export('psv', '|')
	
	def _get_directory(self):
		response = QFileDialog.getExistingDirectory(self, 'Select A Folder',
				str(Path(__file__).resolve().parent.parent.parent / 'exports'))
		response = str(response)
		self.location_btn.setText(f'...{response[-6:]}' if len(response) > 6 else response)
		self._path = response
	
	def _pdf_export(self):
		pass  # TODO: add pdf generation
	
	def _sv_export(self, ext, delimiter):
		with open(self._get_valid_path(ext), 'x') as f:
			for item in self._app.all_items:
				line = ''
				for var in item:  # TODO: __iter__ called here
					line += (str(var) if var else '') + delimiter
				f.write(line[:-1] + '\n')
	
	def _get_valid_path(self, ext):
		name = f'{ext}_export'
		path = f'{self._path}/{name}.{ext}'
		
		count = 1
		while os.path.exists(path):
			path = f'{self._path}/{name}{count}.{ext}'
			count += 1
		
		return path
