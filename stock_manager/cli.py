import argparse
import os
import sys
from typing import Callable

import pytest

import stock_manager
from stock_manager import DatabaseUpdateType, DBUtils, ExportUtils, Item


def build_commands() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Common Stock Manager CLI')
    
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
    
    # core arguments
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
        'search_users': _run_search_user,
        'add_user': _run_add_user,
        'remove_user': _run_remove_user,
    }
    
    for cmd, handler in command_map.items():
        if getattr(args, cmd, False):
            return handler(args)
    
    print('[+] Starting Application UI...')
    return True


def validate_args(args, expected=0) -> bool:
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
    if not validate_args(args):
        return False
    print('[+] Starting Application...')
    return True


def _run_version(args) -> bool:
    if not validate_args(args):
        return False
    print('[*] Version:', stock_manager.__version__)
    return False


def _run_tests(args) -> bool:
    if not validate_args(args):
        return False
    
    print('[+] Starting Tests...')
    
    tests_path = os.path.join(os.path.dirname(__file__), 'tests')
    return_code = pytest.main([tests_path])
    
    sys.exit(return_code)


def _run_export(args) -> bool:
    if not validate_args(args, 2):
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
    if not validate_args(args, 2):
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
    
    print('[*] Successfully Exported', part_num, ' QR Code')
    return False


def _run_sync_databases(args) -> bool:
    if not validate_args(args):
        return False
    print('[+] Syncing Databases...')
    stock_manager.DBUtils().sync_databases()
    print('[*] Successfully Synchronized Databases')
    return False


def _run_list_items(args) -> bool:
    if not validate_args(args):
        return False
    _list_items()
    return False


def _run_search_items(args) -> bool:
    if not validate_args(args, 1):
        return False
    _list_items(args.values[0])
    return False


def _run_add_item(args) -> bool:
    if not validate_args(args, 10):
        return False
    
    print('[+] Adding Item To Databases...')
    
    try:
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
    
    return False


def _run_remove_item(args) -> bool:
    if not validate_args(args, 1):
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
    if not validate_args(args):
        return False
    _list_users()
    return False


def _run_search_user(args) -> bool:
    if not validate_args(args):
        return False
    _run_list_users(args.values[0])
    return False


def _run_add_user(args) -> bool:
    if not validate_args(args, 1):
        return False
    
    print('[+] Adding User To Databases...')
    
    DBUtils().update_users_database(DatabaseUpdateType.ADD, args.values[0])
    
    print('[*] Successfully Added', args.values[0], 'To Databases')
    return False


def _run_remove_user(args) -> bool:
    if not validate_args(args, 1):
        return False
    
    print('[+] Removing User From Databases...')
    
    DBUtils().update_users_database(DatabaseUpdateType.REMOVE, args.values[0])
    
    print('[*] Successfully Removed', args.values[0], 'From Databases')
    return False


def _list_items(search_value='') -> None:
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
