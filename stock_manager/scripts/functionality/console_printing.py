from prettytable import PrettyTable

table = PrettyTable()
table.field_names = [
    'Part #', 'Manufacturer', 'Description', 'Total',
    'B750', 'B757', 'Minimum', 'Excess', 'B750 Minimum',
    'Stock Status'
]
table.add_row(
        ['BK9000', 'Beckhoff',
            'Ethernet TCP/IP Bus Coupler for up to 64 Bus Terminals; Ethernet proto Beckhoff real-time Ethernet',
            '0', '-1', '1', '1', '-4', '3', 'Out Of Stock']
)
print(table)
