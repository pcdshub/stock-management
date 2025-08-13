"""
View controller for displaying inventory data in the Stock Management Application.

Handles the main table display and navigation to the export page.
"""

from typing import override, TYPE_CHECKING

import stock_manager
from stock_manager.controllers import AbstractController

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
        
        page = stock_manager.utils.Pages.VIEW
        super().__init__(page.value.FILE_NAME, app)
        self.PAGE_NAME = page
        self.handle_connections()
    
    @override
    def handle_connections(self) -> None:
        import qtawesome as qta
        
        self.export_btn.clicked.connect(lambda: self.app.export.to_page())  # keep as lambda because of connect()
        
        self.export_btn.setIcon(qta.icon('fa5s.file-export', color='white'))
        self.search_icon.setIcon(qta.icon('fa5s.search'))
