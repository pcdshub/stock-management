import logging

import pytest

from stock_manager.__main__ import main


def test_help(monkeypatch):
    monkeypatch.setattr('sys.argv', ['stock_manager', '--help'])
    with pytest.raises(SystemExit):
        main()


@pytest.mark.parametrize('version_command', ['-v', '--version'])
def test_version(monkeypatch, capsys, version_command: str):
    import stock_manager
    
    monkeypatch.setattr('sys.argv', ['stock_manager', version_command])
    with pytest.raises(SystemExit):
        main()
    
    captured = capsys.readouterr()
    assert captured.out.strip() == stock_manager.__version__


def test_sync(monkeypatch, caplog):
    caplog.set_level(logging.INFO)
    monkeypatch.setattr('sys.argv', ['stock_manager', 'sync'])
    main()
    assert 'Successfully Synchronized Databases' in caplog.text, \
        f'Expected success message not found in logs: {caplog.text}'


@pytest.mark.parametrize(
        'category, list_command',
        [
            ('items', '-l'),
            ('items', '--list'),
            ('users', '-l'),
            ('users', '--list')
        ]
)
def test_no_args_commands(monkeypatch, caplog, category: str, list_command: str):
    caplog.set_level(logging.INFO)
    monkeypatch.setattr('sys.argv', ['stock_manager', category, list_command])
    main()
    assert 'Successfully Printed ' in caplog.text, \
        f'Expected success message not found in logs: {caplog.text}'


@pytest.mark.parametrize(
        'command, arg, path',
        [
            ('export', 'csv', ''),
            ('export', 'csv', './exports'),
            ('qr', 'test', ''),
            ('qr', 'test', './exports'),
        ]
)
def test_file_export_commands(monkeypatch, caplog, command: str, arg: str, path: str):
    caplog.set_level(logging.INFO)
    if not path:
        monkeypatch.setattr('sys.argv', ['stock_manager', command, arg])
    else:
        monkeypatch.setattr('sys.argv', ['stock_manager', command, arg, path])
    main()
    assert 'Successfully Exported' in caplog.text, \
        f'Expected success message not found in logs: {caplog.text}'


@pytest.mark.parametrize(
        'category, search_string',
        [
            ('items', 'BK9000'),
            ('users', 'username')
        ]
)
def test_search_commands(monkeypatch, caplog, category: str, search_string: str):
    caplog.set_level(logging.INFO)
    monkeypatch.setattr('sys.argv', ['stock_manager', category, 'search', search_string])
    main()
    assert 'Successfully Printed ' in caplog.text, \
        f'Expected success message not found in logs: {caplog.text}'


def test_add_edit_remove_item(monkeypatch, caplog):
    caplog.set_level(logging.INFO)
    monkeypatch.setattr(
            'sys.argv',
            [
                'stock_manager',
                'items',
                'add',
                'test', 'test', 'test',
                0, 0, 0, 0, 0, 0,
                'Out Of Stock'
            ]
    )
    main()
    assert 'Successfully Added' in caplog.text, \
        f'Expected success message not found in logs: {caplog.text}'
    
    monkeypatch.setattr('sys.argv', ['stock_manager', 'items', 'edit', 'test', 'total=999'])
    main()
    assert 'Successfully Updated' in caplog.text, \
        f'Expected success message not found in logs: {caplog.text}'
    
    monkeypatch.setattr('sys.argv', ['stock_manager', 'items', 'remove', 'test'])
    main()
    assert 'Successfully Removed' in caplog.text, \
        f'Expected success message not found in logs: {caplog.text}'


def test_add_remove_user(monkeypatch, caplog):
    caplog.set_level(logging.INFO)
    monkeypatch.setattr('sys.argv', ['stock_manager', 'users', 'add', 'test_username'])
    main()
    assert 'Successfully Added' in caplog.text, \
        f'Expected success message not found in logs: {caplog.text}'
    
    monkeypatch.setattr('sys.argv', ['stock_manager', 'users', 'remove', 'test_username'])
    main()
    assert 'Successfully Removed' in caplog.text, \
        f'Expected success message not found in logs: {caplog.text}'
