"""
Module containing application-wide constants.

Defines fixed values used throughout the SLAC-LCLS-Stock-Management
application to maintain consistency and simplify updates.
"""

from typing import Callable

TOTAL_EQUATION: Callable[[int, int], int] = \
	lambda b750_stock, b757_stock: \
		b750_stock + b757_stock

EXCESS_EQUATION: Callable[[int, int, int], int] = \
	lambda total, b750_minimum, b757_minimum: \
		total - (b750_minimum + b757_minimum)

SIDEBAR_BUTTON_SIZE = 14

PAGE_NAMES = [
	'Login',
	'View',
	'QR Scanner',
	'Add',
	'Edit',
	'Remove',
	'Export',
	'Finished',
]
