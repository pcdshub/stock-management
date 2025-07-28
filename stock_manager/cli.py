import argparse


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
                 '.PNG In A Specified Location (Used With Path And Part Number)'
    )
    
    # positional arguments
    for i in range(2):
        parser.add_argument(
                f'pos_arg_{i + 1}',
                type=str,
                nargs='?',
                default=None,
                help=f'Positional Argument {i + 1}'
        )
    
    return parser.parse_args()


def entry_point(args) -> bool:
    if args.run:
        print('[+] Starting Application...')
        return True
    elif args.version:
        from stock_manager import __version__
        print('[*] Version:', __version__)
        return False
    elif args.test:
        import pytest
        import sys
        import os
        
        print('[+] Starting Tests...')
        tests_path = os.path.join(os.path.dirname(__file__), 'tests')
        return_code = pytest.main([tests_path])
        sys.exit(return_code)
    elif args.list_items:
        _run_list_items()
        return False
    elif args.list_users:
        _run_list_users()
        return False
    elif args.export:
        if not args.pos_arg_1 or not args.pos_arg_2:
            print('[!] Please Enter A Path And Extension When Using Export Command')
            return False
        
        from stock_manager import ExportUtils, DBUtils
        
        path = args.pos_arg_1
        extension = args.pos_arg_2
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
        if not args.pos_arg_1 or not args.pos_arg_2:
            print('[!] Please Enter A Path and Part Number When Using QR Command')
            return False
        
        from stock_manager import ExportUtils, DBUtils
        
        path = args.pos_arg_1
        part_num = args.pos_arg_2
        print('[+] Exporting', part_num, 'QR Code As .PNG...')
        utils = ExportUtils()
        
        image = utils.create_code(part_num)
        if not image:
            return False
        
        if not utils.save_code(image, path):
            return False
        
        print('[*] Successfully Exported', part_num, ' QR Code')
        return False
    else:
        print('[+] Starting Application UI...')
        return True


def _run_list_items() -> None:
    from stock_manager import DBUtils, StockStatus
    
    print('[+] Gathering Item Data...')
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
    out_of_stock = low_stock = in_stock = other = 0
    for i, data in enumerate(all_data):
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
        print(format_row(row))
    
    print(border)
    print(
            f'[*] Total Items: {len(all_data)} | Out Of Stock: {out_of_stock} | '
            f'Low Stock: {low_stock} | In Stock: {in_stock} | Other: {other}'
    )


def _run_list_users() -> None:
    from stock_manager import DBUtils
    
    print('[+] Gathering User Data...')
    all_users: set[str] = DBUtils().get_all_users_gs()
    border = '=' * 15
    
    print('\n[+] Users Report')
    print(border)
    
    i: int
    username: str
    for i, username in enumerate(all_users):
        print(i + 1, username)
    
    print(border)
    print('[*] Total Users:', len(all_users))
