# src/yt_analyzer/data/spreadsheet/client.py

import gspread
from google.oauth2.service_account import Credentials


class SpreadsheetClient:
  SCOPES = (
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive.readonly"
  )

  def __init__(self, spreadsheet_id: str, credentials_file: str) -> None:
    credentials = Credentials.from_service_account_file(
      credentials_file,
      scopes=self.SCOPES
    )

    client = gspread.authorize(
      credentials
    )

    self._spreadsheet = client.open_by_key(
      spreadsheet_id
    )

  def records(self, worksheet_name: str) -> list[dict[str, object]]:
    worksheet = self._spreadsheet.worksheet(
      worksheet_name
    )

    return worksheet.get_all_records()
