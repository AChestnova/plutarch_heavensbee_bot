from google.oauth2 import service_account
from googleapiclient.discovery import build
from dynaconf import Dynaconf


def column_number_to_excel_column_name(n):
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


def read_sheet(sheet_name, columns_number=5):
    """Function to read data from a sheet"""

    spreadsheets = authenticate_to_gs()

    last_column = column_number_to_excel_column_name(columns_number)
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


def find_row_index(sheet_name, search_value, search_value_2=None):
    """Finds the index of a first row containing search_value in a specified sheet.
    If search_value_2 is given, checks if that value is also in the row"""

    spreadsheets = authenticate_to_gs()
    values = read_sheet(sheet_name)

    for i, row in enumerate(values, start=1):  # Google Sheets uses 1-based indexing
        if search_value in row:
            if not search_value_2:
                # if we need to find only one value, return row immediately
                return i 
            if search_value_2 in row:
                # otherwise, return only the index for row with both values:
                return i
            
    return None  # Value not found


def write_to_sheet(sheet_name, new_data):
    """Function to append a row to the sheet"""

    assert isinstance(new_data, list), "New data must be a list of values"

    spreadsheets = authenticate_to_gs()

    last_column = column_number_to_excel_column_name(len(new_data))

    request = spreadsheets.values().append(
        spreadsheetId=settings.google.spreadsheet_id,
        range=f"{sheet_name}!A:{last_column}",
        valueInputOption="RAW",
        body={"values": [new_data]},
    )
    result = request.execute()
    if not result.get("updates", None):
        return False # unsuccessful
    return True


def read_by_value(sheet_name, search_value, search_value_2=None):
    """Returns all the rows containing search_value and search_value_2 (if given) 
    in the specified sheet"""

    values = read_sheet(sheet_name)

    result = []
    for row in values:
        if search_value in row:
            if not search_value_2 or search_value_2 in row:
                # if we need to find only one value, add the row to the result immediately
                # otherwise, return only the row with both values
                result.append(row)
        
    return None  # Value not found



def delete_row_by_value(sheet_name, search_value, search_value_2=None):
    """Searches for a row containing search_value (or both search_value and search_value_2 if provided) 
    in sheet_name and deletes the first one found"""

    spreadsheets = authenticate_to_gs()
    row_number = find_row_index(sheet_name, search_value, search_value_2)

    if row_number is None:
        print(f"No row found with '{search_value}' in {sheet_name}.")
        return False

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
    result = request.execute()
    print(f"{result=}")
    if not result:
         return False # unsuccessful
    return True


def update_row_by_value(sheet_name, search_value, search_value_2, new_data):
    """Searches for a row containing search_value in sheet_name and updates the first one found with new_data"""

    spreadsheets = authenticate_to_gs()

    assert isinstance(new_data, list), "New data must be a list of values"

    row_number = find_row_index(spreadsheets, sheet_name, search_value, search_value_2)

    if row_number is None:
        return f"No row found with '{search_value}', '{search_value_2}' in {sheet_name}."

    last_column = column_number_to_excel_column_name(len(new_data))

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
        settings_file="config/settings.toml",
        sysenv_fallback=True,
    )

    sheet_ids = {
        "players": settings.google.players_sheet_id,
        "games": settings.google.games_sheet_id,
        "registrations": settings.google.registrations_sheet_id,
        "auctions": settings.google.auctions_sheet_id,
    }


    # Test reading and writing
    
    #print("Current Players:", read_sheet("players"))
    #write_to_sheet("auctions", ["2024-12-01", "@test_user", "link", 12334, None])
    #delete_row_by_value("players", "Petya Petrov")
    # update_row_by_value(
    #     "players", "@Achestnova", ["@Achestnova", "Anastasiia Chestnova", 65]
    # )
    # print("Updated Players:", read_sheet("players"))
