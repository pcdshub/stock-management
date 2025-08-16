from stock_manager.model import Item
from stock_manager.utils import StockStatus

TEST_ITEM: Item = Item(
    'test_item',
    'test',
    'test',
    0, 0, 0,
    0, 0, 0,
    StockStatus.OUT_OF_STOCK
)
TEST_USERNAME = 'test_username'
TEST_NOTIFICATION = 'test notification'
