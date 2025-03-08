from google.oauth2 import service_account
from googleapiclient.discovery import build

from dynaconf import Dynaconf


def number_to_column(n):
    """Returns an Excel-like column name by its order number (e.g. 1 -> A, 27 -> AA)"""

    result = ""
    while n > 0:
        n -= 1
        result = chr(65 + (n % 26)) + result
        n //= 26
    return result


def authenticate_to_gs():
    """Authenticate with Google Sheets API"""
    creds = service_account.Credentials.from_service_account_file(
        settings.google.credentials_file, scopes=settings.google.scopes
    )
    service = build("sheets", "v4", credentials=creds)
    spreadsheets = service.spreadsheets()

    return spreadsheets


def read_sheet(spreadsheets, sheet_name, columns_number=5):
    """Function to read data from a sheet"""

    last_column = number_to_column(columns_number)
    result = (
        spreadsheets.values()
        .get(
            spreadsheetId=settings.google.spreadsheet_id,
            range=f"{sheet_name}!A:{last_column}",
        )
        .execute()
    )
    values = result.get("values", [])
    return values


def find_row_index(spreadsheets, sheet_name, search_value):
    """Finds the index of a first row containing search_value in a specified sheet"""

    values = read_sheet(spreadsheets, sheet_name)

    for i, row in enumerate(values, start=1):  # Google Sheets uses 1-based indexing
        if search_value in row:
            return i  # Return the row index

    return None  # Value not found


def write_to_sheet(spreadsheets, sheet_name, new_data):
    """Function to append a row to the sheet"""

    assert isinstance(new_data, list), "New data must be a list of values"

    last_column = number_to_column(len(new_data))

    request = spreadsheets.values().append(
        spreadsheetId=settings.google.spreadsheet_id,
        range=f"{sheet_name}!A:{last_column}",
        valueInputOption="RAW",
        body={"values": [new_data]},
    )
    request.execute()
    print("Values added successfully")


def delete_row_by_value(spreadsheets, sheet_name, search_value):
    """Searches for a row containing search_value in sheet_name and deletes the first one found"""

    row_number = find_row_index(spreadsheets, sheet_name, search_value)

    if row_number is None:
        print(f"No row found with '{search_value}' in {sheet_name}.")

    request = spreadsheets.batchUpdate(
        spreadsheetId=settings.google.spreadsheet_id,
        body={
            "requests": [
                {
                    "deleteDimension": {
                        "range": {
                            "sheetId": sheet_ids[sheet_name],
                            "dimension": "ROWS",
                            "startIndex": row_number - 1,  # Convert to zero-based index
                            "endIndex": row_number,
                        }
                    }
                }
            ]
        },
    )
    request.execute()
    print(f"Row {row_number} containing '{search_value}' deleted from {sheet_name}")


def update_row_by_value(spreadsheets, sheet_name, search_value, new_data):
    """Searches for a row containing search_value in sheet_name and updates the first one found with new_data"""

    assert isinstance(new_data, list), "New data must be a list of values"

    row_number = find_row_index(spreadsheets, sheet_name, search_value)

    if row_number is None:
        return f"No row found with '{search_value}' in {sheet_name}."

    last_column = number_to_column(len(new_data))

    request = spreadsheets.values().update(
        spreadsheetId=settings.google.spreadsheet_id,
        range=f"{sheet_name}!A{row_number}:{last_column}{row_number}",
        valueInputOption="RAW",
        body={"values": [new_data]},
    )
    request.execute()

    print(f"Row {row_number} updated in {sheet_name}.")

if __name__ == "__main__":


    settings = Dynaconf(
        envvar_prefix="PLUTARCH",
        settings_file="settings.toml",
        sysenv_fallback=True,
    )

    sheet_ids = {
        "players": settings.google.players_sheet_id,
        "games": settings.google.games_sheet_id,
        "registrations": settings.google.registrations_sheet_id,
        "auctions": settings.google.auctions_sheet_id,
    }


    # Test reading and writing
    spreadsheets = authenticate_to_gs()
    print("Current Players:", read_sheet(spreadsheets, "players"))
    # write_to_sheet(spreadsheets, "players", ["test", "Petya Petrov", 10])
    # delete_row_by_value(spreadsheets, "players", "test")
    update_row_by_value(
        spreadsheets, "players", "@Achestnova", ["@Achestnova", "Anastasiia Chestnova", 65]
    )
    print("Updated Players:", read_sheet(spreadsheets, "players"))
