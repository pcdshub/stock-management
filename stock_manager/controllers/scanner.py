"""
QR Scanner controller for the Stock Management Application.

Handles video capture, QR code scanning, and updates the UI with camera frames.
"""

from pathlib import Path
from typing import TYPE_CHECKING

import cv2
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QWidget
from PyQt6.uic import loadUi
from cv2 import VideoCapture
from numpy import ndarray

from .abstract_controller import AbstractController

if TYPE_CHECKING:
	from stock_manager.app import App


class Scanner(QWidget, AbstractController):
	"""QR Scanner UI controller for capturing video and decoding QR codes."""
	
	def __init__(self, app: 'App'):
		"""
		Initializes the scanner UI and starts video capture.
		
		:param app: Reference to the main application instance.
		"""
		super(Scanner, self).__init__()
		self._app = app
		self._logger = app.log
		self._db = app.db
		self._timer = QTimer()
		self._cap: VideoCapture
		self._user = ''
		self._users_list = app.db.get_all_users()  # get user list from JIRA or database
		self._items: list[str] = []
		
		try:
			ui_path = Path(__file__).resolve().parent.parent.parent / 'ui' / 'scanner.ui'
			loadUi(str(ui_path), self)
		except Exception as e:
			app.log.error_log(f"Failed to load scanner UI file: {e}")
			raise
		
		self.handle_side_ui(self.view_btn, self.qr_btn, self.edit_btn, self.remove_btn, self.exit_btn, app.screens)
		self.clear_btn.clicked.connect(self._clear_form)
		self.done_btn.clicked.connect(self._finish_form)
		self.start_video()
	
	def start_video(self) -> None:
		"""Starts video capture from the default camera."""
		
		self._cap = cv2.VideoCapture(0)
		if not self._cap.isOpened():
			self._logger.error_log('Could not access camera')
			return
		
		self._timer.timeout.connect(self._update_frame)
		self._timer.start(100)
	
	def stop_video(self) -> None:
		"""Stops video capture and disconnects the timer."""
		
		self._cap.release()
		self._timer.stop()
	
	def _update_frame(self) -> None:
		"""Reads the next frame from the camera, updates the UI, and checks for QR codes."""
		
		worked, frame = self._cap.read()
		if not worked:
			self._logger.error_log('Failed to read frame from camera')
			return
		
		self._check_for_qr(frame)
		
		try:
			cv2.cvtColor(frame, cv2.COLOR_BGR2RGB, frame)
		except Exception as e:
			self._logger.error_log(f"Failed to convert frame color: {e}")
		
		h, w, ch = frame.shape
		bytes_per_line = ch * w
		
		try:
			q_img = QImage(frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
			self.video_lbl.setPixmap(QPixmap.fromImage(q_img))
		except Exception as e:
			self._logger.error_log(f"Failed to update video label: {e}")
	
	def _check_for_qr(self, frame: ndarray) -> None:
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
			
			self._logger.info_log(f"QR Code Scanned: {data}")
			print(f"QR Code Scanned: {data}")
			
			for item in self._app.all_items:
				if data == item.part_num:
					self._items.append(item.part_num)
					self.items_list.append(f'<ul><li>{data}</li></ul>')
					return
			
			self._logger.info_log(f'QR Code Not Recognized: {data}')
			print(f'QR Code Not Recognized: {data}')
	
	def _clear_form(self) -> None:
		"""Clears all fields in the scanner UI form and resets the scanned item list."""
		
		self._logger.info_log('Items List Cleared')
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
			self._app.success.set_text('An Error Occurred, Items Could Not Be Subtracted From Database')
			self._logger.error_log(f'Item(s) could not be subtracted from database: {e}')
		else:
			length = len(self._items)
			self._app.success.set_text(f"{length} {'item has' if length == 1 else 'items have'} successfully been subtracted from database.")
			self._logger.info_log(f'{self._user} has checked out items: {self._items}')
			self._clear_form()
			self.desc_lbl.setText('Please Scan User QR Code')
		finally:
			self._app.screens.setCurrentIndex(3)  # finished (success) screen
	
	def _handle_remove_items(self) -> None:
		"""Handles the removal of selected items from the internal item list and updates the UI accordingly."""
		
		for item_name in self._items:
			for item in self._app.all_items:
				if item.part_num == item_name:
					if self.b750_btn.isChecked():
						item.stock_b750 -= 1
					elif self.b757_btn.isChecked():
						item.stock_b757 -= 1
					else:
						self._logger.error_log("Neither Radio Button Is Selected")
						raise ValueError("Neither Radio Button Is Selected")
					
					item.update_stats()
					if item.excess <= 0:
						pass  # TODO: handle alert send for specified item
					
					break
					
		self._app.update_tables()
		self._db.update_database()
