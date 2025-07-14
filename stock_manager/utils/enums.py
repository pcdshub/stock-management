from dataclasses import dataclass
from enum import auto, Enum


class Pages(Enum):
	@dataclass
	class _PageDetails:
		TITLE: str
		FILE_NAME: str
		PAGE_INDEX: int
	# TODO: Possibly add admin boolean
	#  to only display certain pages
	
	LOGIN = _PageDetails('Login', 'login', 0)
	VIEW = _PageDetails('View', 'view', 1)
	SCAN = _PageDetails('QR Scanner', 'scanner', 2)
	ADD = _PageDetails('Add', 'add', 3)
	EDIT = _PageDetails('Edit', 'edit', 4)
	REMOVE = _PageDetails('Remove', 'remove', 5)
	EXPORT = _PageDetails('Export', 'export', 6)
	FINISHED = _PageDetails('Finished', 'finish', 7)


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
