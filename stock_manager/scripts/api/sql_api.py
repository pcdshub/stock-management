import mysql.connector
from mysql.connector.abstracts import MySQLConnectionAbstract, MySQLCursorAbstract

db: MySQLConnectionAbstract = mysql.connector.connect(
        host='localhost',
        user='root',
        password='password',
        database='common_stock'
)

cursor: MySQLCursorAbstract = db.cursor()


# cursor.execute('select * from inventory_items')
# results: list = cursor.fetchall()

# print(results)
#
# for result in results:
#     print(result)


def init_database():
    def fetch_gs_rows() -> list[dict[str, int | float | str]]:
        from oauth2client.service_account import ServiceAccountCredentials
        from gspread import Client
        import gspread
        from gspread import Spreadsheet
        
        credentials = ServiceAccountCredentials.from_json_keyfile_name('../../../assets/gs_credentials.json')
        client: Client = gspread.authorize(credentials)
        client: Spreadsheet = client.open('Common Stock')
        sheet = client.worksheet('Parts')
        records: list[dict[str, int | float | str]] = sheet.get_all_records()
        return records
    
    sql = ('insert into inventory_items '
           '(part_num, manufacturer, description, '
           'total, stock_b750, stock_b757, minimum, '
           'excess, minimum_sallie, stock_status) '
           'values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);')
    
    def parse_values() -> list[list[int | str | None]]:
        vals: list[list[int | float | str]] = [
            [value for value in record.values()]
            for record in fetch_gs_rows()
        ]
        
        i: int
        items: list[int | float | str]
        for i, items in enumerate(vals):
            j: int
            val: int | float | str
            for j, val in enumerate(items):
                if not val or val == '':
                    match j:
                        case 1 | 2 | 9:
                            vals[i][j] = None
                        case 3 | 4 | 5 | 6 | 7 | 8:
                            vals[i][j] = 0
            print(f'Parsed: {items}')
        return vals
    
    cursor.executemany(sql, parse_values())
    db.commit()

# init_database()
