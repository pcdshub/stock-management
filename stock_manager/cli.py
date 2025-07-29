"""
Command Line Interface builder and handler for the Stock Manager Application

Provides a CLI for performing various operations across the application without needing a GUI.
"""

import argparse
import os
import sys
from typing import Callable

import pytest

import stock_manager


def build_commands() -> argparse.Namespace:
    """
    Builds and parses command-line arguments for the CLI interface.
    
    :return: Parsed command-line arguments including flags and values.
    """
    
    parser = argparse.ArgumentParser(description='Common Stock Manager CLI')
    
    # core arguments
    flags = [
        ('-r', '--run', 'Runs Application GUI, Same As Running "python -m stock_manager"'),
        ('-v', '--version', 'Prints stock_manager\'s git version'),
        ('-t', '--test', r'Runs All Tests Located In stock_manager\tests Using PyTest'),
        ('-e', '--export', 'Exports All Item Data To A Specified File Type And Location '
                           '(Used With Path And Extension Arguments)'),
        ('-qr', '--create-qr', 'Generates A QR Code Of A Specified Item And Stores It As A '
                               '.PNG In A Specified Location (Used With Path And Part Number Arguments)'),
        ('-s', '--sync-databases', 'Synchronize Both Databases, Setting The Values Of The SQL Database '
                                   'To That Of The Google Sheet (Only Run If A Database Is Changed Externally)'),
        ('-li', '--list-items', 'Lists All Items In The Database'),
        ('-si', '--search-items', 'Searches For A Specified Value In All Fields In All Items'),
        ('-ai', '--add-item', 'Add An Item With Specified Values To Both Databases '
                              '(Used With Sequence Of 10 Item Detail Arguments)'),
        ('-ri', '--remove-item', 'Remove A Specified Item From Both Databases After Confirmation Query'),
        ('-lu', '--list-users', 'Lists All Users In The Database'),
        ('-su', '--search-users', 'Searches For A Specified Username In All Usernames'),
        ('-au', '--add-user', 'Add A User With Specified Username To Both Databases'),
        ('-ru', '--remove-user', 'Remove A Specified User From Both Databases After Confirmation Query'),
    ]
    
    for short, long, desc in flags:
        parser.add_argument(short, long, action='store_true', help=desc)
    
    # optional positional arguments
    parser.add_argument(
            'values',
            nargs='*',
            default=None,
            help='A Sequence Of Optional Positional Arguments'
    )
    
    return parser.parse_args()


def entry_point(args) -> bool:
    """
    Entry point dispatcher that maps CLI flags to corresponding handler functions.
    
    :param args: Parsed command-line arguments.
    :return: `True` if GUI should be launched, `False` otherwise.
    """
    
    command_map: dict[str, Callable[[args], bool]] = {
        'run': _run_app,
        'version': _run_version,
        'test': _run_tests,
        'export': _run_export,
        'create_qr': _run_qr,
        'sync_databases': _run_sync_databases,
        
        'list_items': _run_list_items,
        'search_items': _run_search_items,
        'add_item': _run_add_item,
        'remove_item': _run_remove_item,
        
        'list_users': _run_list_users,
        'search_users': _run_search_users,
        'add_user': _run_add_user,
        'remove_user': _run_remove_user,
    }
    
    for cmd, handler in command_map.items():
        if getattr(args, cmd, False):
            return handler(args)
    
    print('[+] Starting Application UI...')
    return True


def _valid_args(args, expected=0) -> bool:
    """
    Validates the number of positional arguments received from the command line.
    
    :param args: Parsed arguments containing `values`.
    :param expected: Expected number of positional arguments, 0 by default.
    :return: `True` if valid, `False` otherwise.
    """
    
    values = args.values or []
    if expected:
        if len(values) < expected or len(values) > expected:
            print(f'[!] Expected {expected} values, got {len(values)}: {values}')
            return False
    elif values:
        print(f'[!] No Values Expected, Got {len(values)}: {values}')
        return False
    return True


def _run_app(args) -> bool:
    """
    Handler for the -r/--run command --- starts the GUI application.
    
    :param args: Empty CLI arguments.
    :return: `True` if successful, `False` otherwise.
    """
    
    if not _valid_args(args):
        return False
    print('[+] Starting Application...')
    return True


def _run_version(args) -> bool:
    """
    Handler for the -v/--version command --- prints the application version.
    
    :param args: Empty CLI arguments.
    :return: `False` always, no further action is needed.
    """
    
    if not _valid_args(args):
        return False
    print('[*] Version:', stock_manager.__version__)
    return False


