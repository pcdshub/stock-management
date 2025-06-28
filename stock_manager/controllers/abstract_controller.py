from PyQt6.QtCore import QCoreApplication
from PyQt6.QtWidgets import QPushButton, QStackedWidget


class AbstractController:
	@staticmethod
	def handle_side_ui(
			view_btn: QPushButton,
			qr_btn: QPushButton,
			edit_btn: QPushButton,
			remove_btn: QPushButton,
			exit_btn: QPushButton,
			screens: QStackedWidget):
		view_btn.clicked.connect(lambda: screens.setCurrentIndex(0))
		qr_btn.clicked.connect(lambda: screens.setCurrentIndex(1))
		# edit_btn.clicked.connect(lambda: screens.setCurrentIndex(2))
		# remove_btn.clicked.connect(lambda: screens.setCurrentIndex(3))
		exit_btn.clicked.connect(QCoreApplication.quit)
