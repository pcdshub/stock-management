import argparse

import stock_manager


def build_commands() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Common Stock Manager CLI')
    
    # core arguments
    parser.add_argument(
            '-r', '--run',
            action='store_true',
            help='Runs Application GUI, Same As Running "python -m stock_manager"'
    )
    parser.add_argument(
            '-v', '--version',
            action='store_true',
            help='Prints stock_manager\'s git version'
    )
    parser.add_argument(
            '-t', '--test',
            action='store_true',
            help='Runs All Tests Located In stock_manager/tests Using PyTest'
    )
    parser.add_argument(
            '-li', '--list-items',
            action='store_true',
            help='Lists All Items In The Database'
    )
    parser.add_argument(
            '-lu', '--list-users',
            action='store_true',
            help='Lists All Users In The Database'
    )
    parser.add_argument(
            '-e', '--export',
            action='store_true',
            help='Exports All Item Data To A Specified File Type And Location '
                 '(Used With Path And Extension Arguments)'
    )
    parser.add_argument(
            '-qr', '--create-qr',
            action='store_true',
            help='Generates A QR Code Of A Specified Item And Stores It As A '
                 '.PNG In A Specified Location (Used With Path And Part Number Arguments)'
    )
    parser.add_argument(
            '-si', '--search-items',
            action='store_true',
            help='Searches For A Specified Value In All Fields In All Items'
    )
    parser.add_argument(
            '-su', '--search-users',
            action='store_true',
            help='Searches For A Specified Username In All Usernames'
    )
    parser.add_argument(
            '-ai', '--add-item',
            action='store_true',
            help='Add An Item With Specified Values To Both Databases '
                 '(Used With Sequence Of Item Detail Arguments)'
    )
    parser.add_argument(
            '-au', '--add-user',
            action='store_true',
            help='Add A User With Specified Username To Both Databases'
    )
    parser.add_argument(
            '-ri', '--remove-item',
            action='store_true',
            help='Remove A Specified Item From Both Databases After Confirmation Query'
    )
    parser.add_argument(
            '-ru', '--remove-user',
            action='store_true',
            help='Remove A Specified User From Both Databases After Confirmation Query'
    )
    parser.add_argument(
            '-s', '--sync-databases',
            action='store_true',
            help='Synchronize Both Databases, Setting The Values Of The SQL Database '
                 'To That Of The Google Sheet (Only Run If A Database Is Changed Externally)'
    )
    
    # optional positional argument
    parser.add_argument(
            'values',
            nargs='*',
            default=None,
            help='A Sequence Of Optional Positional Arguments'
    )
    
    return parser.parse_args()


def entry_point(args) -> bool:
    if args.run:
        if args.values:
            print('[!] No Values Expected In Run Command, Got:', args.values)
            return False
        print('[+] Starting Application...')
        return True
    elif args.version:
        if args.values:
            print('[!] No Values Expected In Version Command, Got:', args.values)
            return False
        from stock_manager import __version__
        print('[*] Version:', __version__)
        return False
    elif args.test:
        if args.values:
            print('[!] No Values Expected In Test Command, Got:', args.values)
            return False
        
        import pytest
        import sys
        import os
        
        print('[+] Starting Tests...')
        tests_path = os.path.join(os.path.dirname(__file__), 'tests')
        return_code = pytest.main([tests_path])
        sys.exit(return_code)
    elif args.list_items:
        if args.values:
            print('[!] No Values Expected In List Items Command, Got:', args.values)
            return False
        _run_list_items()
        return False
    elif args.list_users:
        if args.values:
            print('[!] No Values Expected In List Users Command, Got:', args.values)
            return False
        _run_list_users()
        return False
    elif args.export:
        if len(args.values) < 2:
            print('[!] Please Enter A Path And Extension When Using Export Command')
            return False
        elif len(args.values) > 2:
            print('[!] 2 Values Expected In Export Command, Got:', args.values[2:])
            return False
        
        from stock_manager import ExportUtils, DBUtils
        
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
    elif args.create_qr:
        if len(args.values) < 2:
            print('[!] Please Enter A Path and Part Number When Using QR Command')
            return False
        elif len(args.values) > 2:
            print('[!] 2 Values Expected In Create QR Command, Got:', args.values[2:])
            return False
        
        from stock_manager import ExportUtils, DBUtils
        
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
    elif args.search_items:
        if not args.values:
            print(
                    '[!] Please Enter A Value To Search For '
                    'When Using Search Items Command'
            )
            return False
        elif len(args.values) > 1:
            print('[!] 1 Value Expected In Search Items Command, Got:', args.values[1:])
            return False
        _run_list_items(args.values[0])
        return False
    elif args.search_users:
        if not args.values:
            print(
                    '[!] Please Enter A Username To Search For '
                    'When Using Search Users Command'
            )
            return False
        elif len(args.values) > 1:
            print('[!] 1 Value Expected In Search Users Command, Got:', args.values[1:])
            return False
        _run_list_users(args.values[0])
        return False
    elif args.add_item:
        from stock_manager import DBUtils, Item, DatabaseUpdateType
        
        if len(args.values) < 10:
            print(
                    '[!] Please Enter A Sequence Of 10 Item Values '
                    'To Add To Both Databases When Using Add Item Command'
            )
            return False
        elif len(args.values) > 10:
            print('[!] 10 Values Expected In Add Item Command, Got:', args.values[10:])
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
    elif args.add_user:
        from stock_manager import DBUtils, DatabaseUpdateType
        
        if not args.values:
            print(
                    '[!] Please Enter A Username To Add To Databases '
                    'When Using Add User Command'
            )
            return False
        elif len(args.values) > 1:
            print('[!] 1 Value Expected In Add User Command, Got', args.values[1:])
            return False
        
        print('[+] Adding User To Databases...')
        
        DBUtils().update_users_database(DatabaseUpdateType.ADD, args.values[0])
        
        print('[*] Successfully Added', args.values[0], 'To Databases')
        return False
    elif args.remove_item:
        from stock_manager import DBUtils, DatabaseUpdateType
        
        if not args.values:
            print(
                    '[!] Please Enter A Part Number To Remove From Databases '
                    'When Using Remove Item Command'
            )
            return False
        elif len(args.values) > 1:
            print('[!] 1 Value Expected In Remove Item Command, Got', args.values[1:])
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
    elif args.remove_user:
        from stock_manager import DBUtils, DatabaseUpdateType
        
        if not args.values:
            print(
                    '[!] Please Enter A Username To Remove From Databases '
                    'When Using Remove User Command'
            )
            return False
        elif len(args.values) > 1:
            print('[!] 1 Value Expected In Remove User Command, Got', args.values[1:])
            return False
        
        print('[+] Removing User From Databases...')
        
        DBUtils().update_users_database(DatabaseUpdateType.REMOVE, args.values[0])
        
        print('[*] Successfully Removed', args.values[0], 'From Databases')
        return False
    elif args.sync_databases:
        if args.values:
            print('[!] No Values Expected In Sync Databases Command, Got:', args.values)
            return False
        print('[+] Syncing Databases...')
        stock_manager.DBUtils().sync_databases()
        print('[*] Successfully Synchronized Databases')
        return False
    else:
        print('[+] Starting Application UI...')
        return True


def _run_list_items(search_value: str = '') -> None:
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


def _run_list_users(search_value: str = '') -> None:
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
