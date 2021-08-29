from oauth2client.service_account import ServiceAccountCredentials
import gspread


class Sheets():
    def __init__(self):
        self.scope = ['https://www.googleapis.com/auth' + x for x in [
            '/spreadsheets',
            '/drive.file',
            '/drive']]
        self.creds = ServiceAccountCredentials.from_json_keyfile_name('SheetsAPI-KEY.json', self.scope)
        self.client = gspread.authorize(self.creds)

    def write_row(self, text: str):
        sheet = self.client.open('WbParser').sheet1
        sheet.update_cell(1, 1, 'FUCK')
        sheet.update_cell(1, 2, 'YEAH,')
        sheet.clear()

    def clear_sheets(self):
        for sheet in self.client.open('WbParser').worksheets()[1:]:
            self.client.open('WbParser').del_worksheet(sheet)

    def write_matrix(self, matrix, sheetName):
        sheet = self.client.open('WbParser').add_worksheet(sheetName,
                                                           rows=len(max(matrix, key=lambda x: len(x))) + 2,
                                                           cols=len(max(matrix, key=lambda x: len(x))) + 2)
        sheet.clear()
        sheet.update('', [['TIME', 'BLOCK', 'CURRENCY RATE']] + [list(x) for x in matrix])