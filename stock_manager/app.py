"""
Instantiate and run the App class to start the SLAC Inventory Management application.
"""

import asyncio
from pathlib import Path
from typing import override

from PyQt5.QtGui import QCloseEvent, QFont
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QPushButton, QStackedWidget
from PyQt5.uic import loadUi
from qasync import asyncSlot

import stock_manager
from stock_manager.model import Item


class App(QMainWindow):
    """
    Main application window for SLAC Inventory Management.
    
    Handles UI loading, screen transitions, and application startup/shutdown events.
    """
    
    def __init__(self):
        """
        Initialize the main application window and setup screens.
        
        Creates instances of each controller and utility files.
        
        :raises SystemExit: If the main UI fails to load
        """
        
        from stock_manager import DBUtils, Logger, ExportUtils, Login, View, Add, Export, Edit, Remove, QRGenerate, \
            Finish, ItemScanner
        
        super().__init__()
        
        self.log = Logger()
        self.db = DBUtils()
        self.export_utils = ExportUtils(self)
        
        self.login = Login(self)
        self.view = View(self)
        self.scanner = ItemScanner(self)
        self.add = Add(self)
        self.edit = Edit(self)
        self.remove = Remove(self)
        self.generate = QRGenerate(self)
        self.export = Export(self)
        self.finish = Finish(self)
        
        self.controllers: list[stock_manager.AbstractController] = [
            self.view, self.scanner,
            self.add, self.edit, self.remove,
            self.generate, self.login,
            self.export, self.finish
        ]
        
        self.user = ''
        self.all_items: list[Item] = []
        self.screens: QStackedWidget | None = None
        self.current_page: stock_manager.Pages | None = None
        
        try:
            ui_path: Path = Path(__file__).resolve().parent.parent / 'ui' / 'main.ui'
            loadUi(str(ui_path), self)
        except Exception as e:
            print(f'Failed To Load Main UI File: {e}')
            self.log.error_log(f'Failed To Load Main UI File: {e}')
            QMessageBox.critical(
                    self,
                    'UI Failure',
                    'Failed To Load Main UI File'
            )
            raise SystemExit(1)
        
        self.buttons: list[QPushButton] = [
            self.view_btn,
            self.qr_btn,
            self.add_btn,
            self.edit_btn,
            self.remove_btn,
            self.generate_btn,
            self.log_out_btn
        ]
        
        for screen in self.controllers:
            self.screens.addWidget(screen)
        
        self.handle_connections()
    
    def handle_connections(self) -> None:
        """
        Connects sidebar buttons to the appropriate screen
        navigation actions and connects application shortcuts
        to a controllers `to_page()` method.
        """
        
        button: QPushButton
        controller: stock_manager.AbstractController
        enum: stock_manager.Pages
        for button, controller, enum in zip(self.buttons, self.controllers, stock_manager.Pages):
            if not isinstance(button, QPushButton):
                continue
            
            button.clicked.connect(controller.to_page)
            button.setShortcut(str(enum.value.PAGE_INDEX))
        
        self.screens.currentChanged.connect(self._on_page_changed)
        self.actionToggle_Maximize.triggered.connect(self.toggle_maximize)
        self.actionEscape_Maximize.triggered.connect(self.escape_maximize)
        self.actionMinimize.triggered.connect(self.minimize)
        self.actionSearch.triggered.connect(self.search)
        self.actionLog_Out.triggered.connect(self.login.to_page)
        self.actionClose_Application.triggered.connect(self.close)
        
        def handle_icons():
            import qtawesome as qta
            
            qta.set_defaults(color='black')
            
            self.actionToggle_Maximize.setIcon(qta.icon('mdi.fullscreen'))
            self.actionEscape_Maximize.setIcon(qta.icon('mdi.fullscreen-exit'))
            self.actionMinimize.setIcon(qta.icon('fa5s.minus'))
            self.actionSearch.setIcon(qta.icon('fa5s.search'))
            self.actionLog_Out.setIcon(qta.icon('fa5s.sign-out-alt'))
            self.actionClose_Application.setIcon(qta.icon('fa5s.power-off'))
            
            qta.set_defaults(color='white')
            
            self.view_btn.setIcon(qta.icon('fa5s.table'))
            self.qr_btn.setIcon(qta.icon('fa5s.video'))
            self.add_btn.setIcon(qta.icon('fa5s.plus-square'))
            self.edit_btn.setIcon(qta.icon('fa5s.edit'))
            self.remove_btn.setIcon(qta.icon('fa5s.minus-square'))
            self.generate_btn.setIcon(qta.icon('fa5s.qrcode'))
            self.log_out_btn.setIcon(qta.icon('fa5s.sign-out-alt', color='white'))
        
        handle_icons()
    
    def run(self) -> None:
        """
        Start the application workflow.
        
        Navigates to the login page, triggers the page change handler,
        and begins any asynchronous loading.
        """
        
        self.log.info_log('App Started')
        self.login.to_page()
        self._on_page_changed()
        self._async_load()
    
    @asyncSlot()
    async def _async_load(self) -> None:
        """
        Asynchronously load data from the database and update the application tables.
        
        :raises SystemExit: If the user chooses to close the application after a data load failure.
        """
        
        def create_all_items(gs_items: list[dict[str, int | float | str]]) -> list[Item]:
            """
            Convert a list dictionaries (Google Sheet Columns) to a list of `Item` objects
            
            :param gs_items: A list of Google Sheet columns
            :return: a list of `Item` objects
            """
            
            obj_items: list[Item] = []
            for item in gs_items:
                vals: list[int | float | str | None] = [
                    None if val is None or val == ''
                    else val
                    for val in list(item.values())
                ]
                obj_items.append(Item(*vals))
            return obj_items
        
        try:
            self.all_items = create_all_items(self.db.get_all_data())
            await self.update_tables()
        except Exception as e:
            print(f'Error Loading Data Asynchronously: {e}')
            self.log.error_log(f'Could not load data from database: {e}')
            response = QMessageBox.critical(
                    self,
                    'Data Load Failure',
                    'Failed To Load Data From Database',
                    QMessageBox.Ok,
                    QMessageBox.Close
            )
            
            if response == QMessageBox.Close:
                raise SystemExit(1)
    
    def _on_page_changed(self) -> None:
        """Update window title and manage QR scanner based on current screen."""
        
        if self.scanner.camera_thread.running and \
                self.screens.currentIndex() != stock_manager.Pages.SCAN.value.PAGE_INDEX:
            try:
                self.scanner.stop_video()
            except Exception as e:
                print(f'Failed To Stop QR Scanner: {e}')
                self.log.error_log(f'Failed To Stop QR Scanner: {e}')
                QMessageBox.critical(
                        self,
                        'QR Scanner Error',
                        'Failed To Stop QR Scanner'
                )
        
        def bold_current_screen_button() -> None:
            """Update sidebar buttons' font to indicate the currently active screen."""
            
            from stock_manager import SIDEBAR_BUTTON_SIZE
            
            idx = self.screens.currentIndex()
            
            active = QFont()
            active.setPointSize(SIDEBAR_BUTTON_SIZE)
            active.setBold(True)
            inactive = QFont()
            inactive.setPointSize(SIDEBAR_BUTTON_SIZE)
            
            i: int
            button: QPushButton
            for i, button in enumerate(self.buttons):
                button.setFont(active if i == idx else inactive)
        
        bold_current_screen_button()
    
    @override
    def closeEvent(self, event: QCloseEvent) -> None:
        """Handle the application close event and log exit."""
        
        self.log.info_log('App Exited\n')
        super().closeEvent(event)
    
    @asyncSlot()
    async def update_tables(self) -> None:
        """
        Refreshes or updates the displayed tables in the UI to reflect the latest inventory data.
        
        This method should be called after making changes to the inventory or data source.
        """
        
        await asyncio.gather(
                *(
                    controller.update_table()
                    for controller in self.controllers
                    if isinstance(controller, stock_manager.AbstractController) and hasattr(controller, 'table')
                )
        )
    
    def toggle_maximize(self) -> None:
        """Toggles maximization of the application window."""
        
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()
    
    def escape_maximize(self) -> None:
        """Returns window to windowed state if application is maximized."""
        
        if self.isMaximized():
            self.showNormal()
    
    def minimize(self) -> None:
        """Minimizes the application window to the taskbar."""
        
        self.showMinimized()
    
    def search(self) -> None:
        """
        Focuses current page's search bar if one is present.
        
        If a search bar is not present, application navigates
        to `view.ui` and focuses `search` there.
        """
        
        if not self.user:
            return
        
        controller = self.controllers[self.current_page.value.PAGE_INDEX]
        if hasattr(controller, 'search'):
            controller.search.setFocus()
            return
        
        self.view.to_page()
        self.view.search.setFocus()
