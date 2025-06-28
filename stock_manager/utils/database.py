import gspread
from gspread import Client
from oauth2client.service_account import ServiceAccountCredentials


class DBUtils:
	def __init__(self):
		credentials: ServiceAccountCredentials = ServiceAccountCredentials.from_json_keyfile_name(
				'assets/gs_credentials.json')
		self._client: Client = gspread.authorize(credentials)
	
	def get_all_data(self) -> list[dict[str, int | float | str]]:
		sheet = self._client.open('Stock Management Sheet').sheet1
		return sheet.get_all_records()
