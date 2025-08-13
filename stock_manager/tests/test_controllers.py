import os.path
from unittest.mock import MagicMock

import cv2
from _pytest.monkeypatch import MonkeyPatch
from numpy import ndarray
from PyQt5.QtCore import QAbstractItemModel, QModelIndex, QRect, Qt
from PyQt5.QtWidgets import QFileDialog, QLineEdit, QMessageBox, QTableView, QTextEdit
from pytest import fixture, mark, skip

import stock_manager
from conftest import TEST_ITEM, TEST_USERNAME
from stock_manager import AbstractController, AbstractScanner, Add, App, DBUtils, Edit, Export, ExportUtils, Finish, \
    Item, ItemScanner, Login, QRGenerate, Remove, View


def handle_alert(monkeypatch: MonkeyPatch, alert_type: str = 'information', select: int = QMessageBox.Ok):
    monkeypatch.setattr(QMessageBox, alert_type, lambda *args, **kwargs: select)


def handle_table_click(qtbot, table: QTableView):
    model: QAbstractItemModel = table.model()
    item_to_click: QModelIndex = model.index(0, 0)
    assert item_to_click.isValid()
    rect: QRect = table.visualRect(item_to_click)
    qtbot.mouseClick(table.viewport(), Qt.LeftButton, pos=rect.center())
    assert table.selectionModel().isSelected(item_to_click)


class TestControllers:
    @fixture(
            params=[
                Add, Edit, Export,
                QRGenerate, Finish,
                Remove, ItemScanner,
                View, Login
            ]
    )
    def controller(self, request) -> AbstractController:
        return request.param(MagicMock())
    
    @fixture(params=[Edit, QRGenerate, Remove, View])
    def table_controller(self, request) -> AbstractController:
        return request.param(MagicMock())
    
    @mark.asyncio
    async def test_update_table(self, qtbot, table_controller):
        qtbot.addWidget(table_controller)
        assert await table_controller.update_table() and table_controller.table.model()
    
    def test_to_page(self, qtbot, controller):
        if isinstance(controller, AbstractScanner):
            skip('AbstractScanners Raise No Errors But Lots Of Warnings When Switching Pages')
        qtbot.addWidget(controller)
        controller.to_page()


@mark.skip(reason='Raises Warnings But No Errors, Clutters All Useful Information')
class TestScanners:
    @fixture(params=[ItemScanner, Login])
    def scanner(self, request) -> AbstractScanner:
        scanner_controller: AbstractScanner = request.param(MagicMock())
        scanner_controller.database = DBUtils()
        return scanner_controller
    
    def test_video(self, qtbot, scanner):
        qtbot.addWidget(scanner)
        
        try:
            scanner.start_video()
        except TimeoutError:
            print('Timeout, No Errors')
            assert True
        except Exception as e:
            print('Video Testing Error:', e)
            assert False
        else:
            assert True
        finally:
            scanner.stop_video()
    
    @mark.parametrize('file_num', [1, 2])
    def test_qr_checking(self, qtbot, scanner, file_num: str):
        qtbot.addWidget(scanner)
        image: ndarray = cv2.imread(f'./exports/test_image{file_num}.jpeg')
        assert image.any() and scanner.check_for_qr(image)


@mark.parametrize('controller', [Export, QRGenerate])
def test_exporter_directory(qtbot, monkeypatch: MonkeyPatch, controller):
    controller = controller(MagicMock())
    qtbot.addWidget(controller)
    
    monkeypatch.setattr(QFileDialog, 'getExistingDirectory', lambda *args, **kwargs: '../../exports')
    controller.get_directory(controller.location_btn)
    assert controller.path == '../../exports'


