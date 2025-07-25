"""
Database utilities for Stock Management Application.

Provides DBUtils for connecting to and getting/setting data from/to Google Sheets.
"""

import logging
import os.path
from pathlib import Path
from typing import Iterable, TYPE_CHECKING

import gspread
import mysql.connector
from gspread import Cell, Spreadsheet, Worksheet
from mysql.connector.abstracts import MySQLConnectionAbstract, MySQLCursorAbstract
from oauth2client.service_account import ServiceAccountCredentials
from PyQt5.QtWidgets import QMessageBox

import stock_manager

if TYPE_CHECKING:
    from stock_manager import Item, DatabaseUpdateType


class DBUtils:
    """Utility class for interacting with a Google Sheets database."""
    
    def __init__(self) -> None:
        """
        Initializes the Google Sheets client using credentials from a JSON keyfile.
        
        :raises SystemExit: If the database fails to load
        """
        
        base_dir = Path(__file__).resolve().parent.parent.parent
        credentials_path = os.path.join(base_dir, 'assets', 'gs_credentials.json')
        
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive.file',
            'https://www.googleapis.com/auth/drive'
        ]
        
        self._log = logging.getLogger()
        
        try:
            credentials: ServiceAccountCredentials = ServiceAccountCredentials.from_json_keyfile_name(
                    str(credentials_path),
                    scope
            )
            self._client: Spreadsheet = gspread.authorize(credentials).open(stock_manager.GS_FILE_NAME)
            
            self._db: MySQLConnectionAbstract = mysql.connector.connect(
                    host='localhost',
                    user='root',
                    password='password',
                    database='common_stock'
            )
            self._cursor: MySQLCursorAbstract = self._db.cursor(dictionary=True)
        except Exception as e:
            print(f'Failed To Connect To Database: {e}')
            self._log.error(f'Failed To Connect To Database: {e}')
            QMessageBox.critical(
                    None,
                    'Database Connection Failure',
                    'Failed To Connect To Database, Make Sure You Have An Internet Connection'
            )
            raise SystemExit(1)
    
    def get_headers(self) -> list[str]:
        """
        Retrieves the headers of the 'Parts' worksheet of the 'Stock Management Sheet'.
        
        :return: A list of strings containing the headers of the worksheet
        """
        
        try:
            return self._client.worksheet('Parts').row_values(1)
        except Exception as e:
            print(f'Failed To Fetch Sheet Headers From {stock_manager.GS_FILE_NAME} Database: {e}')
            self._log.error(f'Failed To Fetch Sheet Headers From {stock_manager.GS_FILE_NAME} Database: {e}')
            QMessageBox.critical(
                    None,
                    'Header Fetching Error',
                    f'Failed To Fetch Sheet Headers From {stock_manager.GS_FILE_NAME}.'
            )
    
    def get_all_data(self) -> list[dict[str, int | float | str | None]]:
        """
        Retrieves all records from the 'Parts' worksheet of the 'Stock Management Sheet'.
        
        :return: List of dictionaries, each representing a row from the sheet.
        :raises SystemExit: If user chooses to close application after fetching data from Google Sheets fails.
        """
        
        try:
            sql = ('select part_num, manufacturer, description, total, '
                   'stock_b750, stock_b757, minimum, excess, minimum_sallie, '
                   'stock_status from inventory_items;')
            self._cursor.execute(sql)
            results: list[dict[str, int | str | None]] = self._cursor.fetchall()
            return results
            
            # return self._client.worksheet('Parts').get_all_records()
        except Exception as e:
            print(f'Failed To Fetch All Data From {stock_manager.GS_FILE_NAME} Database: {e}')
            self._log.error(f'Failed To Fetch All Data From {stock_manager.GS_FILE_NAME}: {e}')
            response = QMessageBox.critical(
                    None,
                    'Data Fetching Error',
                    f'Failed To Fetch All Data From {stock_manager.GS_FILE_NAME}.\n\n'
                    'Continue To Application?',
                    QMessageBox.Yes,
                    QMessageBox.Close
            )
            
            if response == QMessageBox.Close:
                raise SystemExit(1)
    
    def get_all_users(self) -> set[str]:
        """
        Retrieves all records from the 'Users' worksheet of the 'Stock Management Sheet'
        as a set.
        
        :return: A set of strings representing all the usernames in the database
        :raises SystemExit: If user fetch from database fails
        """
        
        try:
            self._cursor.execute('select * from users;')
            results: list[dict[str, str]] = self._cursor.fetchall()
            return {next(iter(result.values())) for result in results}
            
            # return {
            #     str(user)
            #     for user in self._client.worksheet('Users').col_values(1)
            # }
        except Exception as e:
            print(f'Failed To Get All Users From {stock_manager.GS_FILE_NAME}: {e}')
            self._log.error(f'Failed To Get All Users From {stock_manager.GS_FILE_NAME}: {e}')
            QMessageBox.critical(
                    None,
                    'User Fetch Error',
                    'Failed To Fetch Users From Database',
                    QMessageBox.Close
            )
            raise SystemExit(1)
    
    def update_database(
            self,
            update_type: 'DatabaseUpdateType',
            changelist: Iterable['Item'] | 'Item'
    ) -> bool:
        """
        Update both the Google Sheet and SQL database with the latest changes.
        
        :param update_type: The type of database update as a `DatabaseUpdateType` enum (e.g. `ADD`, `EDIT`, `REMOVE`)
        :param changelist: An iterable list of items to repeat the same process or a single item
        :return: `True` if process completed successfully, `False` if otherwise
        """
        
        from stock_manager import DatabaseUpdateType
        
        sheet: Worksheet = self._client.worksheet('Parts')
        if not isinstance(changelist, list):
            changelist = [changelist]
        
        for item in changelist:
            vals: list[str | int | None] = [value for value in item]
            match update_type:
                case DatabaseUpdateType.ADD:
                    try:
                        sql = ('insert into inventory_items '
                               '(part_num, manufacturer, description, '
                               'total, stock_b750, stock_b757, minimum, '
                               'excess, minimum_sallie, stock_status) '
                               'values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);')
                        
                        sheet.append_row([value for value in item])
                    except Exception as e:
                        print(f'Error Adding "{item.part_num}" To Database: {e}')
                        self._log.error(f'Error Adding "{item.part_num}" To Database: {e}')
                        QMessageBox.critical(
                                None,
                                'Database Add Item Error',
                                f'Error Adding "{item.part_num}" To Database.'
                        )
                        return False
                case DatabaseUpdateType.EDIT:
                    try:
                        sql = ('update inventory_items '
                               'set manufacturer = %s, description = %s, total = %s, '
                               'stock_b750 = %s, stock_b757 = %s, minimum = %s, excess = %s, '
                               'minimum_sallie = %s, stock_status = %s where part_num = %s;')
                        vals = vals[1:] + [item.part_num]
                        
                        cell: Cell | None = sheet.find(item.part_num)
                        if cell:
                            for i, value in enumerate(item):
                                sheet.update_cell(cell.row, i + 1, value)
                    except Exception as e:
                        print(f'Error Editing "{item.part_num}" In Database: {e}')
                        self._log.error(f'Error Editing "{item.part_num}" In Database: {e}')
                        QMessageBox.critical(
                                None,
                                'Database Edit Item Error',
                                f'Error Editing "{item.part_num}" In Database.'
                        )
                        return False
                case DatabaseUpdateType.REMOVE:
                    try:
                        sql = ('delete from inventory_items '
                               'where part_num = %s and manufacturer = %s and '
                               'description = %s and total = %s and stock_b750 = %s and '
                               'stock_b757 = %s and minimum = %s and excess = %s and '
                               'minimum_sallie = %s and stock_status = %s;')
                        
                        cell: Cell | None = sheet.find(item.part_num)
                        if cell:
                            sheet.delete_rows(cell.row)
                    except Exception as e:
                        print(f'Error Deleting "{item.part_num}" From Database: {e}')
                        self._log.error(f'Error Deleting "{item.part_num}" From Database: {e}')
                        QMessageBox.critical(
                                None,
                                'Database Delete Item Error',
                                f'Error Deleting "{item.part_num}" From Database.'
                        )
                        return False
                case _ as unknown:
                    print(f'Unknown Database Update Type: "{unknown}"')
                    QMessageBox.critical(
                            None,
                            'Unknown Database Update Type',
                            f'Unknown Database Update Type: "{unknown}", '
                            'Only Use stock_manager.DatabaseUpdateType Enums When Updating The Database.'
                    )
                    return False
            
            self._cursor.execute(sql, vals)
        
        self._db.commit()
        return True
    
    def add_notification(self, part_num: str) -> bool:
        """
        Adds a notification entry to the Google Sheet Database In The `"Notifications"` tab.
        
        :param part_num: the item part number to be displayed in the notifications database
        :return: `True` if database entry is added successfully, `False` if otherwise.
        """
        
        try:
            sheet: Worksheet = self._client.worksheet('Notifications')
            cell: Cell | None = sheet.find(part_num)
            if cell:
                print(part_num, 'Already In Notifications Database')
                return True
            
            sheet.append_row([part_num])
            return True
        except Exception as e:
            print(f'Failed To Add Notification To Notifications Database: {e}')
            self._log.error(f'Failed To Add Notification To Notifications Database: {e}')
            QMessageBox.critical(
                    None,
                    'Database Notification Add Error',
                    'Error Adding Notification To Notification Database'
            )
            return False
