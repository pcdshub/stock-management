"""
Data model for inventory items
in the Stock Management Application.

Defines the Item dataclass, which tracks
part numbers, quantities, and stock statistics.
"""

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Generator, override

if TYPE_CHECKING:
    from stock_manager.utils import StockStatus


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
    :var stock_status: The current state of the stock item
    represented as a StockStatus enum.
    """

    part_num: str
    manufacturer: str | None
    description: str | None
    total: int | None
    stock_b750: int | None
    stock_b757: int | None
    minimum: int | None
    excess: int | None
    minimum_sallie: int | None
    stock_status: 'StockStatus' = None

    def __post_init__(self):
        self._calc_stock_status()

    @override
    def __hash__(self) -> int:
        """
        Allows hashing of an Item object, and
        allows Item objects to be put into sets

        :return: hashed value of all values in `Item` object.
        """
        return hash((value for value in self))

    @override
    def __eq__(self, other: object) -> bool:
        """
        Allows comparing of two objects by checking
        if all fields are equal in value.

        Comparing `''` and `None` returns `True`.

        :param other: object to compare values to.
        :return: `True` if objects are equal in all values,
        `False` if otherwise or type mismatch.
        """
        if not isinstance(other, Item):
            return False

        def soft_equal(a, b):
            empty = ('', None)
            if a in empty and b in empty:
                return True
            return str(a).strip() == str(b).strip()

        return all(soft_equal(s, o) for s, o, in zip(self, other))

    def __len__(self) -> int:
        """
        Allows counting the length of the item's total number of field values.

        :return: number of values in `Item` object.
        """
        return len(self.__dict__)

    def __getitem__(self, idx: int) -> str | int | Enum | None:
        """
        Allows indexed access to the item's field values.

        :param idx: index at which to check value.
        :return: the field's value.
        """
        return [
            value
            if not isinstance(value, Enum)
            else value.value
            for value in self.__dict__.values()
        ][idx]

    def __setitem__(self, idx: str, value: str | int | Enum | None) -> None:
        """
        Allows the setting of `Item` objects as `obj[str] = val`.

        :param idx: index at which to change the value.
        :param value: a new value to change to at the specified index.
        """

        if hasattr(self, idx):
            setattr(self, idx, value)
            self.update_stats()
            return
        raise NameError(f'Unknown Field: {idx}')

    def __iter__(self) -> Generator[str | int | Enum | None]:
        """
        Allows iteration access to the item's field values.

        :return: A `Generator` of `Item` values to iterate through.
        """
        return (
            value
            if not isinstance(value, Enum)
            else value.value
            for value in self.__dict__.values()
        )

    def update_stats(self) -> None:
        """
        Updates the `total`, `excess`, and `stock_status`
        fields based on current stock and minimums.
        """

        from stock_manager.utils import excess_equation, total_equation

        total = total_equation(self.stock_b750, self.stock_b757)
        self.total = 0 if total <= 0 else total

        self.excess = excess_equation(total, self.minimum, self.minimum_sallie)

        self._calc_stock_status()

    def _calc_stock_status(self) -> None:
        """
        Sets the value of `self.stock_status` to the
        string value of a `StockStatus` enum based on `self.excess`.
        """

        from stock_manager.utils import StockStatus

        if self.excess is None or self.total is None:
            return

        if self.excess > 1:
            self.stock_status = StockStatus.IN_STOCK
        elif self.total <= 0:
            self.stock_status = StockStatus.OUT_OF_STOCK
        elif self.excess <= 1:
            self.stock_status = StockStatus.LOW_STOCK
