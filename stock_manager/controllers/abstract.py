"""
Abstract base classes for shared controller logic.

This module defines abstract classes used to enforce consistent structure
across controllers and scanner components in the SLAC-LCLS-Stock-Management
application. Each abstract class provides required methods, common functionality,
or reusable connection logic for concrete page controllers.
"""

import logging
from abc import ABC, ABCMeta, abstractmethod
from pathlib import Path
from typing import override, TYPE_CHECKING

from numpy import ndarray
from PyQt5.QtCore import pyqtSignal, QSortFilterProxyModel, Qt, QThread
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import QAbstractItemView, QFileDialog, QMessageBox, QPushButton, QWidget
from PyQt5.uic import loadUi

import stock_manager

if TYPE_CHECKING:
    from stock_manager import App


class CombinedMeta(type(QWidget), ABCMeta):
    """
    A metaclass combining PyQts QWidget metaclass and Python's ABCMeta.
    
    This enables the AbstractController to inherit from both PyQt widgets and Python abstract base classes,
    resolving metaclass conflicts that would otherwise occur with multiple inheritance.
    """
    pass


class AbstractController(ABC, QWidget, metaclass=CombinedMeta):
    """Abstract controller with common UI behavior for the application."""
    
    def __init__(self, file_name: str, app: 'App'):
        """
        Initialize the abstract controller, load its child's UI.
        
        :param file_name: The name of the .ui file (without extension) to load for this controller.
        :param app: Reference to the main application instance.
        """
        
        super(AbstractController, self).__init__()
        
        self.app = app
        self.logger = logging.getLogger()
        self.database = app.db
        self.PAGE_NAME: stock_manager.Pages | None = None
        
        try:
            ui_path = Path(__file__).resolve().parent.parent.parent / 'ui' / f'{file_name}.ui'
            loadUi(str(ui_path), self)
        except Exception as e:
            print(f'Failed To Load {file_name}.ui File: {e}')
            self.logger.error(f'Failed To Load {file_name}.ui File: {e}')
            QMessageBox.critical(
                    self,
                    f'{file_name}.ui Failure',
                    f'Failed To Load {file_name}.ui File'
            )
    
    @abstractmethod
    def handle_connections(self) -> None:
        """
        Define and connect all required signals and slots for the controller.
        
        Each subclass must implement this to set up its own UI event handlers
        and internal logic connections.
        """
        pass
    
    async def update_table(self) -> None:
        """
        Initializes the table widget with all inventory data from the database.
        Only works if child controller has a QTableView object called 'table'
        and a QLineEdit named 'search'.
        """
        
        if not hasattr(self, 'table'):
            QMessageBox.warning(
                    self,
                    'No Table Found',
                    'No Table Object Found In Controller, '
                    'Make Sure This Method Is Being Called In A Controller '
                    'That Has A Table Object Called "Table".'
            )
            return
        
        all_data = self.app.all_items
        source_model = QStandardItemModel()
        proxy_model = QSortFilterProxyModel()
        
        source_model.setHorizontalHeaderLabels(self.database.get_headers() + ['Stock Status'])
        for item in all_data:
            items = [QStandardItem(str(value)) for value in item]
            source_model.appendRow(items)
        
        proxy_model.setSourceModel(source_model)
        proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        proxy_model.setFilterKeyColumn(-1)
        
        self.table.setModel(proxy_model)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setDropIndicatorShown(False)
        self.table.setDragDropOverwriteMode(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setWordWrap(True)
        self.table.setCornerButtonEnabled(False)
        
        self.search.textChanged.connect(proxy_model.setFilterFixedString)
    
    def to_page(self) -> None:
        """Navigate to this controller's page in the stacked widget."""
        
        if hasattr(self, 'search'):
            self.search.clear()
        
        self.app.current_page = self.PAGE_NAME
        self.app.screens.setCurrentIndex(self.PAGE_NAME.value.PAGE_INDEX)
        
        username = f' - {self.app.user}' if self.app.user else ''
        
        try:
            self.app.setWindowTitle(
                    self.PAGE_NAME.value.PAGE_TITLE + ' | SLAC Inventory Management Application' + username
            )
        except Exception as e:
            print(f'Page Title Update Error: {e}')
            self.logger.warning(f'Error Updating Window Title With Current Page Title: {e}')
            self.setWindowTitle('SLAC Inventory Management Application' + username)


class AbstractScanner(AbstractController):
    """
    Abstract base class for scanner page controllers.
    
    Provides common functionality for pages that need to handle
    camera threads, QR code processing, and video display updates.
    """
    
    def __init__(self, file_name: str, app: 'App'):
        """
        Initialize the Abstract Scanner controller.
        Creates reference to `_CameraThread` as `self.camera_thread`.
        
        :param file_name: The name of the .ui file (without extension) to load for this controller.
        :param app: Reference to the main application instance.
        """
        
        super().__init__(file_name, app)
        self.camera_thread = self._CameraThread()
    
    @override
    def to_page(self) -> None:
        """Navigate to this scanner page and start the video feed."""
        
        try:
            self.start_video()
        except Exception as e:
            print(f'Failed To Start QR Scanner: {e}')
            self.logger.error(f'Failed To Start QR Scanner: {e}')
            QMessageBox.critical(
                    self,
                    'QR Scanner Error',
                    'Failed To Start QR Scanner'
            )
        finally:
            super().to_page()
    
    def start_video(self) -> None:
        """
        Start the camera thread and begin capturing video frames.

        Connects the thread’s signal to the frame processor.
        """
        
        if self.camera_thread.running:
            return
        
        try:
            self.camera_thread.frame_ready.connect(self.process_frame)
            self.camera_thread.start()
        except Exception as e:
            print(f'Error Starting Camera Thread: {e}')
            self.logger.error(f'Error Starting Camera Thread: {e}')
            QMessageBox.critical(
                    self,
                    'Camera Failure',
                    'Failed To Start Camera'
            )
    
    def stop_video(self) -> None:
        """
        Stop the camera thread and release resources.

        Ensures the camera thread is properly stopped when
        leaving the scanner page.
        """
        
        if self.camera_thread.running:
            self.camera_thread.stop()
            self.camera_thread.wait()
    
    def process_frame(self, frame: ndarray) -> None:
        """
        Process a single frame from the camera feed.
        
        Sends the frame to subclass's `check_for_qr()` to asynchronously decode and manage QR data.
        
        :param frame: A single image frame from the camera.
        """
        
        self.check_for_qr(frame)
        
        try:
            import cv2
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        except Exception as e:
            print(f'Failed To Convert Frame Color: {e}')
            self.logger.warning(f'Failed To Convert Frame Color: {e}')
            QMessageBox.warning(
                    self,
                    'Color Conversion Error',
                    'Failed To Convert Frame Color'
            )
        
        try:
            from PyQt5.QtGui import QImage, QPixmap
            
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            q_img = QImage(frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            self.video_lbl.setPixmap(QPixmap.fromImage(q_img))
        except Exception as e:
            print(f'Failed To Update Video Label: {e}')
            self.logger.error(f'Failed To Update Video Label: {e}')
            QMessageBox.critical(
                    self,
                    'Video Label Failure',
                    'Failed To Update Video Label'
            )
    
    @abstractmethod
    async def check_for_qr(self, frame: ndarray) -> None:
        """
        Asynchronously check the given video frame for a QR code.
        
        Subclasses must implement this method to process the frame,
        decode any QR codes found, and handle any related actions.
        
        :param frame: The video frame to analyze.
        """
        pass
    
    class _CameraThread(QThread):
        """
        Thread to handle continuous video capture from the camera.
        
        Runs in the background to read frames from the webcam and emit them
        via the `frame_ready` signal for processing elsewhere in the application.
        """
        
        frame_ready = pyqtSignal(object)
        
        def __init__(self, parent=None):
            """
            Initialize the camera thread.
            
            :param parent: Parent Qt object.
            """
            
            super().__init__(parent)
            self.running = False
            self._logger = logging.getLogger()
        
        @override
        def run(self) -> None:
            """
            Start the video capture loop.
            
            Continuously captures frames from the default webcam and emits
            each frame through the `frame_ready` signal.
            
            If an exception occurs, the user is offered the option to retry.
            """
            
            from cv2 import VideoCapture
            
            self.running = True
            cap = VideoCapture(0)
            if not cap.isOpened():
                self._logger.error('Could Not Access Camera')
                print('Could Not Access Camera')
                return
            
            while self.running:
                worked, frame = cap.read()
                if worked:
                    self.frame_ready.emit(frame)
                    continue
                
                print('Failed To Read Frame From Camera')
                self._logger.error('Failed To Read Frame From Camera')
            cap.release()
        
        def stop(self) -> None:
            """Stop the video capture loop."""
            self.running = False


class AbstractExporter(AbstractController):
    """
    Abstract base class for export controllers.
    
    Provides common functionality for pages that need to handle
    file exports, file dialogues, and file name generation.
    """
    
    def __init__(self, file_name: str, app: 'App'):
        """
        Initialize the AbstractExporter controller.
        Creates reference to the `../../../export` folder as `self.path`.
        
        :param file_name: The name of the .ui file (without extension) to load for this controller.
        :param app: Reference to the main application instance.
        """
        
        super().__init__(file_name, app)
        self.path = str(Path(__file__).resolve().parent.parent.parent / 'exports')
    
    def get_directory(self, button: QPushButton = None) -> None:
        """
        Open a dialog to select the export directory and update the UI.
        
        If an exception occurs during selection, the user is offered the option to retry.
        
        :param button: sets the text of `button` to the last 6 characters of the user chosen path.
        """
        
        try:
            response = QFileDialog.getExistingDirectory(
                    self, 'Select A Folder',
                    str(Path(__file__).resolve().parent.parent.parent / 'exports')
            )
            response = str(response)
            self.path = response
            if button:
                button.setText(f'...{response.split("/")[-1]}' if len(response) > 6 else response)
        except Exception as e:
            print(f'Directory Selection Failure: {e}')
            self.logger.error(f'Directory Selection Failure: {e}')
            response = QMessageBox.critical(
                    self,
                    'Directory Selection Failure',
                    'Failed To Select Directory',
                    QMessageBox.Ok,
                    QMessageBox.Retry
            )
            
            if response == QMessageBox.Retry:
                self.get_directory()
    
    @abstractmethod
    def export(self) -> None:
        """
        Export data to an external format or destination.
        
        Subclasses must implement this to define the logic
        for exporting application data. The specifics of what
        data is exported, where it is sent, and the export
        format must be handled by the implementing subclass.
        """
        pass
