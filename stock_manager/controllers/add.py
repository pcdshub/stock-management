"""
Add page controller for adding inventory items in the Stock Management Application.

Provides logic for the user to add new stock items, including form validation,
computation of totals and excess, and updating the database.
"""

from typing import override, TYPE_CHECKING

from PyQt5.QtWidgets import QLineEdit, QMessageBox, QSpinBox, QTextEdit

import stock_manager
from .abstract import AbstractController

if TYPE_CHECKING:
    from stock_manager import App


class Add(AbstractController):
    """
    Controller for the 'Add' page of the stock management application.
    
    Handles user input for creating new stock items, validating input fields,
    computing totals and excess, and updating the database.
    """
    
    def __init__(self, app: 'App'):
        """
        Initialize the Add page controller.
        
        :param app: Reference to the main application instance.
        """
        
        page = stock_manager.Pages.ADD
        super().__init__(page.value.FILE_NAME, app)
        self.PAGE_NAME = page
        self._total = self._excess = 0
        self._spinners: set[QSpinBox] = {
            self.b750_spinner,
            self.b757_spinner,
            self.min_750_spinner,
            self.min_757_spinner
        }
        self._text_fields: set[QLineEdit | QTextEdit] = {
            self.part_num,
            self.manufacturer,
            self.desc
        }
        
        self.handle_connections()
    
    @override
    def handle_connections(self) -> None:
        import qtawesome as qta
        
        self.clear_btn.clicked.connect(self._clear_form)
        self.submit_btn.clicked.connect(self._submit_form)
        
        for spinner in self._spinners:
            spinner.valueChanged.connect(self._on_spinner_change)
        
        qta.set_defaults(color='white')
        
        self.clear_btn.setIcon(qta.icon('fa5s.backspace'))
        self.submit_btn.setIcon(qta.icon('fa5s.plus-square'))
    
    def _on_spinner_change(self, _) -> None:
        """
        Handle changes in spinner values.
        
        :param _: The spinner event parameter (unused).
        """
        
        try:
            self._total = stock_manager.total_equation(
                    self.b750_spinner.value(),
                    self.b757_spinner.value()
            )
            self._excess = stock_manager.excess_equation(
                    self._total,
                    self.min_750_spinner.value(),
                    self.min_757_spinner.value()
            )
            
            self.total_lbl.setText('Total: ' + str(self._total))
            self.excess_lbl.setText('Excess: ' + str(self._excess))
        except Exception as e:
            print('[x] Spinner Change Error:', e)
            self.logger.error(f'Spinner Change Error: {e}')
            QMessageBox.critical(
                    self,
                    'Spinner Change Error',
                    'Failed To Compute Spinner Data'
            )
    
    def _clear_form(self) -> None:
        """
        Clear all text fields and reset all spinner values.
        
        Resets the form to its initial state for new input.
        """
        
        text_field: QLineEdit | QTextEdit
        for text_field in self._text_fields:
            text_field.clear()
        for spinner in self._spinners:
            spinner.setValue(0)
    
    def _submit_form(self) -> bool:
        """
        Validate the form and submit a new stock item.
        
        Checks that all required text fields are filled and at least one
        spinner has a value. Adds the item to the database, updates tables,
        and clears the form.
        
        :return: `True` if form is chosen to be submitted or not submitted
        successfully, `False` if any issues occur.
        """
        
        def empty_fields_check() -> bool:
            """
            Checks form for empty QLineEdits and QTextEdits.
            Checks for at least one filled out QSpinBox.
            
            :return: True if any fields are empty or False if all are filled
            """
            
            empty_line_edits = {
                field.objectName() for field in self._text_fields
                if isinstance(field, QLineEdit) and not field.text().strip()
            }
            empty_text_edits = {
                field.objectName() for field in self._text_fields
                if isinstance(field, QTextEdit) and not field.toPlainText().strip()
            }
            valued_spinners = {
                spinner.objectName() for spinner in self._spinners
                if spinner.value()
            }
            
            return True if any([empty_line_edits, empty_text_edits]) or not any(valued_spinners) else False
        
        if empty_fields_check():
            QMessageBox.information(
                    self,
                    'Empty Fields',
                    'Please Fill Out All Text Fields And '
                    'At Least One Spinner Before Submitting Form'
            )
            return False
        
        new_item = stock_manager.Item(
                self.part_num.text(),
                self.manufacturer.text(),
                self.desc.toPlainText(),
                self._total,
                self.b750_spinner.value(),
                self.b757_spinner.value(),
                self.min_750_spinner.value(),
                self._excess,
                self.min_757_spinner.value()
        )
        
        if any([item for item in self.app.all_items if item.part_num == self.part_num.text().strip()]):
            QMessageBox.warning(
                    self,
                    'Item Already Exists Error',
                    f'"{new_item.part_num}" Already Exists In The Database, '
                    'Please Make A New Item That Does Not Already Exist.'
            )
            return False
        
        response = QMessageBox.information(
                self,
                'Item Creation Confirmation',
                f'Are You Sure You Want To Add {new_item.part_num} '
                'To The Database?\n\nThis Item Can Be Removed Later.',
                QMessageBox.Yes,
                QMessageBox.No
        )
        
        if response == QMessageBox.No:
            return True
        
        self.app.all_items.append(new_item)
        self.logger.info(f'{self.app.user} Added Item To Database: {new_item.part_num}')
        self.app.update_tables()
        self.database.update_database(stock_manager.DatabaseUpdateType.ADD, new_item)
        self._clear_form()
        
        if new_item.stock_b750 + new_item.stock_b757 <= 0:
            from datetime import datetime
            msg = ('Hello,\n\n'
                   
                   'This is an automatic notification detailing that '
                   'the following item has been created with a total stock of 0:\n'
                   f'\tItem: {new_item.part_num}\n'
                   f'\tDescription: {new_item.description}\n'
                   f'\tExcess Count: {new_item.excess} ({new_item.stock_status})\n'
                   f'\tDate/Time: {datetime.now()}\n\n'
                   
                   'Please take any necessary action to order or restock.\n\n'
                   
                   'Best regards,\n'
                   'Stock Management System')
            
            self.database.add_notification(new_item.part_num)
            # stock_manager.send_email(msg, self)
        
        self.app.finish.set_text(f'Successfully Added {new_item.part_num} To The Database')
        self.app.finish.to_page()
        
        return True
