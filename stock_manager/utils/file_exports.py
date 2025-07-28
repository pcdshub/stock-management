"""
Export utilities for Stock Management Application.

Provides ExportUtils for managing different types of
data exportation for various application features.
"""

import logging
import os
from typing import Literal, TYPE_CHECKING

import qrcode
from PyQt5.QtWidgets import QMessageBox
from qasync import asyncSlot
from qrcode.image.base import BaseImage

if TYPE_CHECKING:
    from stock_manager import App


class ExportUtils:
    def __init__(self, instance: 'App'):
        """
        Initializes the ExportUtils class.
        
        :param instance: the main instance of `App`, use for access of `log`.
        """
        
        self._instance = instance
        self._logger = logging.getLogger()
    
    @staticmethod
    def _get_valid_name(ext: str, path: str) -> str:
        """
        Generate a unique file path for the export file.
        
        :param ext: The desired file extension.
        :param path: The directory to create file in.
        :return: A unique file path as a string.
        """
        
        name = f'{ext}_export'
        full_path = f'{path}/{name}.{ext}'
        
        count = 2
        while os.path.exists(full_path):
            full_path = f'{path}/{name}{count}.{ext}'
            count += 1
        
        return full_path
    
    @asyncSlot()
    async def pdf_export(self) -> None:
        """Asynchronously exports current data to PDF format."""
        
        pass  # TODO: add pdf generation
    
    @asyncSlot()
    async def sv_export(
            self,
            export_type: Literal['csv', 'tsv', 'psv'],
            path: str
    ) -> bool:
        """
        Asynchronously exports current data to a delimited text file (CSV, TSV, PSV).
        
        :param export_type: The file extension as the value (str) of an ExportType enum.
        :param path: The directory to create file in.
        :return: `True` if file is created and written to successfully, `False` if otherwise
        """
        
        delimiter = {
            'csv': ',',
            'tsv': '\t',
            'psv': '|'
        }.get(export_type)
        
        if not delimiter:
            print(f'Cannot Call sv_export() With Type: "{export_type}"')
            return False
        
        try:
            with open(self._get_valid_name(export_type, path), 'x') as f:
                for i, item in enumerate(self._instance.all_items):
                    line = ''
                    for var in item:
                        line += (str(var) if var else '') + delimiter
                    f.write(line[:-1] + '\n')
            return True
        except FileExistsError as e:
            print(f'That File Already Exists: {e}')
            self._logger.error(f'File Already Exists Error: {e}')
            QMessageBox.critical(
                    self._instance,
                    'File Exists Error',
                    'That File Already Exists, Try Changing File Types'
            )
            return False
        except Exception as e:
            export_type = export_type.upper()
            print(f'Failed To Export Data To {export_type}: {e}')
            self._logger.error(f'Failed To Export Data To {export_type}: {e}')
            QMessageBox.critical(
                    self._instance,
                    f'{export_type} Export Error',
                    f'Failed To Export Data To {export_type}, Try Changing File Types'
            )
            return False
    
    def create_code(self, part_num: str) -> BaseImage:
        """
        This method creates a QR code using the input `part_num` string and returns
        it as a `BaseImage` object.
        
        :param part_num: The string to encode in the QR code.
        :return: The generated QR code image.
        """
        
        try:
            qr = qrcode.QRCode()
            qr.add_data(part_num)
            qr.make()
            return qr.make_image()
        except Exception as e:
            print(f'Failed To Convert {part_num} To QR Image: {e}')
            self._logger.error(f'Failed To Convert {part_num} To QR Image: {e}')
            QMessageBox.critical(
                    self._instance,
                    'QR Code Conversion Error',
                    f'Failed To Convert {part_num} To QR Image'
            )
    
    def save_code(self, qr_code: BaseImage, path: str) -> bool:
        """
        Save a QR code image to a specified file path in `.png` format.
        
        :param qr_code: The QR code image to save.
        :param path: The desired file path for saving the image.
        :return: `True` if QR code is saved successfully, `False` if otherwise.
        """
        
        try:
            qr_code.save(self._get_valid_name('png', path))
            return True
        except Exception as e:
            print(f'Failed To Export Image: {e}')
            self._logger.error(f'Failed To Export To Image: {e}')
            QMessageBox.critical(
                    self._instance,
                    'QR Code Export Error',
                    'Failed To Export QR Image'
            )
            return False
