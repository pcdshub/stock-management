"""
Database utilities for Stock Management Application.

Provides DBUtils for connecting to and getting/setting data from/to Google Sheets and a MySQL Database.
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
            print('[x] Failed To Connect To Database:', e)
            self._log.error(f'Failed To Connect To Database: {e}')
            QMessageBox.critical(
                    None,
                    'Database Connection Failure',
                    'Failed To Connect To Database, Make Sure You Have An Internet Connection'
            )
            raise SystemExit(1)
    
    def sync_databases(self) -> bool:
        """
        Synchronize the local SQL database with the Google Sheet.
    
        This method ensures that the SQL database mirrors the current state of the Google Sheet,
        which is considered the main source of data. It fetches all relevant data from the sheet,
        compares it against the local SQL database, and applies updates, insertions, or deletions
        as needed to keep both databases consistent.
        
        **This method should only be called once (on app startup).**
        
        :return: `True` if databases are synchronized successfully, `False` if otherwise.
        """
        
        from stock_manager import Item, DatabaseUpdateType
        
        all_parts_gs = self.get_all_data_gs()
        all_users_gs = self.get_all_users_gs()
        all_parts_sql = self.get_all_data_sql()
        all_users_sql = self.get_all_users_sql()
        
        sql_part_names: set[str] = {str(part['part_num']).strip() for part in all_parts_sql}
        gs_part_names: set[str] = {str(part['Part #']).strip() for part in all_parts_gs}
        
        # add or update parts
        for part_dict_gs in all_parts_gs:
            part_name = str(part_dict_gs['Part #']).strip()
            gs_part = Item(*part_dict_gs.values())
            
            if part_name in sql_part_names:
                sql_part_dict = next(
                        (d for d in all_parts_sql
                            if str(d['part_num']).strip() == part_name),
                        None
                )
                
                sql_part = Item(
                        sql_part_dict['part_num'],
                        sql_part_dict['manufacturer'],
                        sql_part_dict['description'],
                        sql_part_dict['total'],
                        sql_part_dict['stock_b750'],
                        sql_part_dict['stock_b757'],
                        sql_part_dict['minimum'],
                        sql_part_dict['excess'],
                        sql_part_dict['minimum_sallie'],
                        sql_part_dict['stock_status'],
                )
                
                if gs_part == sql_part:
                    continue
                
                print('[+] Editing Item:', gs_part)
                if not self._update_sql(DatabaseUpdateType.EDIT, gs_part):
                    return False
            else:
                print('[+] Adding Item:', gs_part)
                if not self._update_sql(DatabaseUpdateType.ADD, gs_part):
                    return False
        
        # add new users
        for username in all_users_gs:
            if username in all_users_sql:
                continue
            
            print('[+] Adding Username:', username)
            try:
                self._cursor.execute('insert into users (username) value (%s);', [username])
            except Exception as e:
                print('[+] Adding Usernames Error:', e)
                self._log.error(f'Adding Usernames Error: {e}')
                QMessageBox.critical(
                        None,
                        'Username Inserting Error',
                        'Error Adding GS Usernames To SQL Database'
                )
                return False
        
        # remove SQL parts that are not in GS
        for part_dict in all_parts_sql:
            part_num = str(part_dict['part_num']).strip()
            if part_num in gs_part_names:
                continue
            
            item = Item(*list(part_dict.values()))
            print('[+] Removing Item:', item)
            if not self._update_sql(DatabaseUpdateType.REMOVE, item):
                return False
        
        # remove SQL users that are not in GS
        for username in all_users_sql:
            if username in all_users_gs:
                continue
            
            print('[+] Removing Username:', username)
            try:
                self._cursor.execute('delete from users where username = %s;', [username])
            except Exception as e:
                print('[x] Deleting Users Error:', e)
                self._log.error(f'Deleting Users Error: {e}')
                QMessageBox.critical(
                        None,
                        'Username Deletion Error',
                        'Error Deleting Username From SQL Database'
                )
                return False
        
        self._db.commit()
        return True
    
    @staticmethod
    def create_all_items(gs_items: list[dict[str, int | str | None]]) -> list['Item']:
        """
        Convert a list dictionaries (Google Sheet Columns) to a list of `Item` objects
        
        :param gs_items: A list of Google Sheet columns
        :return: a list of `Item` objects
        """
        
        from stock_manager import Item
        
        obj_items: list[Item] = []
        for item in gs_items:
            vals: list[int | str | None] = [
                None if val is None or val == ''
                else val
                for val in list(item.values())
            ]
            obj_items.append(Item(*vals))
        return obj_items
    
    def get_headers(self) -> list[str]:
        """
        Retrieves the headers of the 'Parts' worksheet of the 'Stock Management Sheet'.
        
        :return: A list of strings containing the headers of the worksheet
        """
        
        try:
            return self._client.worksheet('Parts').row_values(1)
        except Exception as e:
            print(f'[x] Failed To Fetch Sheet Headers From {stock_manager.GS_FILE_NAME} Database: {e}')
            self._log.error(f'Failed To Fetch Sheet Headers From {stock_manager.GS_FILE_NAME} Database: {e}')
            QMessageBox.critical(
                    None,
                    'Header Fetching Error',
                    f'Failed To Fetch Sheet Headers From {stock_manager.GS_FILE_NAME}.'
            )
    
    def get_all_data_gs(self) -> list[dict[str, int | str | None]]:
        """
        Retrieves all records from the `'Parts'` worksheet of the `'Stock Management Sheet'`.
        
        :return: List of dictionaries, each representing a row from the sheet.
        :raises SystemExit: If user chooses to close application after fetching data from Google Sheets fails.
        """
        
        try:
            return self._client.worksheet('Parts').get_all_records()
        except Exception as e:
            print(f'[x] Failed To Fetch All Data From {stock_manager.GS_FILE_NAME} Database: {e}')
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
    
    def get_all_data_sql(self) -> list[dict[str, int | str | None]]:
        """
        Retrieves all part data from the SQL database.
        
        Runs "`select part_num, manufacturer, description, total, stock_b750,
        stock_b757, minimum, excess, minimum_sallie, stock_status from inventory_items;`".
        
        :return: List of dictionaries, each representing a row from the sheet.
        :raises SystemExit: If user chooses to close application after fetching data from Google Sheets fails.
        """
        
        try:
            sql = ('select part_num, manufacturer, description, total, '
                   'stock_b750, stock_b757, minimum, excess, minimum_sallie, '
                   'stock_status from inventory_items;')
            self._cursor.execute(sql)
            return self._cursor.fetchall()
        except Exception as e:
            print('[x] Failed To Fetch All Data From SQL Database:', e)
            self._log.error(f'Failed To Fetch All Data From SQL Database: {e}')
            response = QMessageBox.critical(
                    None,
                    'Data Fetching Error',
                    f'Failed To Fetch All Data From SQL Database.\n\n'
                    'Continue To Application?',
                    QMessageBox.Yes,
                    QMessageBox.Close
            )
            
            if response == QMessageBox.Close:
                raise SystemExit(1)
    
    def get_all_users_gs(self) -> set[str]:
        """
        Retrieves all records from the `'Users'` worksheet of the `'Stock Management Sheet'`
        as a set.
        
        :return: A set of strings representing all the usernames in the database
        :raises SystemExit: If user fetch from database fails
        """
        
        try:
            return {
                str(user)
                for user in self._client.worksheet('Users').col_values(1)
            }
        except Exception as e:
            print(f'[x] Failed To Get All Users From {stock_manager.GS_FILE_NAME}: {e}')
            self._log.error(f'Failed To Get All Users From {stock_manager.GS_FILE_NAME}: {e}')
            QMessageBox.critical(
                    None,
                    'User Fetch Error',
                    f'Failed To Fetch Users From {stock_manager.GS_FILE_NAME}',
                    QMessageBox.Close
            )
            raise SystemExit(1)
    
    def get_all_users_sql(self) -> set[str]:
        """
        Retrieves all users from the SQL database.
        
        Runs "`select * from users;`".
        
        :return: A set of strings representing all the usernames in the database
        :raises SystemExit: If user fetch from database fails
        """
        
        try:
            self._cursor.execute('select * from users;')
            results: list[dict[str, str]] = self._cursor.fetchall()
            return {next(iter(result.values())) for result in results}
        except Exception as e:
            print('[x] Failed To Get All Users From SQL Database:', e)
            self._log.error(f'Failed To Get All Users From SQL Database: {e}')
            QMessageBox.critical(
                    None,
                    'User Fetch Error',
                    'Failed To Fetch Users From SQL Database',
                    QMessageBox.Close
            )
            raise SystemExit(1)
    
    def update_database(
            self,
            update_type: 'DatabaseUpdateType',
            changelist: Iterable['Item'] | 'Item'
    ) -> bool:
        """
        Update both the Google Sheet and SQL database with the latest changes using private local helper methods.
        
        :param update_type: The type of database update as a `DatabaseUpdateType` enum (e.g. `ADD`, `EDIT`, `REMOVE`)
        :param changelist: An iterable list of items to repeat the same process or a single item
        :return: `True` if process completed successfully, `False` if otherwise
        """
        
        from stock_manager import DatabaseUpdateType
        
        if not isinstance(changelist, list):
            changelist = [changelist]
        
        if update_type not in [DatabaseUpdateType.ADD, DatabaseUpdateType.EDIT, DatabaseUpdateType.REMOVE]:
            print('[x] Unknown Database Update Type:', update_type)
            self._log.error(f'Unknown Database Update Type: {update_type}')
            QMessageBox.critical(
                    None,
                    'Database Update Type Error',
                    f'Unknown Database Update Type: {update_type}'
            )
            return False
        
        for item in changelist:
            update_gs: bool = self._update_gs(update_type, item)
            update_sql: bool = self._update_sql(update_type, item)
            
            if not all([update_gs, update_sql]):
                return False
        return True
    
    def _update_sql(self, update_type: 'DatabaseUpdateType', item: 'Item') -> bool:
        from stock_manager import DatabaseUpdateType
        
        vals: list[str | int | None] = [value if not value == '' else None for value in item]
        sql = ''
        match update_type:
            case DatabaseUpdateType.ADD:
                sql = ('insert into inventory_items '
                       '(part_num, manufacturer, description, '
                       'total, stock_b750, stock_b757, minimum, '
                       'excess, minimum_sallie, stock_status) '
                       'values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);')
            case DatabaseUpdateType.EDIT:
                sql = ('update inventory_items '
                       'set manufacturer = %s, description = %s, total = %s, '
                       'stock_b750 = %s, stock_b757 = %s, minimum = %s, excess = %s, '
                       'minimum_sallie = %s, stock_status = %s where part_num = %s;')
                vals = vals[1:] + [item.part_num]
            case DatabaseUpdateType.REMOVE:
                sql = ('delete from inventory_items '
                       'where part_num = %s and manufacturer = %s and '
                       'description = %s and total = %s and stock_b750 = %s and '
                       'stock_b757 = %s and minimum = %s and excess = %s and '
                       'minimum_sallie = %s and stock_status = %s;')
        
        try:
            self._cursor.execute(sql, vals)
            self._db.commit()
            return True
        except Exception as e:
            print('[x] Error Updating SQL Database:', e)
            self._log.error(f'Error Updating SQL Database: {e}')
            QMessageBox.critical(
                    None,
                    'SQL Database Update Error',
                    'Failed To Update SQL Database'
            )
            return False
    
    def _update_gs(self, update_type: 'DatabaseUpdateType', item: 'Item') -> bool:
        from stock_manager import DatabaseUpdateType
        
        sheet: Worksheet = self._client.worksheet('Parts')
        try:
            match update_type:
                case DatabaseUpdateType.ADD:
                    sheet.append_row([value for value in item])
                case DatabaseUpdateType.EDIT:
                    cell: Cell | None = sheet.find(item.part_num)
                    if not cell:
                        return False
                    
                    i: int
                    value: str | int | None
                    for i, value in enumerate(item):
                        sheet.update_cell(cell.row, i + 1, value)
                case DatabaseUpdateType.REMOVE:
                    cell: Cell | None = sheet.find(item.part_num)
                    if cell:
                        sheet.delete_rows(cell.row)
            return True
        except Exception as e:
            print(f'[x] Error Updating "{item.part_num}" In Google Sheet Database: {e}')
            self._log.error(f'Error Updating "{item.part_num}" In Google Sheet Database: {e}')
            QMessageBox.critical(
                    None,
                    'Google Sheet Database Update Error',
                    'Failed To Update Google Sheet Database'
            )
            return False
    
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
                print('[*]', part_num, 'Already In Notifications Database')
                return True
            
            sheet.append_row([part_num])
            return True
        except Exception as e:
            print('[x] Failed To Add Notification To Notifications Database:', e)
            self._log.error(f'Failed To Add Notification To Notifications Database: {e}')
            QMessageBox.critical(
                    None,
                    'Database Notification Add Error',
                    'Error Adding Notification To Notification Database'
            )
            return False