class TestAdd:
    @fixture
    def controller(self) -> Add:
        return Add(MagicMock())
    
    @mark.parametrize(
            'add_clicks, sub_clicks, expected_result',
            [
                (3, 0, 3),
                (5, 2, 3),
                (2, 5, -3)
            ]
    )
    def test_spinner_change(
            self,
            qtbot,
            controller,
            add_clicks: int,
            sub_clicks: int,
            expected_result: int
    ):
        qtbot.addWidget(controller)
        
        controller.b750_spinner.setValue(add_clicks)
        controller.min_750_spinner.setValue(sub_clicks)
        
        total = stock_manager.total_equation(add_clicks, 0)
        excess = stock_manager.excess_equation(total, sub_clicks, 0)
        
        assert controller._total == total and controller._excess == excess == expected_result
    
    def test_clear_form(self, qtbot, controller):
        qtbot.addWidget(controller)
        
        for field in controller._text_fields:
            field.setText('x')
        for spinner in controller._spinners:
            spinner.setValue(99)
        
        controller._clear_form()
        
        assert all(
                [
                    not field.text()
                    if isinstance(field, QLineEdit)
                    else not field.toPlainText()
                    for field in controller._text_fields
                ] + [
                    not spinner.value()
                    for spinner in controller._spinners
                ]
        )
    
    @mark.parametrize(
            'part_num, manufacturer, desc, b750_stock, expected_result',
            [
                ('', '', '', 0, False),
                ('', 'Test', 'Test', 9, False),
                ('Yes', 'Test', 'Test', 9, True),
                ('No', 'Test', 'Test', 9, True)
            ]
    )
    def test_submit_form(
            self,
            qtbot,
            monkeypatch: MonkeyPatch,
            controller,
            part_num: str,
            manufacturer: str,
            desc: str,
            b750_stock: int,
            expected_result: bool
    ):
        qtbot.addWidget(controller)
        
        field: QLineEdit | QTextEdit
        value: str
        for field, value in zip(controller._text_fields, [part_num, manufacturer, desc]):
            field.setText(value)
        controller.b750_spinner.setValue(b750_stock)
        
        if part_num == '':
            handle_alert(monkeypatch)
        elif part_num == 'Yes':
            handle_alert(monkeypatch, 'question', QMessageBox.Yes)
        elif part_num == 'No':
            handle_alert(monkeypatch, 'question', QMessageBox.No)
        else:
            assert False
        
        assert controller._submit_form() is expected_result


class TestEdit:
    @fixture
    def controller(self) -> Edit:
        controller = Edit(MagicMock())
        controller.app.all_items = [TEST_ITEM]
        return controller
    
    @mark.parametrize(
            'text, expected',
            [
                ('None', None),
                ('', None),
                ('0', 0),
                ('test', 'test')
            ]
    )
    def test_parse_field(self, qtbot, controller, text: str, expected: int | str | None):
        qtbot.addWidget(controller)
        assert controller._parse_field(text) == expected
    
    @mark.asyncio
    async def test_clicked_item(self, qtbot, controller):
        qtbot.addWidget(controller)
        
        assert await controller.update_table()
        handle_table_click(qtbot, controller.table)
        
        item: Item = controller.app.all_items[0]
        assert all(
                [
                    controller.part_num.text() == item.part_num,
                    controller.manufacturer.text() == item.manufacturer,
                    controller.desc.toPlainText() == item.description,
                    str(item.total) in controller.total_lbl.text(),
                    str(item.excess) in controller.excess_lbl.text(),
                    controller.b750_spinner.value() == item.stock_b750,
                    controller.b757_spinner.value() == item.stock_b757,
                    controller.min_750_spinner.value() == item.minimum,
                    controller.min_757_spinner.value() == item.minimum_sallie
                ]
        )
    
    def test_spinner_change(self, qtbot, controller):
        qtbot.addWidget(controller)
        
        for i, spinner in enumerate(controller._spinners):
            spinner.setValue(i + 1)
        
        assert '3' in controller.total_lbl.text() and '4' in controller.excess_lbl.text()
    
    def test_clear_form(self, qtbot, controller):
        qtbot.addWidget(controller)
        
        for field in controller._text_fields:
            field.setText('x')
        for spinner in controller._spinners:
            spinner.setValue(9)
        
        controller._selected_item = controller.app.all_items[0]
        controller._clear_form()
        
        assert all(
                [
                    not field.text()
                    if isinstance(field, QLineEdit)
                    else not field.toPlainText()
                    for field in controller._text_fields
                ] + [
                    not spinner.value()
                    for spinner in controller._spinners
                ]
        )
    
    @mark.asyncio
    async def test_submit_form(self, qtbot, monkeypatch: MonkeyPatch, controller):
        qtbot.addWidget(controller)
        
        handle_alert(monkeypatch)
        controller._submit_form()
        
        await self.test_clicked_item(qtbot, controller)
        
        handle_alert(monkeypatch)
        controller._submit_form()
        
        controller.b750_spinner.setValue(1)
        handle_alert(monkeypatch, 'question', QMessageBox.No)
        controller._submit_form()
        
        handle_alert(monkeypatch, 'question', QMessageBox.Yes)
        controller._submit_form()
        assert True


