from typing import Callable

TOTAL_EQUATION: Callable[[int, int], int] = lambda b750_stock, b757_stock: \
	b750_stock + b757_stock

EXCESS_EQUATION: Callable[[int, int, int], int] = lambda total, b750_minimum, b757_minimum: \
	total - (b750_minimum + b757_minimum)
