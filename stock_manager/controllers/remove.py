"""
Remove page controller for removing inventory data in the Stock Management Application.

Provides functionality for removing stock items from the database.
Includes search filtering and confirmation dialogs for safe item removal.
"""

from typing import override, TYPE_CHECKING

from PyQt5.QtCore import QModelIndex
from PyQt5.QtWidgets import QMessageBox

import stock_manager
from stock_manager.controllers import AbstractController

if TYPE_CHECKING:
    from stock_manager import App


class Remove(AbstractController):
    """
    Controller for the 'Remove' page of the stock management application.
    
    Handles user interactions for searching and removing stock items
    from the database.
    """
    
    def __init__(self, app: 'App'):
        """
        Initialize the Remove page.
        
        :param app: Reference to the main application instance.
        """
        
        page = stock_manager.utils.Pages.REMOVE
        super().__init__(page.value.FILE_NAME, app)
        self.PAGE_NAME = page
        self.handle_connections()
    
    @override
    def handle_connections(self) -> None:
        import qtawesome as qta
        
        self.table.clicked.connect(self._on_cell_clicked)
        
        self.search_icon.setIcon(qta.icon('fa5s.search'))
    
    def _on_cell_clicked(self, index: QModelIndex) -> None:
        """
        Confirms and deletes item after user confirmation
        when a table row is clicked.
        
        :param index: The index of the clicked table cell as a `QModelIndex`.
        """
        
        row = index.row()
        selected_item = self.app.all_items[row]
        
        response = QMessageBox.question(
                self,
                'Item Removal Confirmation',
                f'Are You Sure You Want To Remove {selected_item.part_num} '
                'From The Database?\n\nThis Action Cannot Be Undone.',
                QMessageBox.Yes,
                QMessageBox.No
        )
        
        if response == QMessageBox.Yes:
            self.app.all_items.remove(selected_item)
            self.logger.info(f'{self.app.user} Removed Item From Database: {selected_item.part_num}')
            self.app.update_tables()
            self.database.update_items_database(stock_manager.utils.DatabaseUpdateType.REMOVE, selected_item)
