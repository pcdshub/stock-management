"""
Database utilities for Stock Management Application.

Provides DBUtils for connecting to and retrieving data from Google Sheets.
"""

import os.path
from pathlib import Path

import gspread
from gspread import Client
from oauth2client.service_account import ServiceAccountCredentials

from .logger import Logger


class DBUtils:
	"""Utility class for interacting with a Google Sheets database."""
	
	def __init__(self):
		"""Initializes the Google Sheets client using credentials from a JSON keyfile."""
		
		base_dir = Path(__file__).resolve().parent.parent.parent
		credentials_path = os.path.join(base_dir, 'assets', 'gs_credentials.json')
		
		scope = [
			"https://spreadsheets.google.com/feeds",
			"https://www.googleapis.com/auth/spreadsheets",
			"https://www.googleapis.com/auth/drive.file",
			"https://www.googleapis.com/auth/drive"
		]
		
		credentials: ServiceAccountCredentials = ServiceAccountCredentials.from_json_keyfile_name(
				str(credentials_path),
				scope
		)
		self._client: Client = gspread.authorize(credentials)
		
		self._log = Logger()
		self._file_name = 'Stock Management Sheet'
		self._sheet = self._client.open(self._file_name).sheet1
	
	def get_all_data(self) -> list[dict[str, int | float | str]]:
		"""
		Retrieves all records from the first worksheet of the 'Stock Management Sheet'.
		
		Raises RuntimeError if fetching data from Google Sheets fails.
		
		:return: List of dictionaries, each representing a row from the sheet.
		"""
		try:
			return self._sheet.get_all_records()
		except Exception as e:
			self._log.error_log(f"Error in get_all_data: Failed to fetch data from {self._file_name}. Exception: {e}")
			raise RuntimeError
	
	def get_all_users(self) -> list[str]:  # todo: possibly make user objects out of data
		"""Retrieve a list of all users from the database."""
		return ['QR_USERNAME']  # todo: handle getting usernames from database
	
	def update_database(self) -> None:
		"""Update the database with the latest changes or synchronize its contents."""
		pass  # todo: handle update database
