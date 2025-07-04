"""
Data model for inventory items in the SLAC-LCLS Stock Management application.

Defines the Item dataclass, which tracks part numbers, quantities, and stock statistics.
"""

from dataclasses import dataclass
from typing import Generator

from stock_manager.utils import EXCESS_EQUATION, TOTAL_EQUATION


@dataclass
class Item:
	"""
	Represents a single inventory item and its stock information.
	
	:var part_num: The part number of the item.
	:var manufacturer: The manufacturer of the item.
	:var description: Description of the item.
	:var total: Total number of this item in stock.
	:var stock_b750: Stock count at location B750.
	:var stock_b757: Stock count at location B757.
	:var minimum: Minimum required stock for B750.
	:var excess: The amount of stock above minimum levels.
	:var minimum_sallie: Minimum required stock for B757.
	"""
	
	part_num: str | None
	manufacturer: str | None
	description: str | None
	total: int | None
	stock_b750: int | None
	stock_b757: int | None
	minimum: int | None
	excess: int | None
	minimum_sallie: int | None
	
	def __len__(self) -> int:
		"""Allows counting the length of the item's total number of field values."""
		return len(self.__dict__)
	
	def __getitem__(self, idx: int) -> str | int | None:
		"""Allows indexed access to the item's field values."""
		return [value for value in self.__dict__.values()][idx]
	
	def __iter__(self) -> Generator[str | int | None]:
		"""Allows iteration access to the item's field values."""
		return (value for value in self.__dict__.values())
	
	def update_stats(self) -> None:
		"""Updates the 'total' and 'excess' fields based on current stock and minimums."""
		
		total = TOTAL_EQUATION(self.stock_b750, self.stock_b757)
		self.total = 0 if total <= 0 else total
		
		excess = EXCESS_EQUATION(total, self.minimum, self.minimum_sallie)
		self.excess = 0 if excess <= 0 else excess