def _run_tests(args) -> bool:
    """
    Handler for the -t/--test command --- runs pytest on the tests directory.
    
    :param args: Empty CLI arguments.
    :return: `False` if CLI arguments do not match command,
    otherwise calls `sys.exit()` with the test return code.
    """
    
    if not _valid_args(args):
        return False
    
    print('[+] Starting Tests...')
    
    tests_path = os.path.join(os.path.dirname(__file__), 'tests')
    return_code = pytest.main([tests_path])
    
    sys.exit(return_code)


def _run_export(args) -> bool:
    """
    Handler for the -e/--export command --- exports item data to a specified file format.
    
    :param args: CLI arguments with [path, extension] values.
    :return: `False` always, no further action is needed.
    """
    
    from stock_manager import ExportUtils, DBUtils
    
    if not _valid_args(args, 2):
        return False
    
    path = args.values[0]
    extension = args.values[1]
    print(f'[+] Exporting Data As .{extension} File...')
    
    utils = ExportUtils()
    db = DBUtils()
    all_items = db.create_all_items(db.get_all_data_gs())
    
    match extension:
        case 'csv' | 'psv' | 'tsv':
            utils.sv_export(extension, path, all_items)
        case 'pdf':
            utils.pdf_export()
        case _:
            print('[!] Unknown Export Type:', extension)
            return False
    
    print('[*] Successfully Exported Data To', extension, 'File')
    return False


def _run_qr(args) -> bool:
    """
    Handler for the -qr/--create-qr command --- generates and saves a QR code for an item.
    
    :param args: CLI arguments with [path, part_num] values.
    :return: `False` always, no further action is needed.
    """
    
    from stock_manager import ExportUtils
    
    if not _valid_args(args, 2):
        return False
    
    path = args.values[0]
    part_num = args.values[1]
    print('[+] Exporting', part_num, 'QR Code As .PNG...')
    utils = ExportUtils()
    
    image = utils.create_code(part_num)
    if not image:
        return False
    
    if not utils.save_code(image, path):
        return False
    
    print('[*] Successfully Exported', part_num, 'QR Code')
    return False


def _run_sync_databases(args) -> bool:
    """
    Handler for the -s/--sync-databases command --- synchronizes the local and remote databases.
    
    :param args: Empty CLI arguments.
    :return: `False` always, no further action is needed.
    """
    
    if not _valid_args(args):
        return False
    print('[+] Syncing Databases...')
    stock_manager.DBUtils().sync_databases()
    print('[*] Successfully Synchronized Databases')
    return False


def _run_list_items(args) -> bool:
    """
    Handler for the -li/--list-items command --- lists all items in the database.
    
    :param args: Empty CLI arguments.
    :return: `False` always, no further action is needed.
    """
    
    if not _valid_args(args):
        return False
    _list_items()
    return False


def _run_search_items(args) -> bool:
    """
    Handler for the -si/--search-items command --- searches items by a given string.
    
    :param args: CLI arguments with one search string.
    :return: `False` always, no further action is needed.
    """
    
    if not _valid_args(args, 1):
        return False
    _list_items(args.values[0])
    return False


def _run_add_item(args) -> bool:
    """
    Handler for the -ai/--add-item command --- adds a new item to the database.
    
    :param args: CLI arguments with 10 values representing item details in the Google Sheet's order.
    :return: `False` always, no further action is needed.
    """
    
    if not _valid_args(args, 10):
        return False
    
    print('[+] Adding Item To Databases...')
    
    try:
        from stock_manager import DBUtils, DatabaseUpdateType, Item
        
        vals: list[str | int] = [
            value if i not in [3, 4, 5, 6, 7, 8]
            else int(value)
            for i, value in enumerate(args.values)
        ]
        item = Item(*vals)
        
        DBUtils().update_items_database(DatabaseUpdateType.ADD, item)
        
        print('[*] Successfully Added', item.part_num, 'To Databases')
    except ValueError as e:
        print('[x] Failed To Add Item To Database:', e)
    finally:
        return False


def _run_remove_item(args) -> bool:
    """
    Handler for the -ri/--remove-item command --- removes an item by part number.
    
    :param args: CLI arguments with one part number.
    :return: `False` always, no further action is needed.
    """
    
    from stock_manager import DatabaseUpdateType, DBUtils
    
    if not _valid_args(args, 1):
        return False
    
    print(f'[+] Removing "{args.values[0]}" From Databases...')
    
    utils = DBUtils()
    item = utils.find_item(args.values[0])
    if not item:
        print(f'[x] Could Not Locate "{args.values[0]}" In Databases')
        return False
    
    utils.update_items_database(DatabaseUpdateType.REMOVE, item)
    
    print('[*] Successfully Removed', item.part_num, 'From Databases')
    return False


