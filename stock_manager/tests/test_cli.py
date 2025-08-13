import logging
import os

from pytest import mark, raises

from stock_manager.__main__ import main

from .conftest import TEST_ITEM, TEST_USERNAME


def test_help(monkeypatch):
    monkeypatch.setattr('sys.argv', ['stock_manager', '--help'])
    with raises(SystemExit):
        main()


@mark.parametrize('tree_command', ['-t', '--tree'])
def test_tree(monkeypatch, tree_command: str):
    monkeypatch.setattr('sys.argv', ['stock_manager', tree_command])
    with raises(SystemExit):
        main()


@mark.parametrize('version_command', ['-v', '--version'])
def test_version(monkeypatch, capsys, version_command: str):
    import stock_manager

    monkeypatch.setattr('sys.argv', ['stock_manager', version_command])
    with raises(SystemExit):
        main()

    captured = capsys.readouterr()
    assert captured.out.strip() == stock_manager.__version__


def test_sync(monkeypatch, caplog):
    caplog.set_level(logging.INFO)
    monkeypatch.setattr('sys.argv', ['stock_manager', 'sync'])
    main()
    assert 'Successfully Synchronized Databases' in caplog.text, \
        f'Expected success message not found in logs: {caplog.text}'


@mark.parametrize(
    'category, list_command',
    [
        ('items', '-l'),
        ('items', '--list'),
        ('users', '-l'),
        ('users', '--list')
    ]
)
def test_list_commands(monkeypatch, caplog, category: str, list_command: str):
    caplog.set_level(logging.INFO)
    monkeypatch.setattr('sys.argv', ['stock_manager', category, list_command])
    main()
    assert 'Successfully Printed ' in caplog.text, \
        f'Expected success message not found in logs: {caplog.text}'


@mark.parametrize(
    'command, arg, path',
    [
        ('export', 'csv', ''),
        ('export', 'csv', './exports'),
        ('qr', TEST_ITEM.part_num, ''),
        ('qr', TEST_ITEM.part_num, './exports'),
    ]
)
def test_file_export_commands(
    monkeypatch,
    caplog,
    command: str,
    arg: str,
    path: str
):
    caplog.set_level(logging.INFO)
    if not path:
        monkeypatch.setattr('sys.argv', ['stock_manager', command, arg])
    else:
        monkeypatch.setattr('sys.argv', ['stock_manager', command, arg, path])
    main()

    path = './exports/' + (
        f'{arg}_export.{arg}'
        if command == 'export'
        else 'png_export.png'
    )

    assert 'Successfully Exported' in caplog.text, \
        f'Expected success message not found in logs: {caplog.text}' \
        and os.path.exists(path)

    os.remove(path)


@mark.parametrize(
    'category, search_string',
    [
        ('items', TEST_ITEM.part_num),
        ('users', TEST_USERNAME)
    ]
)
def test_search_commands(
    monkeypatch,
    caplog,
    category: str,
    search_string: str
):
    caplog.set_level(logging.INFO)
    monkeypatch.setattr(
        'sys.argv', ['stock_manager', category, 'search', search_string]
    )
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
            *TEST_ITEM
        ]
    )
    main()
    assert 'Successfully Added' in caplog.text, \
        f'Expected success message not found in logs: {caplog.text}'

    monkeypatch.setattr(
        'sys.argv', [
            'stock_manager',
            'items',
            'edit',
            TEST_ITEM.part_num,
            'stock_b750=999'
        ]
    )
    main()
    assert 'Successfully Updated' in caplog.text, \
        f'Expected success message not found in logs: {caplog.text}'

    monkeypatch.setattr(
        'sys.argv', [
            'stock_manager',
            'items',
            'remove',
            TEST_ITEM.part_num
        ]
    )
    main()
    assert 'Successfully Removed' in caplog.text, \
        f'Expected success message not found in logs: {caplog.text}'


def test_add_remove_user(monkeypatch, caplog):
    caplog.set_level(logging.INFO)
    monkeypatch.setattr(
        'sys.argv', [
            'stock_manager',
            'users',
            'add',
            TEST_USERNAME
        ]
    )
    main()
    assert 'Successfully Added' in caplog.text, \
        f'Expected success message not found in logs: {caplog.text}'

    monkeypatch.setattr(
        'sys.argv', [
            'stock_manager',
            'users',
            'remove',
            TEST_USERNAME
        ]
    )
    main()
    assert 'Successfully Removed' in caplog.text, \
        f'Expected success message not found in logs: {caplog.text}'
