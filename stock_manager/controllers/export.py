"""Export page controller for exporting inventory data in the Stock Management Application."""

from typing import override, TYPE_CHECKING

import numpy
from PyQt5.QtCore import QModelIndex
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QMessageBox
from qrcode.image.base import BaseImage

import stock_manager
from .abstract import AbstractExporter

if TYPE_CHECKING:
    from stock_manager import App


class Export(AbstractExporter):
    """
    Controller for the 'Edit' page of the stock management application.
    
    Handles which type of file to export as and sends
    the correct signal to `export_utils.py` to be exported.
    """
    
    def __init__(self, app: 'App'):
        """
        Initialize the Export controller.
        
        :param app: Reference to the main application instance.
        """
        
        page = stock_manager.Pages.EXPORT
        super().__init__(page.value.FILE_NAME, app)
        self.PAGE_NAME = page
        self.location_btn.setText('.../' + self.path.split('\\')[-1])
        self.handle_connections()
    
    @override
    def handle_connections(self) -> None:
        self.back_btn.clicked.connect(lambda: self.app.view.to_page())  # keep as lambda because of connect()
        self.location_btn.clicked.connect(lambda: self.get_directory(self.location_btn))
        self.export_btn.clicked.connect(self.export)
        
        def handle_icons():
            import qtawesome as qta
            
            qta.set_defaults(color='black')
            self.file_icon.setIcon(qta.icon('fa5s.file-alt'))
            self.folder_icon.setIcon(qta.icon('fa5s.folder-open'))
            
            qta.set_defaults(color='white')
            self.back_btn.setIcon(qta.icon('fa5s.arrow-left'))
            self.location_btn.setIcon(qta.icon('fa6s.folder-tree'))
            self.export_btn.setIcon(qta.icon('fa5s.download'))
        
        handle_icons()
    
    @override
    def export(self) -> None:
        try:
            from stock_manager import ExportTypes
            
            match self.export_combo.currentText().lower():
                case ExportTypes.PDF.value:
                    self.app.export_utils.pdf_export()
                case ExportTypes.CSV.value | ExportTypes.TSV.value | ExportTypes.PSV.value as export_type:
                    self.app.export_utils.sv_export(export_type, self.path)
                case 'Select':
                    QMessageBox.information(
                            self,
                            'Please Choose File Type',
                            'Please Select A File Type Before Exporting'
                    )
                case _ as unknown:
                    print(f'Unknown Export Type: "{unknown}"')
                    QMessageBox.warning(
                            self,
                            'Selection Error',
                            'Please Select A Valid File Type To Export'
                    )
        except Exception as e:
            print(f'Export Failed: {e}')
            self.logger.error(f'Export Failed: {e}')
            response = QMessageBox.critical(
                    self,
                    'Export Failure',
                    'Failed To Export Data To File',
                    QMessageBox.Ok,
                    QMessageBox.Retry
            )
            
            if response == QMessageBox.Retry:
                self.export()


class QRGenerate(AbstractExporter):
    """
    Controller for the `QR Generate` page of the stock management application.
    
    Handles generating and exporting QR codes associated with inventory items.
    """
    
    def __init__(self, app: 'App'):
        """
        Initialize the QRGenerate controller.
        
        :param app: Reference to the main application instance.
        """
        
        page = stock_manager.Pages.GENERATE
        super().__init__(page.value.FILE_NAME, app)
        self.PAGE_NAME = page
        self._selected_qr: BaseImage | None = None
        self.location_btn.setText('.../' + self.path.split('\\')[-1])
        self.handle_connections()
    
    @override
    def handle_connections(self) -> None:
        import qtawesome as qta
        
        self.table.clicked.connect(self._on_cell_clicked)
        self.location_btn.clicked.connect(lambda: self.get_directory(self.location_btn))
        self.save_btn.clicked.connect(self.export)
        
        self.search_icon.setIcon(qta.icon('fa5s.search'))
        self.location_btn.setIcon(qta.icon('fa6s.folder-tree'))
        self.save_btn.setIcon(qta.icon('fa5s.download'))
    
    @override
    def export(self):
        if not self._selected_qr:
            QMessageBox.warning(
                    self,
                    'Please Choose Item',
                    'Please Choose An Item From The Table Before Exporting QR Code.'
            )
            return
        
        try:
            self.app.export_utils.save_code(self._selected_qr, self.path)
        except Exception as e:
            print(f'Failed To Save QR Code To File: {e}')
            self.logger.error(f'Failed To Save QR Code To File: {e}')
            QMessageBox.critical(
                    self,
                    'QR Code Download Failure',
                    'Failed To Download QR Code'
            )
    
    def _on_cell_clicked(self, index: QModelIndex) -> None:
        """
        Generates and displays a QR code corresponding
        to the selected table item's part number.
        
        :param index: The index of the clicked table cell as a `QModelIndex`.
        """
        
        row = index.row()
        item = self.app.all_items[row]
        
        try:
            self._selected_qr = self.app.export_utils.create_code(item.part_num)
        except Exception as e:
            print(f'Failed To Get Selected Item QR Code: {e}')
            self.logger.error(f'Failed To Get Selected Item QR Code: {e}')
            QMessageBox.critical(
                    self,
                    'Item QR Code Creation Failure',
                    'Failed To Create Item QR Code.'
            )
            return
        
        try:
            pil_image = self._selected_qr.get_image().convert("RGB")
            frame = numpy.asarray(pil_image)
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            q_img = QImage(frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            self.qr_lbl.setPixmap(QPixmap.fromImage(q_img))
        except Exception as e:
            print(f'Failed To Update QR Label: {e}')
            self.logger.error(f'Failed To Update QR Label: {e}')
            QMessageBox.critical(
                    self,
                    'QR Label Failure',
                    'Failed To Update QR Label'
            )