def _run_list_users(args) -> bool:
    """
    Handler for the -lu/--list-users command --- lists all users in the database.
    
    :param args: Empty CLI arguments.
    :return: `False` always, no further action is needed.
    """
    
    if not _valid_args(args):
        return False
    _list_users()
    return False


def _run_search_users(args) -> bool:
    """
    Handler for the -su/--search-users command --- searches users by username substring.
    
    :param args: CLI arguments with one username.
    :return: `False` always, no further action is needed.
    """
    
    if not _valid_args(args, 1):
        return False
    _list_users(args.values[0])
    return False


def _run_add_user(args) -> bool:
    """
    Handler for the -au/--add-user command --- adds a new user to the database.
    
    :param args: CLI arguments with one username.
    :return: `False` always, no further action is needed.
    """
    
    from stock_manager import DatabaseUpdateType, DBUtils
    
    if not _valid_args(args, 1):
        return False
    
    print('[+] Adding User To Databases...')
    
    DBUtils().update_users_database(DatabaseUpdateType.ADD, args.values[0])
    
    print('[*] Successfully Added', args.values[0], 'To Databases')
    return False


def _run_remove_user(args) -> bool:
    """
    Handler for the -ru/--remove-user command --- removes a user by username.
    
    :param args: CLI arguments with one username.
    :return: `False` always, no further action is needed.
    """
    
    from stock_manager import DatabaseUpdateType, DBUtils
    
    if not _valid_args(args, 1):
        return False
    
    print('[+] Removing User From Databases...')
    
    DBUtils().update_users_database(DatabaseUpdateType.REMOVE, args.values[0])
    
    print('[*] Successfully Removed', args.values[0], 'From Databases')
    return False


def _list_items(search_value='') -> None:
    """
    Prints a formatted report of all stock items, optionally filtered by a search value.
    
    :param search_value: Optional substring to filter items.
    """
    
    from stock_manager import DBUtils, StockStatus
    
    print('[+]', 'Gathering Item Data...' if not search_value else f'Searching For Items With "{search_value}"...')
    widths = [3, 10, 12, 5, 10, 10, 8, 8, 6, 12, 20]
    sum_widths = sum(widths)
    all_data: list[dict[str, int | str | None]] = DBUtils().get_all_data_gs()
    headers = [
        'ID', 'Name', 'Manufacturer', 'Total',
        'B750 Stock', 'B757 Stock', 'B750 Min',
        'B757 Min', 'Excess', 'Status', 'Description'
    ]
    border = '=' * (sum_widths + 2 * len(widths))
    
    def truncate(text: str, width: int) -> str:
        return text if len(text) <= width else f'{text[:width - 3]}...'
    
    def format_row(row_items: list[str]):
        return '  '.join(
                truncate(
                        str(item), w
                ).ljust(w)
                    for item, w in zip(row_items, widths)
        )
    
    print('\n[+] Stock Items Report')
    print(border)
    print(format_row(headers))
    print(format_row(['-' * widths[i] for i in range(len(widths))]))
    
    i: int
    data: dict[str, int | str | None]
    out_of_stock = low_stock = in_stock = other = total = 0
    for i, data in enumerate(all_data):
        if search_value:
            found = False
            for value in data.values():
                value = str(value)
                if search_value.lower() in value.lower():
                    found = True
                    break
            if not found:
                continue
        
        row = [
            i + 1,
            data['Part #'],
            data['Manufacturer'],
            data['Total'],
            data['B750'],
            data['B757'],
            data['Minimum'],
            data['B750 Minimum'],
            data['Excess'],
            data['Stock Status'],
            data['Description']
        ]
        match data['Stock Status']:
            case StockStatus.OUT_OF_STOCK.value:
                out_of_stock += 1
            case StockStatus.LOW_STOCK.value:
                low_stock += 1
            case StockStatus.IN_STOCK.value:
                in_stock += 1
            case _:
                other += 1
        total += 1
        print(format_row(row))
    
    print(border)
    print(
            '[*] Total Items:', total, '| Out Of Stock:', out_of_stock,
            '| Low Stock:', low_stock, '| In Stock:', in_stock, '| Other:', other
    )


def _list_users(search_value='') -> None:
    """
    Prints a list of all users in the database, optionally filtered by a substring.
    
    :param search_value: Optional username substring to filter users.
    """
    
    from stock_manager import DBUtils
    
    print('[+]', 'Gathering User Data...' if not search_value else f'Searching For Usernames With "{search_value}"...')
    all_users: set[str] = DBUtils().get_all_users_gs()
    border = '=' * 16
    
    print('\n[+] Users Report')
    print(border)
    
    i: int
    username: str
    total = 0
    for i, username in enumerate(all_users):
        if search_value and search_value.lower() not in username.lower():
            continue
        total += 1
        print(i + 1, username)
    
    print(border)
    print('[*] Total Users:', total)
