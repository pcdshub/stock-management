"""
Database utilities for Stock Management Application.

Provides DBUtils for connecting to and getting/setting data from/to Google Sheets.
"""

import os.path
from pathlib import Path
from typing import Iterable, TYPE_CHECKING

import gspread
from gspread import Cell, Spreadsheet, Worksheet
from oauth2client.service_account import ServiceAccountCredentials
from PyQt6.QtWidgets import QMessageBox

if TYPE_CHECKING:
	from stock_manager import Item, DatabaseUpdateType


class DBUtils:
	"""Utility class for interacting with a Google Sheets database."""
	
	def __init__(self) -> None:
		"""
		Initializes the Google Sheets client using credentials from a JSON keyfile.
		
		:raises SystemExit: If the database fails to load
		"""
		
		from .logger import Logger
		
		base_dir = Path(__file__).resolve().parent.parent.parent
		credentials_path = os.path.join(base_dir, 'assets', 'gs_credentials.json')
		
		scope = [
			'https://spreadsheets.google.com/feeds',
			'https://www.googleapis.com/auth/spreadsheets',
			'https://www.googleapis.com/auth/drive.file',
			'https://www.googleapis.com/auth/drive'
		]
		
		try:
			credentials: ServiceAccountCredentials = ServiceAccountCredentials.from_json_keyfile_name(
					str(credentials_path),
					scope
			)
			
			self._log = Logger()
			self._file_name = 'Stock Management Sheet'
			self._client: Spreadsheet = gspread.authorize(credentials).open(self._file_name)
		except Exception as e:
			print(f'Failed To Connect To Database: {e}')
			Logger().error_log(f'Failed To Connect To Database: {e}')
			QMessageBox.critical(
					None,
					'Database Connection Failure',
					'Failed To Connect To Database, Try Restarting The Application',
					QMessageBox.StandardButton.Ok
			)
			raise SystemExit(1)
	
	def get_all_data(self) -> list[dict[str, int | float | str]]:
		"""
		Retrieves all records from the first worksheet of the 'Stock Management Sheet'.
		
		:return: List of dictionaries, each representing a row from the sheet.
		:raises SystemExit: If user chooses to close application after fetching data from Google Sheets fails.
		"""
		
		try:
			return self._client.worksheet('Parts').get_all_records()
		except Exception as e:
			print(f'Failed To Fetch All Data From {self._file_name} Database: {e}')
			self._log.error_log(f'Failed To Fetch All Data From {self._file_name}: {e}')
			response = QMessageBox.critical(
					None,
					'Data Fetching Error',
					f'Failed To Fetch All Data From {self._file_name}.\n\n'
					'Continue To Application?',
					QMessageBox.StandardButton.Yes,
					QMessageBox.StandardButton.Close
			)
			
			if response == QMessageBox.StandardButton.Close:
				raise SystemExit(1)
	
	def get_all_users(self) -> set[str]:  # TODO: possibly make user objects out of data
		"""
		Retrieves a set of all users from the database.
		
		:return: A set of strings representing all the usernames in the database
		:raises SystemExit: If user fetch from database fails
		"""
		
		try:
			return {
				str(user)
				for user in self._client.worksheet('Users').col_values(1)
			}
		except Exception as e:
			print(f'Failed To Get All Users From {self._file_name}: {e}')
			self._log.error_log(f'Failed To Get All Users From {self._file_name}: {e}')
			QMessageBox.critical(
					None,
					'User Fetch Error',
					'Failed To Fetch Users From Database',
					QMessageBox.StandardButton.Close
			)
			raise SystemExit(1)
	
	def update_database(
			self,
			update_type: 'DatabaseUpdateType',
			changelist: Iterable['Item'] | 'Item'
	) -> None:
		"""
		Update the database with the latest changes
		
		:param update_type: The type of database update as a `DatabaseUpdateType` enum (e.g. `ADD`, `EDIT`, `REMOVE`)
		:param changelist: An iterable list of items to repeat the same process or a single item
		"""
		
		from stock_manager import DatabaseUpdateType
		
		sheet: Worksheet = self._client.worksheet('Parts')
		if not isinstance(changelist, list):
			changelist = [changelist]
		
		for item in changelist:
			match update_type:
				case DatabaseUpdateType.ADD:
					try:
						sheet.append_row([value for value in item])
					except Exception as e:
						print(f'Error Adding "{item.part_num}" To Database: {e}')
						self._log.error_log(f'Error Adding "{item.part_num}" To Database: {e}')
						QMessageBox.critical(
								None,
								'Database Add Item Error',
								f'Error Adding "{item.part_num}" To Database.',
								QMessageBox.StandardButton.Ok
						)
				case DatabaseUpdateType.EDIT:
					try:
						cell: Cell | None = sheet.find(item.part_num)
						if cell:
							for i, value in enumerate(item):
								sheet.update_cell(cell.row, i + 1, value)
							continue
					except Exception as e:
						print(f'Error Editing "{item.part_num}" In Database: {e}')
						self._log.error_log(f'Error Editing "{item.part_num}" In Database: {e}')
						QMessageBox.critical(
								None,
								'Database Edit Item Error',
								f'Error Editing "{item.part_num}" In Database.',
								QMessageBox.StandardButton.Ok
						)
					else:
						QMessageBox.warning(
								None,
								'Database Update Item Warning',
								f'Cannot Update Item: "{item.part_num}" '
								f'Because It Does Not Exist In Database',
								QMessageBox.StandardButton.Ok
						)
				case DatabaseUpdateType.REMOVE:
					try:
						cell: Cell | None = sheet.find(item.part_num)
						if cell:
							sheet.delete_rows(cell.row)
							continue
					except Exception as e:
						print(f'Error Deleting "{item.part_num}" From Database: {e}')
						self._log.error_log(f'Error Deleting "{item.part_num}" From Database: {e}')
						QMessageBox.critical(
								None,
								'Database Delete Item Error',
								f'Error Deleting "{item.part_num}" From Database.',
								QMessageBox.StandardButton.Ok
						)
					else:
						QMessageBox.warning(
								None,
								'Database Delete Item Warning',
								f'Cannot Delete Item: "{item.part_num}" '
								f'Because It Does Not Exist In Database',
								QMessageBox.StandardButton.Ok
						)
				case _ as unknown:
					QMessageBox.critical(
							None,
							'Unknown Database Update Type',
							f'Unknown Database Update Type: "{unknown}", '
							'Only Use stock_manager.DatabaseUpdateType Enums When Updating Database',
							QMessageBox.StandardButton.Ok
					)
