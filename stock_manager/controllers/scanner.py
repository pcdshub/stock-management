from typing import override, TYPE_CHECKING

import cv2
from numpy import ndarray
from PyQt6.QtWidgets import QMessageBox
from qasync import asyncSlot

from .abstract import AbstractScanner

if TYPE_CHECKING:
	from stock_manager import App, Item


class ItemScanner(AbstractScanner):
	"""QR Scanner UI controller for capturing video and decoding Item QR codes."""
	
	def __init__(self, app: 'App'):
		"""
		Initializes the scanner UI.
		
		:param app: Reference to the main application instance.
		"""
		
		super().__init__('scanner', app)
		
		self._items: set[Item] = set()
		self.PAGE_INDEX = 2
		
		self.handle_connections()
	
	@override
	def handle_connections(self) -> None:
		self.clear_btn.clicked.connect(self._clear_form)
		self.done_btn.clicked.connect(self._finish_form)
	
	@override
	@asyncSlot()
	async def check_for_qr(self, frame: ndarray) -> None:
		"""
		Scans the current frame for a QR code and logs if found.
		
		:param frame: Current video frame as a numpy ndarray.
		"""
		
		data, _, _ = cv2.QRCodeDetector().detectAndDecode(frame)
		if not data or data in [item.part_num for item in self._items]:
			return
		
		self.logger.info_log(f"QR Code Scanned: {data}")
		
		for item in self.app.all_items:
			if data == item.part_num:
				self._items.add(item)
				self.logger.info_log(f'{data} Added To Items List')
				self.items_list.append(f'<ul><li>{data}</li></ul>')
				return
		
		print(f'QR Code Not Recognized: "{data}"')
		self.logger.info_log(f'QR Code Not Recognized: "{data}"')
		QMessageBox.information(
				self,
				'Unknown QR Code',
				'QR Code Not Recognized In Database',
				QMessageBox.StandardButton.Ok
		)
	
	def _clear_form(self) -> None:
		"""Clears all fields in the scanner UI form and resets the scanned item list."""
		
		self.logger.info_log('Items List Cleared')
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
		
		string_items = ''.join(f'{item.part_num}\n' for item in self._items)
		
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
						print("Neither Radio Button Is Selected")
						raise ValueError("Neither Radio Button Is Selected")
					
					item.update_stats()
					if item.excess <= 0:
						pass  # TODO: handle alert send for specified item
					
					break
			
			self.app.update_tables()
			self.database.update_database()
		except Exception as e:
			print(f'Item(s) Could Not Be Subtracted From Database: {e}')
			self.logger.error_log(f'Item(s) Could Not Be Subtracted From Database: {e}')
			self.app.finish.set_text('An Error Occurred, Item(s) Could Not Be Subtracted From Database.')
		else:
			length = len(self._items)
			self.app.finish.set_text(
					f"{'1 item has' if length == 1 else f'{length} items have'} "
					f"successfully been subtracted from database."
			)
			self.logger.info_log(f'{self.app.user} has checked out items:\n{string_items}')
			self._clear_form()
		finally:
			self.app.finish.to_page()


class Login(AbstractScanner):
	"""QR Scanner UI controller for capturing video and decoding User QR codes."""

	def __init__(self, app: 'App'):
		super().__init__('login', app)
		
		self._users_list = self.database.get_all_users()  # get user list from JIRA or database
		self.PAGE_INDEX = 0
		
		self.handle_connections()
	
	@override
	def handle_connections(self) -> None:
		pass
	
	@override
	@asyncSlot()
	async def check_for_qr(self, frame: ndarray) -> None:
		data, _, _ = cv2.QRCodeDetector().detectAndDecode(frame)
		if not data or self.app.user:
			return
		
		self.logger.info_log(f"QR Code Scanned: {data}")
		
		if data not in self._users_list:
			print(f'QR Code Not Recognized: "{data}"')
			self.logger.info_log(f'QR Code Not Recognized: "{data}"')
			QMessageBox.information(
					self,
					'Unknown QR Code',
					'QR Code Not Recognized In Database',
					QMessageBox.StandardButton.Ok
			)
			return
		
		self.app.user = data
		print(f'User Logged In As: {data}')
		self.logger.info_log(f'User Logged In As: {data}')
		self.app.view.to_page()
		self.stop_video()
