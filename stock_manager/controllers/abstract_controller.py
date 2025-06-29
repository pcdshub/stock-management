"""Abstract base controller for Stock Management Application.

Provides static methods to handle common UI control logic shared
across controllers, such as navigation sidebar button behavior.
"""
from PyQt6.QtCore import QCoreApplication
from PyQt6.QtWidgets import QPushButton, QStackedWidget


class AbstractController:
	"""Abstract controller with common UI behavior for the application."""
	@staticmethod
	def handle_side_ui(
			view_btn: QPushButton,
			qr_btn: QPushButton,
			edit_btn: QPushButton,
			remove_btn: QPushButton,
			exit_btn: QPushButton,
			screens: QStackedWidget) -> None:
		"""
		Connects sidebar buttons to the appropriate screen navigation actions.
		
		:param view_btn: Button to switch to the View screen.
		:param qr_btn: Button to switch to the QR Scanner screen.
		:param edit_btn:
		:param remove_btn:
		:param exit_btn: Button to quit the application.
		:param screens: Stacked widget managing different application screens.
		"""
		view_btn.clicked.connect(lambda: screens.setCurrentIndex(0))
		qr_btn.clicked.connect(lambda: screens.setCurrentIndex(1))
		# edit_btn.clicked.connect(lambda: screens.setCurrentIndex(2))
		# remove_btn.clicked.connect(lambda: screens.setCurrentIndex(3))
		exit_btn.clicked.connect(QCoreApplication.quit)
