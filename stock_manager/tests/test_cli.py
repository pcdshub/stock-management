import sys

import pytest

from stock_manager.__main__ import main


@pytest.fixture(
        params=[
            '-v', '--version',
            '-s', '--sync-databases',
            '-li', '--list-items',
            '-lu', '--list-users'
        ]
)
def no_args_command(request) -> str:
    return request.param


def test_help(monkeypatch):
    monkeypatch.setattr(sys, 'argv', ['stock_manager', '--help'])
    with pytest.raises(SystemExit):
        main()


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
