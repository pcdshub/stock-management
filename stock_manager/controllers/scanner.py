"""
Scanner Controller Classes For Camera Functionality

This module defines multiple classes related to QR code scanning functionality.
Each class provides a different implementation or specialization for handling
camera input, processing frames, and integrating QR scanning into different
parts of the application.
"""

from typing import override, TYPE_CHECKING

import cv2
import qtawesome as qta
from numpy import ndarray
from PyQt5.QtWidgets import QMessageBox
from qasync import asyncSlot

import stock_manager
from .abstract import AbstractScanner

if TYPE_CHECKING:
    from stock_manager import App, Item


class ItemScanner(AbstractScanner):
    """
    Controller for the 'QR Scan' page of the stock management application.
    
    Handles decoding of Item QR codes and form functionality.
    """
    
    def __init__(self, app: 'App'):
        """
        Initializes the QR Scan page.
        
        :param app: Reference to the main application instance.
        """
        
        page = stock_manager.Pages.SCAN
        super().__init__(page.value.FILE_NAME, app)
        self.PAGE_NAME = page
        self._items: list[Item] = []
        self.handle_connections()
    
    @override
    def handle_connections(self) -> None:
        self.clear_btn.clicked.connect(self._clear_form)
        self.done_btn.clicked.connect(self._finish_form)
        
        qta.set_defaults(color='white')
        self.clear_btn.setIcon(qta.icon('fa5s.backspace'))
        self.done_btn.setIcon(qta.icon('fa5s.check-square'))
    
    @override
    @asyncSlot()
    async def check_for_qr(self, frame: ndarray) -> bool:
        """
        Scans the current frame for an item QR code, adding it to an
        internal list to be used when submitting a form and updating the UI.
        
        :param frame: Current video frame as a numpy ndarray.
        :return: True if the QR code scanned is successfully added to the
        scanned items list or is already in the scanned items list, False
        if no QR code is detected or if the scanned QR code is not recognized
        in the database.
        """
        
        data, _, _ = cv2.QRCodeDetector().detectAndDecode(frame)
        
        if not data:
            return False
        
        if data in [item.part_num for item in self._items]:
            return True
        
        self.logger.info(f'{self.app.user} Scanned Item QR Code: {data}')
        
        for item in self.app.all_items:
            if data == item.part_num:
                self._items.append(item)
                self.logger.info(f'{self.app.user} Added {data} To Items List')
                self.items_list.append(f'<ul><li>{data}</li></ul>')
                return True
        
        self.logger.warning(f'Item QR Code Not Recognized: "{data}"')
        QMessageBox.warning(
                self,
                'Unknown QR Code',
                'QR Code Not Recognized In Database'
        )
        return False
    
    def _clear_form(self) -> None:
        """Clears all fields in the scanner UI form and resets the scanned item list."""
        
        self.logger.info(f'{self.app.user} Cleared Items List')
        self._items.clear()
        self.items_list.clear()
    
    def _finish_form(self) -> None:
        """Handles the completion of a scanning session and navigates to the finish screen."""
        
        if not self._items:
            QMessageBox.critical(
                    self,
                    'Item Required',
                    'Please Scan At Least One Item'
            )
            return
        
        string_items = ''.join(f'\n{item.part_num}' for item in self._items)
        
        response = QMessageBox.question(
                self,
                'Item Checkout Confirmation',
                'Are You Sure You Want To Checkout Items:\n' + string_items,
                QMessageBox.Yes,
                QMessageBox.No
        )
        
        if response == QMessageBox.No:
            return
        
        try:
            for _item in self._items:
                for item in self.app.all_items:
                    if not _item == item:
                        continue
                    
                    if self.b750_btn.isChecked():
                        item.stock_b750 -= 1
                    elif self.b757_btn.isChecked():
                        item.stock_b757 -= 1
                    else:
                        self.logger.warning('Neither Radio Button Is Selected')
                        QMessageBox.warning(
                                self,
                                'Radio Button Error',
                                'Neither Radio Button Is Selected, '
                                'Please Select A Radio Button Before Submitting Form'
                        )
                        return
                    
                    item.update_stats()
                    if item.stock_b750 + item.stock_b757 <= 0:
                        from datetime import datetime
                        msg = ('Hello,\n\n'
                               
                               'This is an automatic notification detailing that '
                               'the following item has reached a total stock of 0:\n'
                               f'\tItem: {item.part_num}\n'
                               f'\tDescription: {item.description}\n'
                               f'\tExcess Count: {item.excess} ({item.stock_status})\n'
                               f'\tDate/Time: {datetime.now()}\n\n'
                               
                               'Please take any necessary action to reorder or restock.\n\n'
                               
                               'Best regards,\n'
                               'Stock Management System')
                        
                        self.database.add_notification(item.part_num)
                        # stock_manager.send_email(msg, self)
                    break
            
            self.app.update_tables()
            self.database.update_items_database(stock_manager.DatabaseUpdateType.EDIT, self._items)
        except Exception as e:
            self.logger.error(f'Item(s) Could Not Be Subtracted From Database: {e}')
            self.app.finish.set_text('An Error Occurred, Item(s) Could Not Be Subtracted From Database.')
        else:
            length = len(self._items)
            self.app.finish.set_text(
                    f'{"1 item has" if length == 1 else f"{length} items have"} '
                    f'successfully been subtracted from database.'
            )
            self.logger.info(f'{self.app.user} Checked Out Items: {string_items}')
            self._clear_form()
        finally:
            self.app.finish.to_page()