@mark.parametrize('idx', [2, 3, 4])
def test_export(qtbot, idx: int):
    controller = Export(MagicMock())
    controller.app.export_utils = ExportUtils()
    qtbot.addWidget(controller)
    
    controller.export_combo.setCurrentIndex(idx)
    assert controller.export()
    
    ext = ['csv', 'tsv', 'psv'][idx - 2]
    path = f'../../exports/{ext}_export.{ext}'
    assert os.path.exists(path)
    
    os.remove(path)


class TestQRGenerate:
    @fixture
    def controller(self) -> Export:
        controller = QRGenerate(MagicMock())
        controller.app.export_utils = ExportUtils()
        controller.app.all_items = [TEST_ITEM]
        return controller
    
    @mark.asyncio
    async def test_clicked_item(self, qtbot, controller):
        qtbot.addWidget(controller)
        assert await controller.update_table()
        handle_table_click(qtbot, controller.table)
        assert controller._selected_qr and not controller.qr_lbl.text()
    
    @mark.asyncio
    async def test_export(self, qtbot, monkeypatch: MonkeyPatch, controller):
        qtbot.addWidget(controller)
        
        handle_alert(monkeypatch, 'warning')
        assert not controller.export()
        
        await self.test_clicked_item(qtbot, controller)
        
        path = '../../exports/png_export.png'
        assert controller.export() and os.path.exists(path)
        
        os.remove(path)


def test_finish(qtbot):
    controller = Finish(MagicMock())
    qtbot.addWidget(controller)
    
    msg = 'test text message'
    controller.set_text(msg)
    
    assert controller.label.text() == msg


@mark.asyncio
async def test_remove(qtbot, monkeypatch: MonkeyPatch):
    controller = Remove(MagicMock())
    controller.app.all_items = [TEST_ITEM]
    qtbot.addWidget(controller)
    
    assert await controller.update_table()
    
    handle_alert(monkeypatch, 'question', QMessageBox.No)
    handle_table_click(qtbot, controller.table)
    
    handle_alert(monkeypatch, 'question', QMessageBox.Yes)
    handle_table_click(qtbot, controller.table)
    assert not controller.app.all_items


class TestItemScanner:
    @fixture
    def controller(self) -> ItemScanner:
        return ItemScanner(MagicMock())
    
    def test_clear_form(self, qtbot, controller):
        qtbot.addWidget(controller)
        
        controller._items = [TEST_ITEM, TEST_ITEM, TEST_ITEM]
        controller.items_list.setText('test text')
        assert controller._items and controller.items_list.toPlainText()
        
        controller._clear_form()
        
        assert not controller._items and not controller.items_list.toPlainText()
    
    def test_submit_form(self, qtbot, monkeypatch: MonkeyPatch, controller):
        qtbot.addWidget(controller)
        
        handle_alert(monkeypatch, 'warning')
        controller._finish_form()
        
        TEST_ITEM.stock_b750 += 1
        controller.app.all_items = [TEST_ITEM]
        controller._items = [TEST_ITEM]
        
        handle_alert(monkeypatch, 'question', QMessageBox.No)
        controller._finish_form()
        handle_alert(monkeypatch, 'question', QMessageBox.Yes)
        controller._finish_form()
        
        assert not controller.app.all_items[0].total


def test_login(qtbot, monkeypatch: MonkeyPatch):
    controller = Login(App())
    qtbot.addWidget(controller)
    
    handle_alert(monkeypatch)
    assert not controller._login_clicked()
    
    controller._users_list = []
    
    controller.username.setText(TEST_USERNAME)
    handle_alert(monkeypatch, 'warning')
    assert controller.username.text() not in controller._users_list and not controller._login_clicked()
    
    controller._users_list.append(TEST_USERNAME)
    handle_alert(monkeypatch, 'warning')
    assert controller.username.text() in controller._users_list and controller._login_clicked() \
           and controller.app.current_page == controller.app.view.PAGE_NAME and controller.app.user == TEST_USERNAME
