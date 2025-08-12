"""
Edit page controller for managing inventory item edits in the Stock Management Application.

This module provides the Edit class, which handles the UI and logic for editing inventory items,
including updating item details, validating user input, and saving changes to the database.
"""

from typing import override, TYPE_CHECKING

from PyQt5.QtCore import QModelIndex
from PyQt5.QtWidgets import QLineEdit, QMessageBox, QSpinBox, QTextEdit

import stock_manager
from stock_manager.model.item import Item
from .abstract import AbstractController

if TYPE_CHECKING:
    from stock_manager import App


class Edit(AbstractController):
    """
    Controller for the 'Edit' page of the stock management application.
    
    Handles editing already existing inventory items, validating input fields,
    and updating the database.
    """
    
    def __init__(self, app: 'App'):
        """
        Initialize the Edit page controller.
        
        :param app: Reference to the main application instance.
        """
        
        page = stock_manager.Pages.EDIT
        super().__init__(page.value.FILE_NAME, app)
        self.PAGE_NAME = page
        
        self._selected_item: Item | None = None
        self._total = self._excess = 0
        self._spinners: list[QSpinBox] = [
            self.b750_spinner,
            self.b757_spinner,
            self.min_750_spinner,
            self.min_757_spinner
        ]
        self._text_fields: list[QLineEdit | QTextEdit] = [self.manufacturer, self.desc]
        
        self.handle_connections()
    
    @override
    def handle_connections(self) -> None:
        import qtawesome as qta
        
        self.table.clicked.connect(self._on_cell_clicked)
        self.clear_btn.clicked.connect(self._clear_form)
        self.submit_btn.clicked.connect(self._submit_form)
        
        for spinner in self._spinners:
            spinner.valueChanged.connect(self._on_spinner_change)
        
        self.search_icon.setIcon(qta.icon('fa5s.search'))
        
        qta.set_defaults(color='white')
        
        self.clear_btn.setIcon(qta.icon('fa5s.backspace'))
        self.submit_btn.setIcon(qta.icon('fa5s.plus-square'))
    
    @staticmethod
    def _parse_field(text: str) -> int | str | None:
        """
        Convert text from a table cell into the appropriate type (int, str, or None).
        
        :param text: The text to parse.
        :return: The parsed value or `None` if no value exists.
        """
        
        if text in ['None', '']:
            return None
        elif text.isdigit():
            return int(text)
        return text
    
    def _on_cell_clicked(self, index: QModelIndex) -> None:
        """
        Populate the edit form fields with data from the selected item when a table row is clicked.
        
        :param index: The index of the clicked table cell as a `QModelIndex`.
        """
        
        row = index.row()
        
        self._selected_item = item = self.app.all_items[row]
        self._total = item.total
        self._excess = item.excess
        
        try:
            self.part_num.setText(str(item.part_num))
            self.manufacturer.setText(item.manufacturer)
            self.desc.setText(item.description)
            self.total_lbl.setText('Total: ' + str(self._total))
            self.excess_lbl.setText('Excess: ' + str(self._excess))
            self.b750_spinner.setValue(item.stock_b750 if item.stock_b750 is not None else 0)
            self.b757_spinner.setValue(item.stock_b757 if item.stock_b757 is not None else 0)
            self.min_750_spinner.setValue(item.minimum if item.minimum is not None else 0)
            self.min_757_spinner.setValue(item.minimum_sallie if item.minimum_sallie is not None else 0)
        except Exception as e:
            self.logger.error(f'Failed To Populate Fields: {e}')
            QMessageBox.critical(
                    self,
                    'Field Population Error',
                    'Failed To Populate Fields'
            )
    
    def _on_spinner_change(self, _) -> None:
        """
        Update the total and excess labels when any spinner value changes.
        
        :param _: The value emitted by the spinner (unused).
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
            self.logger.error(f'Spinner Change Error: {e}')
            QMessageBox.critical(
                    self,
                    'Spinner Change Error',
                    'Failed To Compute Spinner Data'
            )
    
    def _clear_form(self) -> None:
        """Clear all fields in the edit form and reset spinners and labels."""
        
        if not self._selected_item:
            return
        
        self.part_num.setText('Part Number...')
        
        text_field: QLineEdit | QTextEdit
        for text_field in self._text_fields:
            text_field.clear()
        for spinner in self._spinners:
            spinner.setValue(0)
        
        self._selected_item = None
        self._total = self._excess = 0
    
    def _submit_form(self) -> None:
        """
        Validate form data, update the selected item if it has changed,
        update the tables and database, and clear the form.
        """
        
        if not self._selected_item:
            QMessageBox.information(
                    self,
                    'No Item Selected',
                    'Please Select An Item Before Submitting The Form'
            )
            return
        
        field_vals: list[str | int] = [
            self.part_num.text(),
            self.manufacturer.text(),
            self.desc.toPlainText(),
            self._total,
            self.b750_spinner.value(),
            self.b757_spinner.value(),
            self.min_750_spinner.value(),
            self._excess,
            self.min_757_spinner.value()
        ]
        
        i: int
        field_val: str | int
        for i, field_val in enumerate(field_vals):
            if isinstance(field_val, str):
                field_vals[i] = self._parse_field(field_val)
        
        new_item = Item(*field_vals)
        
        if new_item == self._selected_item:
            QMessageBox.information(
                    self,
                    'Identical Items',
                    'Item Is Unchanged, Please Change A Field Before Submitting Form'
            )
            return
        
        response = QMessageBox.question(
                self,
                'Item Change Confirmation',
                f'Are You Sure You Want To Update Item {new_item.part_num}?',
                QMessageBox.Yes,
                QMessageBox.No
        )
        
        if response == QMessageBox.No:
            return
        
        for i, old_item in enumerate(self.app.all_items):
            if old_item.part_num == new_item.part_num:
                self.app.all_items[i] = new_item
                break
        
        self.logger.info(f'{self.app.user} Edited Database Item: {new_item.part_num}')
        self.app.update_tables()
        self.database.update_items_database(stock_manager.DatabaseUpdateType.EDIT, new_item)
        self._clear_form()
        
        if new_item.stock_b750 + new_item.stock_b757 <= 0:
            from datetime import datetime
            msg = ('Hello,\n\n'
                   
                   'This is an automatic notification detailing that '
                   'the following item has reached a total stock of 0:\n'
                   f'\tItem: {new_item.part_num}\n'
                   f'\tDescription: {new_item.description}\n'
                   f'\tExcess Count: {new_item.excess} ({new_item.stock_status.value})\n'
                   f'\tDate/Time: {datetime.now()}\n\n'
                   
                   'Please take any necessary action to reorder or restock.\n\n'
                   
                   'Best regards,\n'
                   'Stock Management System')
            
            self.database.add_notification(new_item.part_num)
            # stock_manager.send_email(msg, self)
