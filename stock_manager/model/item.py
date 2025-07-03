from dataclasses import dataclass
from typing import Generator


@dataclass
class Item:
	part_num: str
	manufacturer: str
	description: str
	total: int
	stock_b750: int
	stock_b757: int
	minimum: int
	excess: int
	minimum_sallie: int
	
	def __len__(self) -> int:
		return len(self.__dict__)
	
	def __getitem__(self, idx: int) -> str | int:
		return [value for value in self.__dict__.values()][idx]
	
	def __iter__(self) -> Generator[str | int | None]:
		return (value for value in self.__dict__.values())
	
	def update_stats(self) -> None:
		total = self.stock_b750 + self.stock_b757
		self.total = 0 if total <= 0 else total
			
		excess = total - (self.minimum + self.minimum_sallie)
		self.excess = 0 if excess <= 0 else excess
