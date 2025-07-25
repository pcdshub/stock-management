import argparse


def build_commands() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Common Stock Manager CLI')
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
            help=''
    )
    parser.add_argument(
            'path',
            type=str,
            help=''
    )
    parser.add_argument(
            'extension',
            type=str,
            help=''
    )
    
    return parser.parse_args()


def entry_point(args) -> bool:
    if args.run:
        print('Starting Application...')
        return True
    elif args.version:
        from stock_manager import __version__
        print(f'Version: {__version__}')
        return False
    elif args.test:
        import pytest
        import sys
        import os
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
        from stock_manager import ExportUtils, App
        
        path = args.path
        extension = args.extension
        utils = ExportUtils(App())
        match extension:
            case 'csv' | 'psv' | 'tsv' as ext:
                utils.sv_export(ext, path)
            case 'pdf':
                utils.pdf_export()
            case _ as unknown:
                print(f'Unknown Export Type: {unknown}')
        
        return False
    
    print('Starting Application UI...')
    return True


def _run_list_items() -> None:
    from stock_manager import DBUtils, StockStatus
    
    def truncate(text: str, width: int) -> str:
        return text if len(text) <= width else f'{text[:width - 3]}...'
    
    widths = [3, 10, 12, 5, 10, 10, 8, 8, 6, 12, 20]
    sum_widths = sum(widths)
    
    def format_row(row_items: list[str]):
        return '  '.join(
                truncate(
                        str(item), w
                ).ljust(w)
                    for item, w in zip(row_items, widths)
        )
    
    all_data: list[dict[str, int | str | None]] = DBUtils().get_all_data()
    headers = [
        'ID', 'Name', 'Manufacturer', 'Total',
        'B750 Stock', 'B757 Stock', 'B750 Min',
        'B757 Min', 'Excess', 'Status', 'Description'
    ]
    border = '=' * (sum_widths + 2 * len(widths))
    
    print('\nStock Items Report')
    print(border)
    print(format_row(headers))
    print(format_row(['-' * widths[i] for i in range(len(widths))]))
    
    i: int
    data: dict[str, int | str | None]
    out_of_stock = 0
    low_stock = 0
    in_stock = 0
    other = 0
    for i, data in enumerate(all_data):
        row = [
            i + 1,
            data['part_num'],
            data['manufacturer'],
            data['total'],
            data['stock_b750'],
            data['stock_b757'],
            data['minimum'],
            data['minimum_sallie'],
            data['excess'],
            data['stock_status'],
            data['description']
        ]
        match data['stock_status']:
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
            f'Total Items: {len(all_data)} | Out Of Stock: {out_of_stock} | '
            f'Low Stock: {low_stock} | In Stock: {in_stock} | Other: {other}'
    )


def _run_list_users():
    from stock_manager import DBUtils
    
    all_users: set[str] = DBUtils().get_all_users()
    border = '=' * 15
    
    print('\nUsers Report')
    print(border)
    
    i: int
    username: str
    for i, username in enumerate(all_users):
        print(f'{i + 1}  {username}')
    
    print(border)
    print(f'Total Users: {len(all_users)}')