class Login(AbstractScanner):
    """
    Controller for the 'Login' page of the stock management application.
    
    Handles the login functionality for both user QR code scan and the login form.
    """
    
    def __init__(self, app: 'App'):
        """
        Initializes the Login page.
        
        :param app: Reference to the main application instance.
        """
        
        page = stock_manager.Pages.LOGIN
        super().__init__(page.value.FILE_NAME, app)
        self.PAGE_NAME = page
        self._users_list = self.database.get_all_users_gs()
        self.handle_connections()
    
    @override
    def handle_connections(self) -> None:
        self.login_btn.clicked.connect(self._login_clicked)
        self.username.returnPressed.connect(self._login_clicked)
        
        self.login_btn.setIcon(qta.icon('fa6s.right-to-bracket', color='white'))
    
    @override
    def to_page(self) -> None:
        """Navigate to this login page, logging out, and hiding sidebar."""
        
        self.app.sideUI.hide()
        user = self.app.user
        if user:
            self.logger.info(f'User Logged Out As: {user}')
            self.app.user = ''
        super().to_page()
    
    @override
    @asyncSlot()
    async def check_for_qr(self, frame: ndarray) -> bool:
        """
        Scans the current frame for a user QR code, logging them in if valid.
        
        :param frame: Current video frame as a numpy ndarray.
        :return: True if the QR code scanned is valid and the user can
        be logged in, False if no QR code is detected or if the scanned
        QR code is not recognized in the database.
        """
        
        data, _, _ = cv2.QRCodeDetector().detectAndDecode(frame)
        if not data or self.app.user:
            return False
        
        self.logger.info(f'QR Code Scanned: {data}')
        
        if data in self._users_list:
            self._finish_login(data)
            return True
        
        self.logger.warning(f'QR Code Not Recognized: "{data}"')
        QMessageBox.warning(
                self,
                'Unknown QR Code',
                'QR Code Not Recognized In Database'
        )
        return False
    
    def _login_clicked(self) -> None:
        """Checks if the user entered a valid username and logs them in if valid."""
        
        text = self.username.text().strip()
        
        if text in [None, '']:
            QMessageBox.information(
                    self,
                    'Empty Field',
                    'Please Fill Out Login Field Before Submitting'
            )
            return
        
        if text in self._users_list:
            self._finish_login(text)
            return
        
        self.logger.warning(f'Username Not Recognized: "{text}"')
        QMessageBox.warning(
                self,
                'Unknown Username Entered',
                'Entered Username Not Recognized In Database'
        )
    
    def _finish_login(self, username) -> None:
        """
        Finalizing the login process after either scanning a
        user QR code or entering a username.
        
        Sets the currently logged-in user and navigates
        to `view.ui` and `view.py`.
        
        :param username: the username of the newly logged-in user
        """
        
        self.app.user = username
        self.logger.info(f'User Logged In As: {username}')
        self.app.view.to_page()
        self.stop_video()
        self.username.clear()
        self.app.sideUI.show()
