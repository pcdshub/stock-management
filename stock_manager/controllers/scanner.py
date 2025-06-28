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
	_cap: VideoCapture
	
	def __init__(self, app: App):
		super(Scanner, self).__init__()
		self._timer = QTimer()
		self._logger = app.log
		loadUi("ui/scanner.ui", self)
		self.handle_side_ui(self.view_btn, self.qr_btn, self.edit_btn, self.remove_btn, self.exit_btn, app.screens)
		self.start_video()
	
	def start_video(self):
		self._cap = cv2.VideoCapture(0)
		if not self._cap.isOpened():
			self._logger.error_log('[ERROR] Could not access camera')
			return

		self._timer.timeout.connect(self._update_frame)
		self._timer.start(100)

	def stop_video(self):
		self._cap.release()
		self._timer.stop()

	def _update_frame(self):
		worked, frame = self._cap.read()
		if not worked:
			return
		
		self._check_for_qr(frame)
		cv2.cvtColor(frame, cv2.COLOR_BGR2RGB, frame)
		h, w, ch = frame.shape
		bytes_per_line = ch * w
		q_img = QImage(frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)

		self.video_lbl.setPixmap(QPixmap.fromImage(q_img))
	
	def _check_for_qr(self, frame: ndarray):
		detector = cv2.QRCodeDetector()
		data, bbox, code = detector.detectAndDecode(frame)
		if data:
			self._logger.info_log(f"QR Code Scanned: {data}")
