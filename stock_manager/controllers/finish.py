"""
Finish page controller for displaying success or
error message upon form submission from other controllers
in the Stock Management Application.

Manages the UI and logic for displaying the completion screen and returning the user to the main menu.
"""

from typing import override, TYPE_CHECKING

import stock_manager
from .abstract import AbstractController

if TYPE_CHECKING:
	from stock_manager import App


class Finish(AbstractController):
	"""
	Controller for the 'Finish' screen in the SLAC-LCLS Stock Management application.
	
	Handles a completion screen and provides navigation back to `view.ui` and `view.py`.
	"""
	
	def __init__(self, app: 'App'):
		"""
		Initialize the Finish screen controller.
		
		:param app: The main application instance.
		"""
		
		page = stock_manager.Pages.FINISHED
		super().__init__(page.value.FILE_NAME, app)
		self.PAGE_NAME = page
		self.handle_connections()
	
	@override
	def handle_connections(self) -> None:
		self.pushButton.clicked.connect(lambda: self.app.view.to_page())  # keep as lambda because of connect()
	
	def set_text(self, title_txt: str) -> None:
		"""
		Set the text label on the Finish screen.
		
		:param title_txt: Text to display in the label.
		"""
		self.label.setText(title_txt)
