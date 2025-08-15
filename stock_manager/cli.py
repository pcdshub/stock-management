"""
Command Line Interface builder and handler for
the Stock Manager Application.

Provides a CLI for performing various operations
across the application without needing a GUI.
"""

import argparse
import logging
import os
import sys
from typing import Union

import pytest
from prettytable import PrettyTable

import stock_manager
from stock_manager.model import Item
from stock_manager.utils import (DatabaseUpdateType, DBUtils, ExportUtils,
                                 StockStatus)

logger = logging.getLogger()


def build_commands() -> Union[argparse.Namespace, None]:
    """
    Builds and parses command-line arguments for the CLI interface.

    :return: Parsed command-line arguments including flags and values.
    """

    top_parser = argparse.ArgumentParser(
        prog='stock_manager',
        description='Common Stock Manager CLI'
    )
    sub_parsers = top_parser.add_subparsers(help='Available Subcommands')

    # region Top-Level Arguments
    top_parser.add_argument(
        '-r', '--run',
        action='store_true',
        help='Runs Application GUI, Same As Running "python -m stock_manager"'
    )
    top_parser.add_argument(
        '-v', '--version',
        action='version',
        version=stock_manager.__version__,
        help='Prints stock_manager\'s git version'
    )
    top_parser.add_argument(
        '-t', '--tree',
        action='store_true',
        help='Prints stock_manager\'s commands, subcommands, '
             'and positional arguments in tree layout',
    )

    test_parser = sub_parsers.add_parser(
        'test',
        help='Runs All Tests Located In stock_manager/tests/ Using PyTest'
    )
    test_parser.set_defaults(func=_run_tests)

    sync_parser = sub_parsers.add_parser(
        'sync',
        help='Synchronize Both Databases, '
             'Setting The Values Of The SQL Database '
             'To That Of The Google Sheet '
             '(Only Run If A Database Is Changed Externally)'
    )
    sync_parser.set_defaults(func=_run_sync_databases)
    # endregion

    # region Export Arguments
    export_parser = sub_parsers.add_parser(
        'export',
        help='Exports All Item Data To A Specified File Type And Location '
             '(Used With Path And Extension Arguments)'
    )
    export_parser.add_argument(
        'extension',
        type=str,
        help='File extension/format to export as (e.g., csv, pdf, etc.)'
    )
    export_parser.add_argument(
        'path',
        type=str,
        nargs='?',
        default='./exports',
        help='Path To Export The File To (Default Path: ./exports)'
    )
    export_parser.set_defaults(func=_run_export)
    # endregion

    # region QR Arguments
    qr_parser = sub_parsers.add_parser(
        'qr',
        help='Generates A QR Code Of A Specified Item And Stores It As A '
             '.PNG In A Specified Location '
             '(Used With Path And Part Number Arguments)'
    )
    qr_parser.add_argument(
        'part_num',
        type=str,
        help='Part Number Of The Item To Generate A QR Code For'
    )
    qr_parser.add_argument(
        'path',
        type=str,
        nargs='?',
        default='./exports',
        help='Output Path Where The QR Code Image Will Be Saved '
             '(Default Path: ./exports)'
    )
    qr_parser.set_defaults(func=_run_qr)
    # endregion

    # region Item Arguments
    item_parser = sub_parsers.add_parser(
        'items',
        help='Commands Related To Item Management '
             '(e.g., list, add, search, etc.)'
    )

    item_parser.add_argument(
        '-l', '--list',
        action='store_true',
        help='Lists All Items In The Database'
    )
    item_parser.set_defaults(func=_run_list_items)

    item_subparser = item_parser.add_subparsers()

    search_parser = item_subparser.add_parser(
        'search',
        help='Searches For A Specified Value In All Fields In All Items'
    )
    search_parser.add_argument(
        'search_string',
        type=str,
        help='Keyword To Search Across All Item Fields'
    )
    search_parser.set_defaults(func=_run_search_items)

    add_parser = item_subparser.add_parser(
        'add',
        help='Add An Item With Specified Values To Both Databases '
             '(Used With Sequence Of 10 Item Detail Arguments)'
    )
    add_parser.add_argument(
        'values',
        nargs=10,
        help='10 Values Representing The Item Fields In Order '
             '(e.g., part_num, manufacturer, total, etc.)'
    )
    add_parser.set_defaults(func=_run_add_item)

    remove_parser = item_subparser.add_parser(
        'remove',
        help='Remove A Specified Item From Both Databases'
    )
    remove_parser.add_argument(
        'part_num',
        type=str,
        help='Part Number Of The Item To Be Removed'
    )
    remove_parser.set_defaults(func=_run_remove_item)

    edit_parser = item_subparser.add_parser(
        'edit',
        help='Edit A Specified Item With At Least One Field Name And New Value'
    )
    edit_parser.add_argument(
        'part_num',
        type=str,
        help='Part Number Of The Item To Be Edited'
    )
    edit_parser.add_argument(
        'values',
        nargs='+',
        help='Pairs Of Field Names And New Values To Update '
             '(e.g., part_num=sample_item, total=0, etc.)'
    )
    edit_parser.set_defaults(func=_run_edit_item)
    # endregion

    # region User Arguments
    user_parser = sub_parsers.add_parser(
        'users',
        help='Commands Related To User Management '
             '(e.g., list, add, search, etc.)'
    )

    user_parser.add_argument(
        '-l', '--list',
        action='store_true',
        help='Lists All Users In The Database'
    )
    user_parser.set_defaults(func=_run_list_users)

    user_subparser = user_parser.add_subparsers()

    search_parser = user_subparser.add_parser(
        'search',
        help='Searches For A Specified Username In All Usernames'
    )
    search_parser.add_argument(
        'part_num',
        type=str,
        help='Username To Search In User List'
    )
    search_parser.set_defaults(func=_run_search_users)

    add_parser = user_subparser.add_parser(
        'add',
        help='Add A User With Specified Username To Both Databases'
    )
    add_parser.add_argument(
        'username',
        type=str,
        help='Username To Add To Databases'
    )
    add_parser.set_defaults(func=_run_add_user)

    remove_parser = user_subparser.add_parser(
        'remove',
        help='Remove A Specified User From Both Databases'
    )
    remove_parser.add_argument(
        'username',
        type=str,
        help='Username To Remove From Databases'
    )
    remove_parser.set_defaults(func=_run_remove_user)
    # endregion

    args = top_parser.parse_args()

    if args.tree:
        print_command_tree(top_parser)
        raise SystemExit(1)

    return args


