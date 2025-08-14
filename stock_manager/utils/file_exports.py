"""
Export utilities for Stock Management Application.

Provides ExportUtils for managing different types of
data exportation for various application features.
"""

import logging
import os
from typing import TYPE_CHECKING, Literal, Union

import qrcode
from PyQt5.QtWidgets import QMessageBox
from qrcode.image.base import BaseImage

if TYPE_CHECKING:
    from stock_manager.model import Item


class ExportUtils:
    def __init__(self):
        """
        Initializes the ExportUtils class.
        """

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

    def pdf_export(self) -> None:
        """Asynchronously exports current data to PDF format."""

        pass  # TODO: add pdf generation

    def sv_export(
        self,
        export_type: Literal['csv', 'tsv', 'psv'],
        path: str,
        all_items: list['Item']
    ) -> bool:
        """
        Asynchronously exports current data to a
        delimited text file (CSV, TSV, PSV).

        :param export_type: The file extension as the
        value (str) of an ExportType enum.
        :param path: The directory to create file in.
        :param all_items: All items from database to be exported
        :return: `True` if file is created and written to successfully,
        `False` otherwise
        """

        delimiter = {
            'csv': ',',
            'tsv': '\t',
            'psv': '|'
        }.get(export_type)

        if not delimiter:
            self._logger.warning(
                f'Cannot Call sv_export() With Type: "{export_type}"'
            )
            return False

        try:
            with open(self._get_valid_name(export_type, path), 'x') as f:
                for i, item in enumerate(all_items):
                    line = ''
                    for var in item:
                        line += (str(var) if var else '') + delimiter
                    f.write(line[:-1] + '\n')
            return True
        except FileExistsError as e:
            self._logger.error(f'File Already Exists Error: {e}')
            QMessageBox.critical(
                None,
                'File Exists Error',
                'That File Already Exists, Try Changing File Types'
            )
            return False
        except Exception as e:
            export_type = export_type.upper()
            self._logger.error(f'Failed To Export Data To {export_type}: {e}')
            QMessageBox.critical(
                None,
                f'{export_type} Export Error',
                f'Failed To Export Data To {export_type}, '
                'Try Changing File Types'
            )
            return False

    def create_code(self, part_num: str) -> Union[BaseImage, None]:
        """
        This method creates a QR code using the input `part_num`
        string and returns it as a `BaseImage` object.

        :param part_num: The string to encode in the QR code.
        :return: The generated QR code image.
        """

        try:
            qr = qrcode.QRCode()
            qr.add_data(part_num)
            qr.make()
            image = qr.make_image()
            self._logger.info(
                f'Successfully Generated QR Code For: {part_num}'
            )
            return image
        except Exception as e:
            self._logger.error(
                f'Failed To Convert {part_num} To QR Image: {e}'
            )
            QMessageBox.critical(
                None,
                'QR Code Conversion Error',
                f'Failed To Convert {part_num} To QR Image'
            )
            return None

    def save_code(self, qr_code: BaseImage, path: str) -> bool:
        """
        Save a QR code image to a specified file path in `.png` format.

        :param qr_code: The QR code image to save.
        :param path: The desired file path for saving the image.
        :return: `True` if QR code is saved successfully, `False` otherwise.
        """

        try:
            qr_code.save(self._get_valid_name('png', path))
            self._logger.info(f'Successfully Saved QR Code At: {path}')
            return True
        except Exception as e:
            self._logger.error(f'Failed To Export Image: {e}')
            QMessageBox.critical(
                None,
                'QR Code Export Error',
                'Failed To Export QR Image'
            )
            return False
