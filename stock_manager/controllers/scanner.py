"""
QR Scanner controller for the Stock Management Application.

Handles video capture, QR code scanning, and updates the UI with camera frames.
"""

from typing import override, TYPE_CHECKING

import cv2
from numpy import ndarray
from PyQt6.QtCore import pyqtSignal, QThread
from PyQt6.QtGui import QImage, QPixmap
from qasync import asyncSlot

from .abstract_controller import AbstractController

if TYPE_CHECKING:
	from stock_manager import App
	from stock_manager import Logger


class Scanner(AbstractController):
	"""QR Scanner UI controller for capturing video and decoding QR codes."""
	
	@override
	def __init__(self, app: 'App'):
		"""
		Initializes the scanner UI.
		
		:param app: Reference to the main application instance.
		"""
		
		super().__init__('scanner', app)
		
		self._db = app.db
		self._camera_thread = CameraThread(self.logger)
		self._user = ''
		self._users_list = app.db.get_all_users()  # get user list from JIRA or database
		self._items: list[str] = []
		
		self.clear_btn.clicked.connect(self._clear_form)
		self.done_btn.clicked.connect(self._finish_form)
	
	def start_video(self) -> None:
		try:
			self._camera_thread.frame_ready.connect(self._process_frame)
			self._camera_thread.start()
		except Exception as e:
			self.logger.error_log(f'Error Starting Camera Thread: {e}')
			print(f'error in start video: {e}')
	
	def stop_video(self) -> None:
		self._camera_thread.stop()
		self._camera_thread.wait()
	
	def _process_frame(self, frame: ndarray) -> None:
		self._check_for_qr(frame)
		
		try:
			cv2.cvtColor(frame, cv2.COLOR_BGR2RGB, frame)
		except Exception as e:
			self.logger.error_log(f"Failed to convert frame color: {e}")
			print(f'failed to convert frame color: {e}')
		
		try:
			h, w, ch = frame.shape
			bytes_per_line = ch * w
			q_img = QImage(frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
			self.video_lbl.setPixmap(QPixmap.fromImage(q_img))
		except Exception as e:
			self.logger.error_log(f"Failed to update video label: {e}")
			print(f'Failed to update video label: {e}')
	
	@asyncSlot()
	async def _check_for_qr(self, frame: ndarray) -> None:
		"""
		Scans the current frame for a QR code and logs if found.
		
		:param frame: Current video frame as a numpy ndarray.
		"""
		
		data, _, _ = cv2.QRCodeDetector().detectAndDecode(frame)
		if data:
			if data in self._items or data == self._user:
				return
			elif data in self._users_list:
				self.desc_lbl.setText(data + ' is checking out items:')
				self._user = data
				return
			
			self.logger.info_log(f"QR Code Scanned: {data}")
			print(f"QR Code Scanned: {data}")
			
			for item in self.app.all_items:
				if data == item.part_num:
					self._items.append(item.part_num)
					self.items_list.append(f'<ul><li>{data}</li></ul>')
					return
			
			self.logger.info_log(f'QR Code Not Recognized: {data}')
			print(f'QR Code Not Recognized: {data}')
	
	def _clear_form(self) -> None:
		"""Clears all fields in the scanner UI form and resets the scanned item list."""
		
		self.logger.info_log('Items List Cleared')
		self._items = []
		self._user = ''
		self.items_list.clear()
	
	def _finish_form(self) -> None:
		"""Handles the completion of a scanning session and navigates to the finish screen."""
		
		if not self._user:
			print("user required")
			return
		elif not self._items:
			print("at least one item required")
			return
		
		try:
			self._handle_remove_items()
		except Exception as e:
			self.app.success.set_text('An Error Occurred, Items Could Not Be Subtracted From Database')
			self.logger.error_log(f'Item(s) could not be subtracted from database: {e}')
		else:
			length = len(self._items)
			self.app.success.set_text(
					f"{length} "
					f"{'item has' if length == 1 else 'items have'} "
					f"successfully been subtracted from database."
			)
			self.logger.info_log(f'{self._user} has checked out items: {self._items}')
			self._clear_form()
			self.desc_lbl.setText('Please Scan User QR Code')
		finally:
			self.app.screens.setCurrentIndex(6)  # finished (success) screen
	
	def _handle_remove_items(self) -> None:
		"""Handles the removal of selected items from the internal item list and updates the UI accordingly."""
		
		for item_name in self._items:
			for item in self.app.all_items:
				if item.part_num == item_name:
					if self.b750_btn.isChecked():
						item.stock_b750 -= 1
					elif self.b757_btn.isChecked():
						item.stock_b757 -= 1
					else:
						self.logger.error_log("Neither Radio Button Is Selected")
						raise ValueError("Neither Radio Button Is Selected")
					
					item.update_stats()
					if item.excess <= 0:
						pass  # TODO: handle alert send for specified item
					
					break
		
		self.app.update_tables()
		self._db.update_database()


class CameraThread(QThread):
	frame_ready = pyqtSignal(object)
	
	def __init__(self, logger: 'Logger', parent=None):
		super().__init__(parent)
		self._running = False
		self._logger = logger
	
	@override
	def run(self) -> None:
		self._running = True
		cap = cv2.VideoCapture(0)
		if not cap.isOpened():
			self._logger.error_log('Could not access camera')
			print('could not access camera')
			return
		
		while self._running:
			worked, frame = cap.read()
			if worked:
				self.frame_ready.emit(frame)
			else:
				self._logger.error_log('Failed to read frame from camera')
				print('Failed to read frame from camera')
		cap.release()
	
	def stop(self) -> None:
		self._running = False
