import os
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

class GoogleSheetsLogger:
    def __init__(self, spreadsheet_id: str):
        self.spreadsheet_id = spreadsheet_id
        self.creds = Credentials.from_service_account_file('config/google_creds.json')
        self.service = build('sheets', 'v4', credentials=self.creds)

    def append_row(self, data: list):
        sheet = self.service.spreadsheets()
        body = {'values': [data]}
        sheet.values().append(
            spreadsheetId=self.spreadsheet_id,
            range="Sheet1!A1",
            valueInputOption="USER_ENTERED",
            body=body
        ).execute()
