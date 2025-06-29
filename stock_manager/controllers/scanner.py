"""
QR Scanner controller for the Stock Management Application.

Handles video capture, QR code scanning, and updates the UI with camera frames.
"""
from pathlib import Path

import cv2
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QWidget
from PyQt6.uic import loadUi
from cv2 import VideoCapture
from numpy import ndarray

from stock_manager import App
from .abstract_controller import AbstractController


class Scanner(QWidget, AbstractController):
	"""QR Scanner UI controller for capturing video and decoding QR codes."""
	
	_cap: VideoCapture
	
	def __init__(self, app: App):
		"""
		Initializes the scanner UI and starts video capture.
		
		:param app: Reference to the main application instance.
		"""
		super(Scanner, self).__init__()
		self._timer = QTimer()
		self._logger = app.log
		try:
			ui_path = Path(__file__).resolve().parent.parent.parent / 'ui' / 'scanner.ui'
			loadUi(str(ui_path), self)
		except Exception as e:
			app.log.error_log(f"Failed to load scanner UI file: {e}")
			raise
		
		self.handle_side_ui(self.view_btn, self.qr_btn, self.edit_btn, self.remove_btn, self.exit_btn, app.screens)
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
		"""
		Reads the next frame from the camera, updates the UI, and checks for QR codes.
		
		Logs and skips on frame read failures.
		"""
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
		detector = cv2.QRCodeDetector()
		data, bbox, code = detector.detectAndDecode(frame)
		if data:
			self._logger.info_log(f"QR Code Scanned: {data}")
