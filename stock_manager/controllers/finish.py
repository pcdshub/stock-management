"""
Controller for the 'Finish' screen

Manages the UI and logic for displaying the completion screen and returning the user to the main menu.
"""

from pathlib import Path
from typing import TYPE_CHECKING

from PyQt6.QtWidgets import QWidget
from PyQt6.uic import loadUi

from .abstract_controller import AbstractController

if TYPE_CHECKING:
	from stock_manager.app import App


class Finish(QWidget, AbstractController):
	"""
	Controller for the 'Finish' screen in the SLAC-LCLS Stock Management application.
	
	This UI component displays a completion screen and provides navigation back to the main menu.
	"""

	def __init__(self, app: 'App'):
		"""
		Initialize the Finish screen controller.
		
		Loads the UI from the 'finish.ui' file, sets up navigation buttons,
		and connects the 'pushButton' to switch back to the main menu.
		
		:param app: The main application instance.
		:raises Exception: If the UI file cannot be loaded.
		"""
		
		super(Finish, self).__init__()
		
		try:
			ui_path = Path(__file__).resolve().parent.parent.parent / 'ui' / 'finish.ui'
			loadUi(str(ui_path), self)
		except Exception as e:
			app.log.error_log(f"Failed to load scanner UI file: {e}")
			raise
		
		self.handle_side_ui(self.view_btn, self.qr_btn, self.edit_btn, self.remove_btn, self.exit_btn, app.screens)
		
		self.pushButton.clicked.connect(lambda: app.screens.setCurrentIndex(0))

	def set_text(self, title_txt: str) -> None:
		"""
		Set the label text on the Finish screen.
		
		:param title_txt: Text to display in the label.
		"""
		self.label.setText(title_txt)
