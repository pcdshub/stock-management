import gspread
from gspread import Client, Spreadsheet, Worksheet
from oauth2client.service_account import ServiceAccountCredentials


def main():
    scope: list[str] = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name('../../../assets/gs_credentials.json')
    client: Client = gspread.authorize(credentials)
    # client.del_spreadsheet('Stock Management Sheet')
    client: Spreadsheet = client.open('Common Stock')
    sheet = client.worksheet('Users')
    read_sheet(sheet)
    # create_sheet(client)
    # update_sheet(sheet)


def update_sheet(sheet: Worksheet):
    # sheet.update_cell(1, 1, 'Another Updated Value')
    sheet.update(range_name='A2:D2', values=[[1, 2, 3, 4]])
    
    # sheet.update(range_name='B1:C2', values=[['New Value 1', 'New Value 2'], ['New Value 3', 'New Value 4']])
    # sheet.batch_update(
    #         [{
    #             'range': 'D1',
    #             'values': [['Batch Updated Value']]
    #         }, {
    #             'range': 'E1:F2',
    #             'values': [['Batch', 'Update'], ['Example', 'Data']]
    #         }]
    # )


def read_sheet(sheet: Worksheet):
    print(sheet.get_all_records())
    # print(sheet.row_values(1))
    # print(sheet.cell(1, 1).value)


def create_sheet(client):
    sheet = client.create('Stock Management Sheet')
    sheet.share('lkingerslev@gmail.com', 'user', 'writer')


if __name__ == '__main__':
    main()
