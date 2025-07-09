from functools import partial
from typing import override, TYPE_CHECKING

from .abstract_controller import AbstractController

if TYPE_CHECKING:
	from stock_manager import App


class Remove(AbstractController):
	@override
	def __init__(self, app: 'App'):
		super().__init__('remove', app)
		
		self.search.textChanged.connect(partial(self.filter_table, table=self.table))
		self.table.cellClicked.connect(self._on_cell_clicked)
	
	def _on_cell_clicked(self, row: int, _) -> None:
		selected_item = self.app.all_items[row]
		
		# confirmation popup
		
		# if yes
		self.app.all_items.remove(selected_item)
		self.app.update_tables()
		self.app.db.update_database()