# region Misc Argument Functions
def print_command_tree(parser: argparse.ArgumentParser, indent=1):
    for action in parser._actions:
        if not isinstance(action, argparse.Action):
            continue

        if not hasattr(action, '_choices_actions'):
            print(f'{"│   " * (indent - 1)}├── {action.dest} - {action.help}')
            continue

        for i, choice_action in enumerate(action._choices_actions):
            subparser_name = choice_action.dest
            help_text = choice_action.help
            print(f'{"│   " * (indent - 1)}├── {subparser_name} - {help_text}')

            subparser = action.choices[subparser_name]
            print_command_tree(subparser, indent + 1)


def _run_tests(args) -> None:
    """
    Handler for the `test` command --- runs pytest on the `tests/` directory.

    :param args: Empty CLI arguments.
    :return: Exits after completion.
    """

    logger.info('Starting Tests...')

    tests_path = os.path.join(os.path.dirname(__file__), 'tests')
    return_code = pytest.main([tests_path])

    sys.exit(return_code)


def _run_export(args) -> bool:
    """
    Handler for the `export...` command --- exports item data to
    a specified file format and location.

    :param args: CLI arguments with `path` and `extension` values.
    :return: `True` if operation is completed successfully, `False` otherwise.
    """

    path = args.path
    extension = args.extension
    logger.info(f'Exporting Data As .{extension} File...')

    utils = ExportUtils()
    db = DBUtils()
    all_items = db.create_all_items(db.get_all_data_gs())

    match extension:
        case 'csv' | 'psv' | 'tsv':
            utils.sv_export(extension, path, all_items)
        case 'pdf':
            utils.pdf_export()
        case _:
            logger.warning(f'Unknown Export Type: {extension}')
            return False

    logger.info(f'Successfully Exported Data To .{extension} File')
    return True


