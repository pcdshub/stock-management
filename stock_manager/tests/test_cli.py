import sys

import pytest

from stock_manager.__main__ import main


def test_help(monkeypatch):
    monkeypatch.setattr(sys, 'argv', ['stock_manager', '--help'])
    with pytest.raises(SystemExit):
        main()


@pytest.mark.parametrize(
        'no_args_command',
        [
            '-v', '--version',
            '-s', '--sync-databases',
            '-li', '--list-items',
            '-lu', '--list-users'
        ]
)
def test_no_args_commands(monkeypatch, no_args_command):
    monkeypatch.setattr(sys, 'argv', ['stock_manager', no_args_command])
    main()


@pytest.mark.parametrize(
        'command, arg',
        [
            ('-e', 'csv'),
            ('--export', 'csv'),
            ('-qr', 'test'),
            ('--create-qr', 'test')
        ]
)
def test_file_export_commands(monkeypatch, command: str, arg: str):
    monkeypatch.setattr(sys, 'argv', ['stock_manager', command, './exports', arg])
    main()


@pytest.mark.parametrize(
        'command, arg',
        [
            ('-si', 'BK9000'),
            ('--search-items', 'BK9000'),
            ('-su', 'username'),
            ('--search-users', 'username')
        ]
)
def test_search_commands(monkeypatch, command: str, arg: str):
    monkeypatch.setattr(sys, 'argv', ['stock_manager', command, arg])
    main()


@pytest.mark.parametrize(
        'add_command, edit_command, remove_command', [
            ('-ai', '-ei', '-ri'),
            ('--add-item', '--edit', '--remove-item')
        ]
)
def test_add_edit_remove_item(monkeypatch, add_command: str, edit_command: str, remove_command: str):
    monkeypatch.setattr(
            sys, 'argv',
            [
                'stock_manager',
                add_command,
                'test', 'test', 'test',
                0, 0, 0, 0, 0, 0,
                'Out Of Stock'
            ]
    )
    main()
    monkeypatch.setattr(sys, 'argv', ['stock_manager', edit_command, 'test', 'total=999'])
    main()
    monkeypatch.setattr(sys, 'argv', ['stock_manager', remove_command, 'test'])
    main()


@pytest.mark.parametrize(
        'add_command, remove_command', [
            ('-au', '-ru'),
            ('--add-user', '--remove-user')
        ]
)
def test_add_remove_user(monkeypatch, add_command: str, remove_command: str):
    monkeypatch.setattr(sys, 'argv', ['stock_manager', add_command, 'test_username'])
    main()
    monkeypatch.setattr(sys, 'argv', ['stock_manager', remove_command, 'test_username'])
    main()
