"""
Data model for inventory items in the SLAC-LCLS Stock Management application.

Defines the Item dataclass, which tracks part numbers, quantities, and stock statistics.
"""

from dataclasses import dataclass
from typing import Generator, override


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
    :var stock_status: The current state of the stock item represented as a StockStatus enum.
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
    stock_status: str = ''
    
    def __post_init__(self):
        self._calc_stock_status()
    
    @override
    def __hash__(self) -> int:
        """Allows hashing of an Item object, allows Item objects to be put into sets"""
        return hash((value for value in self))
    
    @override
    def __eq__(self, other: object) -> bool:
        """Allows comparing of two objects by checking if all fields are equal in value."""
        if not isinstance(other, Item):
            return False
        return all(s == o for s, o, in zip(self, other))
    
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
        """Updates the `total`, `excess`, and `stock_status` fields based on current stock and minimums."""
        
        from stock_manager import excess_equation, total_equation
        
        total = total_equation(self.stock_b750, self.stock_b757)
        self.total = 0 if total <= 0 else total
        
        self.excess = excess_equation(total, self.minimum, self.minimum_sallie)
        
        self._calc_stock_status()
    
    def _calc_stock_status(self):
        from stock_manager.utils import StockStatus
        
        if self.excess > 1:
            self.stock_status = StockStatus.IN_STOCK.value
        elif self.excess == 0:
            self.stock_status = StockStatus.LOW_STOCK.value
        else:
            self.stock_status = StockStatus.OUT_OF_STOCK.value