def _run_qr(args) -> bool:
    """
    Handler for the `qr...` command --- generates
    and saves a QR code for an item.

    :param args: CLI arguments with `path` and `part_num` values.
    :return: `True` if operation is completed successfully, `False` otherwise.
    """

    path = args.path
    part_num = args.part_num
    logger.info(f'Exporting {part_num} QR Code As .PNG...')
    utils = ExportUtils()

    image = utils.create_code(part_num)
    if not image:
        return False

    if not utils.save_code(image, path):
        return False

    logger.info(f'Successfully Exported {part_num} QR Code')
    return True


def _run_sync_databases(args) -> bool:
    """
    Handler for the `sync` command --- synchronizes
    the local and remote database.

    :param args: Empty CLI arguments.
    :return: `True` if operation is completed successfully, `False` otherwise.
    """

    logger.info('Syncing Databases...')
    utils = DBUtils()
    if not utils.sql_database:
        logger.info('No MySQL Database Present, '
                    'No Need For Database Synchronization')
        return True

    if not utils.sync_databases():
        return False
    logger.info('Successfully Synchronized Databases')
    return True


# endregion


# region Item Argument Functions
def _run_list_items(args) -> bool:
    """
    Handler for the `...items -l/--list` command
    --- lists all items in the database.

    :param args: Empty CLI arguments.
    :return: `True` if operation is completed successfully, `False` otherwise.
    """

    try:
        _list_items()
        return True
    except Exception as e:
        logger.error(f'Failed To List All Database Items: {e}')
        return False


def _run_search_items(args) -> bool:
    """
    Handler for the `...items search...` command
    --- searches items by a given string.

    :param args: CLI argument with `part_num` search string value.
    :return: `True` if operation is completed successfully, `False` otherwise.
    """

    try:
        _list_items(args.search_string)
        return True
    except Exception as e:
        logger.error(f'Failed To Search For Item In Databases: {e}')
        return False


def _run_add_item(args) -> bool:
    """
    Handler for the `...item add...` command
    --- adds a new item to the database.

    :param args: CLI arguments with 10 values representing
    item detail in the Google Sheet's order.
    :return: `True` if operation is completed successfully, `False` otherwise.
    """

    logger.info(f'Adding "{args.values[0]}" To Databases...')

    try:
        vals: list[Union[str, int]] = [
            value if i not in [3, 4, 5, 6, 7, 8]
            else int(value)
            for i, value in enumerate(args.values)
        ]
        item = Item(*vals)

        utils = DBUtils()
        if utils.find_item(item.part_num):
            raise Exception(f'"{item.part_num}" Already In Items Databases.')

        utils.update_items_database(DatabaseUpdateType.ADD, item)

        logger.info(f'Successfully Added "{item.part_num}" To Items Databases')
        return True
    except Exception as e:
        logger.error(f'Failed To Add Item To Items Database: {e}')
        return False


def _run_remove_item(args) -> bool:
    """
    Handler for the `...item remove...` command
    --- removes an item by part number.

    :param args: CLI argument with `part_num` value.
    :return: `True` if operation is completed successfully, `False` otherwise.
    """

    logger.info(f'Removing "{args.part_num}" From Databases...')

    utils = DBUtils()
    item = utils.find_item(args.part_num)
    if not item:
        logger.error(f'Could Not Locate "{args.part_num}" In Databases')
        return False

    if not utils.update_items_database(DatabaseUpdateType.REMOVE, item):
        return False

    logger.info(f'Successfully Removed {item.part_num} From Databases')
    return True


def _run_edit_item(args) -> bool:
    """
    Handler for the `edit` command
    --- edits an item by specified part number and values.
    and field specified changes.

    :param args: CLI arguments with one `part_num`
    and up to 9 individual field values.
    :return: `True` if operation is completed successfully, `False` otherwise.
    """

    logger.info(f'Editing {args.part_num} In Databases...')

    utils = DBUtils()
    item = utils.find_item(args.part_num)
    if not item:
        logger.error(f'Could Not Locate "{args.part_num}" In Databases')
        return False

    change_vals_dict: dict[str, str] = {}
    value: str
    for value in args.values:
        split_arg: list[str, str] = value.split('=')
        change_vals_dict[split_arg[0]] = split_arg[1]

    for key, value in change_vals_dict.items():
        item[key] = value

    if not utils.update_items_database(DatabaseUpdateType.EDIT, item):
        return False

    logger.info(f'Successfully Updated {item.part_num}\'s Values In Databases')
    return True


