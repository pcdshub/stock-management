import logging
import os.path
from typing import Literal
from unittest.mock import MagicMock

from pytest import fixture, mark

from stock_manager.utils import DatabaseUpdateType, DBUtils, ExportUtils

from .conftest import TEST_ITEM, TEST_USERNAME


class TestDatabase:
    @fixture
    def database(self) -> DBUtils:
        return DBUtils()

    def test_sync_databases(self, database):
        original_items_gs = database.get_all_data_gs()
        original_users_gs = database.get_all_users_gs()
        original_users_sql = database.get_all_users_sql()
        original_items_sql = database.get_all_data_sql()

        new_users_gs = original_users_gs.copy()
        new_users_gs.add(TEST_USERNAME)
        new_users_sql = original_users_sql.copy()
        new_users_sql.add(TEST_USERNAME)

        def update_sql(update_type: DatabaseUpdateType) -> None:
            database._update_items_sql(update_type, TEST_ITEM)
            database._update_users_sql(update_type, TEST_USERNAME)
            database.sync_databases()

        def update_gs(update_type: DatabaseUpdateType) -> None:
            database._update_items_gs(update_type, TEST_ITEM)
            database._update_users_gs(update_type, TEST_USERNAME)
            database.sync_databases()

        def database_altered() -> bool:
            return (
                    database.get_all_data_gs() != original_items_gs
                    and database.get_all_data_sql() != original_items_sql
                    and database.get_all_users_gs()
                    == database.get_all_users_sql()
                    == new_users_gs == new_users_sql
            )

        def database_unaltered() -> bool:
            return (
                    database.get_all_data_gs() == original_items_gs
                    and database.get_all_data_sql() == original_items_sql
                    and database.get_all_users_gs()
                    == database.get_all_users_sql()
                    == original_users_gs == original_users_sql
            )

        update_sql(DatabaseUpdateType.ADD)
        assert database_unaltered

        update_gs(DatabaseUpdateType.ADD)
        assert database_altered

        update_sql(DatabaseUpdateType.REMOVE)
        assert database_altered

        update_gs(DatabaseUpdateType.REMOVE)
        assert database_unaltered

    def test_fetch_data_gs(self, database):
        assert database.get_all_data_gs()

    def test_fetch_data_sql(self, database):
        assert database.get_all_data_sql()

    def test_fetch_users_gs(self, database):
        assert database.get_all_users_gs()

    def test_fetch_users_sql(self, database):
        assert database.get_all_users_sql()

    def test_update_database(self, database):
        database.update_items_database(DatabaseUpdateType.ADD, TEST_ITEM)
        assert database.find_item(TEST_ITEM.part_num) == TEST_ITEM

        TEST_ITEM.stock_b750 = 999
        database.update_items_database(DatabaseUpdateType.EDIT, TEST_ITEM)
        assert database.find_item(TEST_ITEM.part_num) == TEST_ITEM

        database.update_items_database(DatabaseUpdateType.REMOVE, TEST_ITEM)
        assert not database.find_item(TEST_ITEM.part_num)

    def test_create_items(self, database):
        assert database.create_all_items(database.get_all_data_gs())


class TestLogger:
    def test_info_log(self, caplog):
        msg = 'Test Info Log'
        caplog.set_level(logging.INFO)
        logging.getLogger().info(msg)
        assert msg in caplog.text

    def test_warning_log(self, caplog):
        msg = 'Test Warning Log'
        caplog.set_level(logging.INFO)
        logging.getLogger().warning(msg)
        assert msg in caplog.text

    def test_error_log(self, caplog):
        msg = 'Test Error Log'
        caplog.set_level(logging.INFO)
        logging.getLogger().error(msg)
        assert msg in caplog.text


class TestExports:
    @fixture
    def exports(self) -> ExportUtils:
        return ExportUtils()

    @mark.parametrize(
        'file_type, expected_path',
        [
            ('py', './exports/py_export.py'),
            ('txt', './exports/txt_export2.txt')
        ]
    )
    def test_valid_name(self, exports, file_type: str, expected_path: str):
        assert expected_path == exports._get_valid_name(file_type, './exports')

    def test_pdf_export(self, exports):
        pass

    @mark.parametrize('export_type', ['csv', 'tsv', 'psv'])
    def test_sv_export(
        self,
        exports,
        export_type: Literal['csv', 'tsv', 'psv']
    ):
        exports.sv_export(export_type, './exports', [MagicMock()])
        path = f'./exports/{export_type}_export.{export_type}'
        assert os.path.exists(path)

        os.remove(path)

    def test_make_qr_code(self, exports):
        assert exports.create_code(TEST_ITEM.part_num)

    def test_save_qr_code(self, exports):
        exports.save_code(exports.create_code('test part'), './exports')
        path = './exports/png_export.png'
        assert os.path.exists(path)

        os.remove(path)
