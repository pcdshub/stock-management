"""
View controller for displaying inventory data in the Stock Management Application.

Handles the main table display and integrates with the database utility.
"""

from functools import partial
from typing import override, TYPE_CHECKING

from .abstract_controller import AbstractController

if TYPE_CHECKING:
	from stock_manager import App


class View(AbstractController):
	"""
	View controller for displaying and managing inventory data.
	"""
	
	@override
	def __init__(self, app: 'App'):
		"""
		Initializes the View controller, loads the UI, and sets up the table.
		
		:param app: Reference to the main application instance.
		"""
		
		super().__init__('view', app)
		
		self.PAGE_INDEX = 1
		
		self.search.textChanged.connect(partial(self.filter_table, table=self.table))
		self.export_btn.clicked.connect(app.export.to_page)
