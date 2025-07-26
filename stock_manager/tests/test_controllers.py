from unittest.mock import MagicMock

import cv2
import pytest
from _pytest.monkeypatch import MonkeyPatch
from PyQt5.QtWidgets import QLineEdit, QMessageBox, QTextEdit
from pytestqt.qtbot import QtBot

import stock_manager
from stock_manager import AbstractController, AbstractScanner, Add, Edit, Export, Finish, ItemScanner, Login, \
    QRGenerate, Remove, View


class TestAllControllers:
    @pytest.fixture(
            params=[
                Add, Edit, Export,
                QRGenerate, Finish,
                Remove, ItemScanner,
                View, Login
            ]
    )
    def controller(self, request) -> AbstractController:
        return request.param(MagicMock())
    
    def test_basic(self, qtbot: QtBot, controller):
        qtbot.addWidget(controller)
    
    @pytest.mark.asyncio
    async def test_update_table(self, qtbot: QtBot, controller):
        qtbot.addWidget(controller)
        
        if not hasattr(controller, 'table'):
            pytest.skip(f'{controller.__class__.__name__} Has No Table')
        
        assert await controller.update_table() is True
    
    def test_to_page(self, qtbot: QtBot, controller):
        if isinstance(controller, AbstractScanner):
            pytest.skip('AbstractScanners Raise No Errors But Lots Of Warnings When Switching Pages')
        qtbot.addWidget(controller)
        controller.to_page()


@pytest.mark.skip(reason='Raises Warnings But No Errors, Clutters All Useful Information')
class TestScanners:
    @pytest.fixture(params=[ItemScanner, Login])
    def scanner(self, request) -> AbstractScanner:
        from stock_manager import DBUtils
        
        scanner_controller: AbstractScanner = request.param(MagicMock())
        scanner_controller.database = DBUtils()
        return scanner_controller
    
    def test_video(self, qtbot: QtBot, scanner):
        qtbot.addWidget(scanner)
        try:
            scanner.start_video()
            scanner.stop_video()
        except TimeoutError:
            print('Timeout, No Errors')
            assert True
        except Exception as e:
            print(f'Error: {e}')
            assert False
    
    def test_qr_checking(self, qtbot: QtBot, scanner, file_name: str):
        from numpy import ndarray
        
        qtbot.addWidget(scanner)
        image: ndarray = cv2.imread('./assets/' + file_name)
        if not image.any():
            assert False
        scanner.check_for_qr(image)


class TestExporters:
    pass


class TestAdd:
    @pytest.fixture
    def controller(self) -> Add:
        return Add(MagicMock())
    
    @pytest.mark.parametrize(
            'add_clicks, sub_clicks, expected_result',
            [
                (3, 0, 3),
                (5, 2, 3),
                (2, 5, -3)
            ]
    )
    def test_spinner_change(
            self,
            qtbot: QtBot,
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
    
    def test_clear_form(self, qtbot: QtBot, controller):
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
                ]
        ) and all(
                [
                    not spinner.value()
                    for spinner in controller._spinners
                ]
        )
    
    @pytest.mark.parametrize(
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
            qtbot: QtBot,
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
            monkeypatch.setattr(QMessageBox, 'information', lambda *args, **kwargs: QMessageBox.Ok)
        elif part_num == 'Yes':
            monkeypatch.setattr(QMessageBox, 'information', lambda *args, **kwargs: QMessageBox.Yes)
        elif part_num == 'No':
            monkeypatch.setattr(QMessageBox, 'information', lambda *args, **kwargs: QMessageBox.No)
        else:
            assert False
        
        assert controller._submit_form() is expected_result
