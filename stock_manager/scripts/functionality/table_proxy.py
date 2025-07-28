import sys

from PyQt5.QtCore import QSortFilterProxyModel, Qt
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import (QApplication, QLineEdit, QTableView, QVBoxLayout, QWidget)


class TableExample(QWidget):
    def __init__(self):
        super().__init__()
        
        layout = QVBoxLayout(self)
        
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText('Filter table...')
        layout.addWidget(self.filter_input)
        
        self.table_view = QTableView()
        layout.addWidget(self.table_view)
        
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(['Name', 'Age', 'Country'])
        
        data = [
            ['Alice', '30', 'USA'],
            ['Bob', '25', 'Canada'],
            ['Charlie', '35', 'UK'],
            ['David', '40', 'USA'],
        ]
        
        for row in data:
            items = [QStandardItem(field) for field in row]
            self.model.appendRow(items)
        
        self.proxy = QSortFilterProxyModel()
        self.proxy.setSourceModel(self.model)
        self.proxy.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.proxy.setFilterKeyColumn(-1)  # Filter all columns
        
        self.filter_input.textChanged.connect(self.proxy.setFilterFixedString)
        
        self.table_view.setModel(self.proxy)
        self.table_view.setSortingEnabled(True)
        self.table_view.sortByColumn(0, Qt.AscendingOrder)
        
        self.setWindowTitle('QTableView Example')
        self.resize(500, 300)


app = QApplication([])
window = TableExample()
window.show()
sys.exit(app.exec_())
