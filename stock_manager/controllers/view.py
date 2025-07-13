"""
View controller for displaying inventory data in the Stock Management Application.

Handles the main table display and navigation to the export page.
"""

from typing import override, TYPE_CHECKING

from .abstract import AbstractController

if TYPE_CHECKING:
	from stock_manager import App


class View(AbstractController):
	"""
	Controller for the 'View' page of the stock management application.
	
	Handles displaying inventory data and navigation to `export.ui` and `export.py`.
	"""
	
	def __init__(self, app: 'App'):
		"""
		Controller for the 'View' page of the stock management application.
		
		:param app: Reference to the main application instance.
		"""
		
		super().__init__('view', app)
		self.PAGE_INDEX = 1
		self.handle_connections()
	
	@override
	def handle_connections(self) -> None:
		self.search.textChanged.connect(self.filter_table)
		self.export_btn.clicked.connect(self.app.export.to_page)
