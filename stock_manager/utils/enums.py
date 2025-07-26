from dataclasses import dataclass
from enum import auto, Enum


class Pages(Enum):
    @dataclass
    class _PageDetails:
        PAGE_TITLE: str
        FILE_NAME: str
        PAGE_INDEX: int
    
    VIEW = _PageDetails('View', 'view', 0)
    SCAN = _PageDetails('QR Scanner', 'scanner', 1)
    ADD = _PageDetails('Add', 'add', 2)
    EDIT = _PageDetails('Edit', 'edit', 3)
    REMOVE = _PageDetails('Remove', 'remove', 4)
    GENERATE = _PageDetails('QR Generate', 'qr_generate', 5)
    LOGIN = _PageDetails('Login', 'login', 6)
    EXPORT = _PageDetails('Export', 'export', 7)
    FINISHED = _PageDetails('Finished', 'finish', 8)


class ExportTypes(Enum):
    PDF = 'pdf'
    CSV = 'csv'
    TSV = 'tsv'
    PSV = 'psv'


class StockStatus(Enum):
    IN_STOCK = 'In Stock'
    LOW_STOCK = 'Low Stock'
    OUT_OF_STOCK = 'Out Of Stock'


class DatabaseUpdateType(Enum):
    ADD = auto()
    EDIT = auto()
    REMOVE = auto()
