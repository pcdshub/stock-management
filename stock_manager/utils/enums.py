from dataclasses import dataclass
from enum import auto, Enum

import stock_manager


class Pages(Enum):
    @dataclass
    class _PageDetails:
        PAGE_TITLE: str
        FILE_NAME: str
        PAGE_INDEX: int
        CONTROLLER: type(stock_manager.AbstractController)
    
    # TODO: Possibly add admin boolean
    #  to only display certain pages
    
    LOGIN = _PageDetails('Login', 'login', 0, stock_manager.Login)
    VIEW = _PageDetails('View', 'view', 1, stock_manager.View)
    SCAN = _PageDetails('QR Scanner', 'scanner', 2, stock_manager.ItemScanner)
    ADD = _PageDetails('Add', 'add', 3, stock_manager.Add)
    EDIT = _PageDetails('Edit', 'edit', 4, stock_manager.Edit)
    REMOVE = _PageDetails('Remove', 'remove', 5, stock_manager.Remove)
    GENERATE = _PageDetails('QR Generate', 'qr_generate', 6, stock_manager.QRGenerate)
    EXPORT = _PageDetails('Export', 'export', 7, stock_manager.Export)
    FINISHED = _PageDetails('Finished', 'finish', 8, stock_manager.Finish)


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
