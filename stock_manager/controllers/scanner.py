"""
Scanner Controller Classes For Camera Functionality

This module defines multiple classes related to QR code scanning functionality.
Each class provides a different implementation or specialization for handling
camera input, processing frames, and integrating QR scanning into different
parts of the application.
"""

from typing import override, TYPE_CHECKING

import cv2
from numpy import ndarray
from PyQt6.QtWidgets import QMessageBox
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
	
	@override
	@asyncSlot()
	async def check_for_qr(self, frame: ndarray) -> None:
		"""
		Scans the current frame for an item QR code, adding it to an
		internal list to be used when submitting a form and updating the UI.
		
		:param frame: Current video frame as a numpy ndarray.
		"""
		
		data, _, _ = cv2.QRCodeDetector().detectAndDecode(frame)
		if not data or data in [item.part_num for item in self._items]:
			return
		
		self.logger.info_log(f'{self.app.user} Scanned Item QR Code: {data}')
		
		for item in self.app.all_items:
			if data == item.part_num:
				self._items.append(item)
				self.logger.info_log(f'{self.app.user} Added {data} To Items List')
				self.items_list.append(f'<ul><li>{data}</li></ul>')
				return
		
		print(f'Item QR Code Not Recognized: "{data}"')
		self.logger.info_log(f'Item QR Code Not Recognized: "{data}"')
		QMessageBox.information(
				self,
				'Unknown QR Code',
				'QR Code Not Recognized In Database',
				QMessageBox.StandardButton.Ok
		)
	
	def _clear_form(self) -> None:
		"""Clears all fields in the scanner UI form and resets the scanned item list."""
		
		self.logger.info_log(f'{self.app.user} Cleared Items List')
		self._items.clear()
		self.items_list.clear()
	
	def _finish_form(self) -> None:
		"""Handles the completion of a scanning session and navigates to the finish screen."""
		
		if not self._items:
			QMessageBox.critical(
					self,
					'Item Required',
					'Please Scan At Least One Item',
					QMessageBox.StandardButton.Ok
			)
			return
		
		string_items = ''.join(f'\n{item.part_num}' for item in self._items)
		
		response = QMessageBox.question(
				self,
				'Item Checkout Confirmation',
				'Are You Sure You Want To Checkout Items:\n' + string_items,
				QMessageBox.StandardButton.Yes,
				QMessageBox.StandardButton.No
		)
		
		if response == QMessageBox.StandardButton.No:
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
						print('Neither Radio Button Is Selected')
						QMessageBox.information(
								self,
								'Radio Button Error',
								'Neither Radio Button Is Selected, '
								'Please Select A Radio Button Before Submitting Form',
								QMessageBox.StandardButton.Ok
						)
						return
					
					item.update_stats()
					if item.excess <= 0:
						pass  # TODO: handle alert send for specified item
					
					break
			
			self.app.update_tables()
			self.database.update_database(stock_manager.DatabaseUpdateType.EDIT, self._items)
		except Exception as e:
			print(f'Item(s) Could Not Be Subtracted From Database: {e}')
			self.logger.error_log(f'Item(s) Could Not Be Subtracted From Database: {e}')
			self.app.finish.set_text('An Error Occurred, Item(s) Could Not Be Subtracted From Database.')
		else:
			length = len(self._items)
			self.app.finish.set_text(
					f'{"1 item has" if length == 1 else f"{length} items have"} '
					f'successfully been subtracted from database.'
			)
			self.logger.info_log(f'{self.app.user} Checked Out Items: {string_items}')
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
		self._users_list = self.database.get_all_users()
		self.handle_connections()
	
	@override
	def handle_connections(self) -> None:
		self.login_btn.clicked.connect(self._login_clicked)
	
	@override
	def to_page(self) -> None:
		"""Navigate to this login page, logging out, and hiding sidebar."""
		
		self.app.sideUI.hide()
		user = self.app.user
		if user:
			print(f'User Logged Out As: {user}')
			self.logger.info_log(f'User Logged Out As: {user}')
			self.app.user = ''
		super().to_page()
	
	@override
	@asyncSlot()
	async def check_for_qr(self, frame: ndarray) -> None:
		"""
		Scans the current frame for a user QR code, logging them in if valid.
		
		:param frame: Current video frame as a numpy ndarray.
		"""
		
		data, _, _ = cv2.QRCodeDetector().detectAndDecode(frame)
		if not data or self.app.user:
			return
		
		self.logger.info_log(f'QR Code Scanned: {data}')
		
		if data in self._users_list:
			self._finish_login(data)
			return
		
		print(f'QR Code Not Recognized: "{data}"')
		self.logger.info_log(f'QR Code Not Recognized: "{data}"')
		QMessageBox.information(
				self,
				'Unknown QR Code',
				'QR Code Not Recognized In Database',
				QMessageBox.StandardButton.Ok
		)
	
	def _login_clicked(self) -> None:
		"""Checks if the user entered a valid username and logs them in if valid."""
		
		text = self.username.text().strip()
		
		if text in [None, '']:
			QMessageBox.information(
					self,
					'Empty Field',
					'Please Fill Out Login Field Before Submitting',
					QMessageBox.StandardButton.Ok
			)
			return
		
		if text in self._users_list:
			self._finish_login(text)
			return
		
		print(f'Username Not Recognized: "{text}"')
		self.logger.info_log(f'Username Not Recognized: "{text}"')
		QMessageBox.information(
				self,
				'Unknown Username Entered',
				'Entered Username Not Recognized In Database',
				QMessageBox.StandardButton.Ok
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
		print(f'User Logged In As: {username}')
		self.logger.info_log(f'User Logged In As: {username}')
		self.app.view.to_page()
		self.stop_video()
		self.username.clear()
		self.app.sideUI.show()
