from abc import ABC, ABCMeta, abstractmethod
from pathlib import Path
from typing import override, TYPE_CHECKING

from numpy import ndarray
from PyQt6.QtCore import pyqtSignal, QThread
from PyQt6.QtWidgets import QMessageBox, QTableWidget, QTableWidgetItem, QWidget
from PyQt6.uic import loadUi

if TYPE_CHECKING:
	from stock_manager import App
	from stock_manager import Item


class CombinedMeta(type(QWidget), ABCMeta):
	"""
	A metaclass combining PyQts QWidget metaclass and Python's ABCMeta.
	
	This enables the AbstractController to inherit from both PyQt widgets and Python abstract base classes,
	resolving metaclass conflicts that would otherwise occur with multiple inheritance.
	"""
	pass


class AbstractController(ABC, QWidget, metaclass=CombinedMeta):
	"""Abstract controller with common UI behavior for the application."""
	
	def __init__(self, file_name: str, app: 'App'):
		"""
		Initialize the abstract controller, load its UI, and set up sidebar navigation handlers.
		
		:param file_name: The name of the .ui file (without extension) to load for this controller.
		:param app: Reference to the main application instance
		"""
		
		super(AbstractController, self).__init__()
		
		self.app = app
		self.logger = app.log
		self.database = app.db
		self.PAGE_INDEX = -1
		
		try:
			ui_path = Path(__file__).resolve().parent.parent.parent / 'ui' / f'{file_name}.ui'
			loadUi(str(ui_path), self)
		except Exception as e:
			print(f'Failed To Load {file_name}.ui File: {e}')
			self.logger.error_log(f"Failed To Load {file_name}.ui File: {e}")
			QMessageBox.critical(
					self,
					f'{file_name}.ui Failure',
					f'Failed To Load {file_name}.ui File',
					QMessageBox.StandardButton.Ok
			)
	
	@abstractmethod
	def handle_connections(self) -> None:
		pass
	
	@staticmethod
	def filter_table(text: str, table: QTableWidget) -> None:
		"""
		Filter the rows of a QTableWidget to show only those matching the search text.
		
		:param text: Search string to filter rows by. Only rows that contain this text will be shown.
		:param table: The table widget to filter.
		"""
		
		if text == '':
			for row in range(table.rowCount()):
				table.setRowHidden(row, False)
			return
		
		for row in range(table.rowCount()):
			match = False
			for col in range(table.columnCount()):
				item = table.item(row, col)
				if item and text.lower() in item.text().lower():
					match = True
					break
			
			table.setRowHidden(row, not match)
	
	async def update_table(self, table: QTableWidget) -> None:
		"""
		Initializes the table widget with all inventory data from the database.
		"""
		
		all_data = self.app.all_items
		table.setRowCount(len(all_data))
		
		row_num: int
		item: 'Item'
		for row_num, item in enumerate(all_data):
			for col_num in range(len(item)):
				table.setItem(row_num, col_num, QTableWidgetItem(str(item[col_num])))
	
	def to_page(self) -> None:
		self.app.screens.setCurrentIndex(self.PAGE_INDEX)


class AbstractScanner(AbstractController):
	def __init__(self, file_name: str, app: 'App'):
		super().__init__(file_name, app)
		self.camera_thread = self._CameraThread(self)
	
	@override
	def to_page(self) -> None:
		self.app.screens.setCurrentIndex(self.PAGE_INDEX)
		
		try:
			self.start_video()
		except Exception as e:
			print(f'Failed To Start QR Scanner: {e}')
			self.logger.error_log(f"Failed To Start QR Scanner: {e}")
			QMessageBox.critical(
					self,
					'QR Scanner Error',
					'Failed To Start QR Scanner',
					QMessageBox.StandardButton.Ok
			)
	
	def start_video(self) -> None:
		if self.camera_thread.running:
			return
		
		try:
			self.camera_thread.frame_ready.connect(self.process_frame)
			self.camera_thread.start()
		except Exception as e:
			print(f'Error Starting Camera Thread: {e}')
			self.logger.error_log(f'Error Starting Camera Thread: {e}')
			QMessageBox.critical(
					self,
					'Camera Failure',
					'Failed To Start Camera',
					QMessageBox.StandardButton.Ok
			)
	
	def stop_video(self) -> None:
		if self.camera_thread.running:
			self.camera_thread.stop()
			self.camera_thread.wait()
	
	def process_frame(self, frame: ndarray) -> None:
		self.check_for_qr(frame)
		
		try:
			import cv2
			frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
		except Exception as e:
			print(f'Failed To Convert Frame Color: {e}')
			self.logger.warning_log(f"Failed To Convert Frame Color: {e}")
			QMessageBox.warning(
					self,
					'Color Conversion Error',
					'Failed To Convert Frame Color',
					QMessageBox.StandardButton.Ok
			)
		
		try:
			from PyQt6.QtGui import QImage, QPixmap
			
			h, w, ch = frame.shape
			bytes_per_line = ch * w
			q_img = QImage(frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
			self.video_lbl.setPixmap(QPixmap.fromImage(q_img))
		except Exception as e:
			print(f'Failed To Update Video Label: {e}')
			self.logger.error_log(f'Failed To Update Video Label: {e}')
			QMessageBox.critical(
					self,
					'Video Label Failure',
					'Failed To Update Video Label',
					QMessageBox.StandardButton.Ok
			)
	
	@abstractmethod
	async def check_for_qr(self, frame: ndarray) -> None:
		pass
	
	class _CameraThread(QThread):
		frame_ready = pyqtSignal(object)
		
		def __init__(self, outer_instance: AbstractController, parent=None):
			super().__init__(parent)
			self.running = False
			self._logger = outer_instance.logger
		
		@override
		def run(self) -> None:
			from cv2 import VideoCapture
			
			self.running = True
			cap = VideoCapture(0)
			if not cap.isOpened():
				self._logger.error_log('Could Not Access Camera')
				print('Could Not Access Camera')
				response = QMessageBox.critical(
						None,
						'Camera Failure',
						'Failed To Access Camera',
						QMessageBox.StandardButton.Ok,
						QMessageBox.StandardButton.Retry
				)
				
				if response == QMessageBox.StandardButton.Retry:
					self.run()
				
				return
			
			while self.running:
				worked, frame = cap.read()
				if worked:
					self.frame_ready.emit(frame)
				else:
					print('Failed To Read Frame From Camera')
					self._logger.error_log('Failed To Read Frame From Camera')
					QMessageBox.critical(
							None,
							'Frame Read Failure',
							'Failed To Read Frame From Camera',
							QMessageBox.StandardButton.Ok
					)
			cap.release()
		
		def stop(self) -> None:
			self.running = False
