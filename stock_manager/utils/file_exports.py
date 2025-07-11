import os

from PyQt6.QtWidgets import QMessageBox
from qasync import asyncSlot

import stock_manager


class FileExports:
	@staticmethod
	def get_valid_name(ext: str, path: str) -> str:
		"""
		Generate a unique file path for the export file.
		
		:param ext: The desired file extension.
		:param path: The directory to create file in.
		:return: A unique file path as a string.
		"""
		
		name = f'{ext}_export'
		path = f'{path}/{name}.{ext}'
		
		count = 1
		while os.path.exists(path):
			path = f'{path}/{name}{count}.{ext}'
			count += 1
		
		return path
	
	@asyncSlot()
	async def pdf_export(self) -> None:
		"""Export current data to PDF format."""
		
		pass  # TODO: add pdf generation
	
	@asyncSlot()
	async def sv_export(self, instance: stock_manager.AbstractController, ext: str, path: str) -> None:
		"""
		Export current data to a delimited text file (CSV, TSV, PSV).
		
		:param instance: Instance of controller class that method is being called from
		:param ext: The file extension (e.g., 'csv', 'tsv', 'psv').
		:param path: The directory to create file in.
		"""
		
		delimiter = {
			'csv': ',',
			'tsv': '\t',
			'psv': ' | '
		}.get(ext)
		
		try:
			with open(self.get_valid_name(ext, path), 'x') as f:
				for i, item in enumerate(instance.app.all_items):
					line = ''
					for var in item:
						line += (str(var) if var else '') + delimiter
					f.write(line[:-1] + '\n')
					instance.progressBar.setValue(i)
		except FileExistsError as e:
			print(f"That File Already Exists: {e}")
			instance.logger.error_log(f'File Already Exists Error: {e}')
			QMessageBox.critical(
					None,
					'File Exists Error',
					'That File Already Exists, Try Changing File Types',
					QMessageBox.StandardButton.Ok
			)
		except Exception as e:
			print(f'Failed To Export Data To {ext.upper()}: {e}')
			instance.logger.error_log(f'Failed To Export Data To {ext.upper()}: {e}')
			QMessageBox.critical(
					None,
					f'{ext.upper()} Export Error',
					f'Failed To Export Data To {ext.upper()}, Try Changing File Types',
					QMessageBox.StandardButton.Ok
			)
