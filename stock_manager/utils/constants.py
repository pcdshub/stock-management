"""
Module containing application-wide constants.

Defines fixed values used throughout the SLAC-LCLS-Stock-Management
application to maintain consistency and simplify updates.
"""


def total_equation(b750_stock: int, b757_stock: int) -> int:
    """
    Calculates the total stock from both locations.

    :param b750_stock: the stock at B750
    :param b757_stock: the stock at B757
    :return: the sum of the two values
    """

    return int(b750_stock) + int(b757_stock)


def excess_equation(total: int, b750_minimum: int, b757_minimum: int) -> int:
    """
    Calculates the excess of total stock based on
    the total stock and the minimums for each location.

    :param total: the total stock
    :param b750_minimum: the minimum stock at B750
    :param b757_minimum: the minimum stock at B757
    :return: the calculated total excess of the stock item
    """

    return total - (b750_minimum + b757_minimum)


SIDEBAR_BUTTON_SIZE = 14
GS_FILE_NAME = 'ECS Common Stock Inventory'
KEEP_HEADERS = [
    'Part #',
    'Manufacturer',
    'Description',
    'Total',
    'B750',
    'B757',
    'Minimum',
    'Excess',
    'Min Sallies',
    'Stock Status'
]
