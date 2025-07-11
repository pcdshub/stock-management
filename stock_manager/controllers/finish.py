"""
Controller for the 'Finish' screen

Manages the UI and logic for displaying the completion screen and returning the user to the main menu.
"""

from typing import override, TYPE_CHECKING

from .abstract import AbstractController

if TYPE_CHECKING:
	from stock_manager import App


class Finish(AbstractController):
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
		
		super().__init__('finish', app)
		
		self.PAGE_INDEX = 7
		
		self.handle_connections()
	
	@override
	def handle_connections(self) -> None:
		self.pushButton.clicked.connect(lambda: self.app.view.to_page())  # keep as lambda because of connect()
	
	def set_text(self, title_txt: str) -> None:
		"""
		Set the label text on the Finish screen.
		
		:param title_txt: Text to display in the label.
		"""
		self.label.setText(title_txt)
