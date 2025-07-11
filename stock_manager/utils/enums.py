from dataclasses import dataclass
from enum import Enum


class PageNames(Enum):
	@dataclass
	class PageDetails:
		TITLE: str
		FILE_NAME: str
	
	LOGIN = PageDetails('Login', 'login')
	VIEW = 'View'
	SCAN = 'QR Scanner'
	ADD = 'Add'
	EDIT = 'Edit'
	REMOVE = 'Remove'
	EXPORT = 'Export'
	FINISHED = 'Finished'


class ExportTypes(Enum):
	PDF = 'pdf'
	CSV = 'csv'
	TSV = 'tsv'
	PSV = 'psv'


class StockStatus(Enum):
	IN_STOCK = 'In Stock'
	LOW_STOCK = 'Low Stock'
	OUT_OF_STOCK = 'Out Of Stock'
