import logging
import sys

import pytest

from stock_manager.__main__ import main


def test_help(monkeypatch):
    monkeypatch.setattr(sys, 'argv', ['stock_manager', '--help'])
    with pytest.raises(SystemExit):
        main()


@pytest.mark.parametrize(
        'version_command', ['-v', '--version']
)
def test_version(monkeypatch, caplog, version_command):
    caplog.set_level(logging.INFO)
    monkeypatch.setattr(sys, 'argv', ['stock_manager', version_command])
    main()
    assert 'Version: ' in caplog.text


@pytest.mark.parametrize(
        'version_command', ['-s', '--sync-databases']
)
def test_version(monkeypatch, caplog, version_command):
    caplog.set_level(logging.INFO)
    monkeypatch.setattr(sys, 'argv', ['stock_manager', version_command])
    main()
    assert 'Successfully Synchronized Databases' in caplog.text


@pytest.mark.parametrize(
        'list_command',
        [
            '-li', '--list-items',
            '-lu', '--list-users'
        ]
)
def test_no_args_commands(monkeypatch, caplog, list_command):
    caplog.set_level(logging.INFO)
    monkeypatch.setattr(sys, 'argv', ['stock_manager', list_command])
    main()
    assert 'Successfully Printed ' in caplog.text


@pytest.mark.parametrize(
        'command, arg',
        [
            ('-e', 'csv'),
            ('--export', 'csv'),
            ('-qr', 'test'),
            ('--create-qr', 'test')
        ]
)
def test_file_export_commands(monkeypatch, caplog, command: str, arg: str):
    caplog.set_level(logging.INFO)
    monkeypatch.setattr(sys, 'argv', ['stock_manager', command, './exports', arg])
    main()
    assert 'Successfully Exported' in caplog.text


@pytest.mark.parametrize(
        'command, arg',
        [
            ('-si', 'BK9000'),
            ('--search-items', 'BK9000'),
            ('-su', 'username'),
            ('--search-users', 'username')
        ]
)
def test_search_commands(monkeypatch, caplog, command: str, arg: str):
    caplog.set_level(logging.INFO)
    monkeypatch.setattr(sys, 'argv', ['stock_manager', command, arg])
    main()
    assert 'Successfully Printed ' in caplog.text


@pytest.mark.parametrize(
        'add_command, edit_command, remove_command', [
            ('-ai', '-ei', '-ri'),
            ('--add-item', '--edit', '--remove-item')
        ]
)
def test_add_edit_remove_item(monkeypatch, caplog, add_command: str, edit_command: str, remove_command: str):
    caplog.set_level(logging.INFO)
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
    assert 'Successfully Added' in caplog.text
    monkeypatch.setattr(sys, 'argv', ['stock_manager', edit_command, 'test', 'total=999'])
    main()
    assert 'Successfully Updated' in caplog.text
    monkeypatch.setattr(sys, 'argv', ['stock_manager', remove_command, 'test'])
    main()
    assert 'Successfully Removed' in caplog.text


@pytest.mark.parametrize(
        'add_command, remove_command', [
            ('-au', '-ru'),
            ('--add-user', '--remove-user')
        ]
)
def test_add_remove_user(monkeypatch, caplog, add_command: str, remove_command: str):
    caplog.set_level(logging.INFO)
    monkeypatch.setattr(sys, 'argv', ['stock_manager', add_command, 'test_username'])
    main()
    assert 'Successfully Added' in caplog.text
    monkeypatch.setattr(sys, 'argv', ['stock_manager', remove_command, 'test_username'])
    main()
    assert 'Successfully Removed' in caplog.text