# endregion


# region User Argument Functions
def _run_list_users(args) -> bool:
    """
    Handler for the `...users -l/--list` command
    --- lists all users in the database.

    :param args: Empty CLI arguments.
    :return: `True` if operation is completed successfully, `False` otherwise.
    """

    try:
        _list_users()
        return True
    except Exception as e:
        logger.error(f'Failed To List All Database Users: {e}')
        return False


def _run_search_users(args) -> bool:
    """
    Handler for the `...users search...` command
    --- searches users by username substring.

    :param args: CLI argument with `username` search string value.
    :return: `True` if operation is completed successfully, `False` otherwise.
    """

    try:
        _list_users(args.part_num)
        return True
    except Exception as e:
        logger.error(f'Failed To Search For User In Database: {e}')
        return False


def _run_add_user(args) -> bool:
    """
    Handler for the `...users add...` command
    --- adds a new user to the database.

    :param args: CLI arguments with one `username` value.
    :return: `True` if operation is completed successfully, `False` otherwise.
    """

    logger.info('Adding User To Databases...')

    utils = DBUtils()
    username_arg = args.username
    if username_arg in utils.get_all_users_gs():
        logger.warning(f'"{username_arg}" Already In Users Databases')
        return False

    if not utils.update_users_database(DatabaseUpdateType.ADD, username_arg):
        return False

    logger.info(f'Successfully Added "{username_arg}" To Users Databases')
    return True


def _run_remove_user(args) -> bool:
    """
    Handler for the `...users remove...` command
    --- removes a user by username.

    :param args: CLI arguments with one `username` value.
    :return: `True` if operation is completed successfully, `False` otherwise.
    """

    logger.info('Removing User From Databases...')

    username_arg = args.username
    if not DBUtils().update_users_database(
            DatabaseUpdateType.REMOVE,
            username_arg
    ):
        return False

    logger.info(f'Successfully Removed {username_arg} From Databases')
    return True


# endregion


# region Printing Functions
def _list_items(search_value='') -> None:
    """
    Prints a formatted report of all stock items,
    optionally filtered by a search value.

    :param search_value: Optional substring to filter items.
    """

    logger.info(
        'Gathering Item Data...'
        if not search_value
        else f'Searching For Items With "{search_value}"...'
    )

    all_data: list[dict[str, Union[int, str, None]]] = DBUtils().get_all_data_gs()
    headers = [
        '#', 'Name', 'Manufacturer', 'Total',
        'B750 Stock', 'B757 Stock', 'B750 Min',
        'B757 Min', 'Excess', 'Status', 'Description'
    ]
    table = PrettyTable(headers)
    table._max_width = {'Name': 14, 'Description': 80}
    table.align['Description'] = 'l'

    print('\n[+] Stock Items Report')

    i: int
    data: dict[str, Union[int, str, None]]
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
            data['Min Sallies'],
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
        table.add_row(row)

    print(table)
    print(
        '[*] Total Items:', total, '| Out Of Stock:', out_of_stock,
        '| Low Stock:', low_stock, '| In Stock:', in_stock, '| Other:',
        other
    )
    logger.info('Successfully Printed Items')


def _list_users(search_value='') -> None:
    """
    Prints a list of all users in the database,
    optionally filtered by a substring.

    :param search_value: Optional username substring to filter users.
    """

    logger.info(
        'Gathering User Data...'
        if not search_value
        else f'Searching For Usernames With "{search_value}"...'
    )
    all_users: set[str] = DBUtils().get_all_users_gs()
    table = PrettyTable(['#', 'Username'])

    print('\n[+] Users Report')

    i: int
    username: str
    total = 0
    for i, username in enumerate(all_users):
        if search_value and search_value.lower() not in username.lower():
            continue
        total += 1
        table.add_row([i + 1, username])

    print(table)
    print('[*] Total Users:', total)
    logger.info('Successfully Printed Users')
# endregion
