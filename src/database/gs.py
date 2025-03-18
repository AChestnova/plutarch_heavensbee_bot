import logging
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dynaconf import Dynaconf
from functools import lru_cache

GS_SETTINGS = Dynaconf(
    envvar_prefix="PLUTARCH",
    settings_file="config/settings.toml",
    sysenv_fallback=True,
)

SHEET_IDS = {
    "players": GS_SETTINGS.google.players_sheet_id,
    "games": GS_SETTINGS.google.games_sheet_id,
    "registrations": GS_SETTINGS.google.registrations_sheet_id,
    "auctions": GS_SETTINGS.google.auctions_sheet_id,
}

SHEET_NUM_COL = {
    "players": 5,
    "games": 4,
    "registrations": 4,
    "auctions": 6
}
log = logging.getLogger("database")

def column_number_to_excel_column_name(n):
    """Returns an Excel-like column name by its order number (e.g. 1 -> A, 27 -> AA)"""

    result = ""
    while n > 0:
        n -= 1
        result = chr(65 + (n % 26)) + result
        n //= 26
    return result

@lru_cache(maxsize=1)
def authenticate_to_gs():
    """Authenticate with Google Sheets API"""

    log.info("Authenticating to Google Sheets")
    #TODO: Exit if cannot connect
    creds = service_account.Credentials.from_service_account_file(
        GS_SETTINGS.google.credentials_file, scopes=GS_SETTINGS.google.scopes
    )
    service = build("sheets", "v4", credentials=creds)
    spreadsheets = service.spreadsheets()

    return spreadsheets


def read_sheet(sheet_name, columns_number=5) -> tuple[list, str]:
    """Function to read data from a sheet
    return list of lists that represents spreadsheet
    and error in case we cannot connect to a database"""
    last_column = column_number_to_excel_column_name(SHEET_NUM_COL[sheet_name])

    log.info(f"read_sheet: reading from {sheet_name} {last_column}")
    spreadsheets = authenticate_to_gs()
    try:
        result = (
            spreadsheets.values()
            .get(
                spreadsheetId=GS_SETTINGS.google.spreadsheet_id,
                range=f"{sheet_name}!A:{last_column}",
            )
            .execute()
        )
    except:
        return [], f"cannot read {sheet_name}: database unavailable"
    
    return result.get("values", []), ""


def find_row_index(sheet_name, search_value, search_value_2=None) -> tuple[int|None, str]:
    """Finds the index of a first row containing search_value in a specified sheet.
    If search_value_2 is given, checks if that value is also in the row"""

    log.info(f"find_row_index: reading from {sheet_name} {search_value} {search_value_2}")
    values, err = read_sheet(sheet_name)
    if err:
        return None, f"cannot find index from {sheet_name}: {err}"

    for i, row in enumerate(values, start=1):  # Google Sheets uses 1-based indexing
        if search_value in row:
            # If there are 2 filters:
            # In case search_value_2 is None or won't execute further
            # so we simply append
            # In case search value_2 is not None we check search_value_2 in row
            if not search_value_2 or search_value_2 in row:
                # if we need to find only one value, return row immediately
                return i, "" 
    return None, ""


def write_to_sheet(sheet_name, new_data) -> tuple[bool,str]:
    """Function to append a row to the sheet"""
    
    last_column = column_number_to_excel_column_name(len(new_data))

    log.info(f"write_to_sheet: writing to {sheet_name} {new_data}")
    spreadsheets = authenticate_to_gs()
    try:
        request = spreadsheets.values().append(
            spreadsheetId=GS_SETTINGS.google.spreadsheet_id,
            range=f"{sheet_name}!A:{last_column}",
            valueInputOption="RAW",
            body={"values": [new_data]},
        )
        result = request.execute()
    except:
        return False, f"cannot write to {sheet_name}: database unavailable"
    
    if not result.get("updates", None):
        return False, f"cannot write to {sheet_name}"
    return True, ""


def read_by_value(sheet_name, search_value, search_value_2=None) -> tuple[list, str]:
    """Returns all the rows containing search_value and search_value_2 (if given) 
    in the specified sheet"""

    log.info(f"read_by_value: reading from {sheet_name} {search_value} {search_value_2}")
    values, err = read_sheet(sheet_name)
    if err:
        return [], f"cannot read value from {sheet_name}: {err}"

    result = []
    log.info(f"read_by_value: result from {sheet_name} before filtering by {search_value} {search_value_2}: {values}")
    for row in values:

        if search_value in row:
            # If there are 2 filters:
            # In case search_value_2 is None or won't execute further
            # so we simply append
            # In case search value_2 is not None we check search_value_2 in row
            if search_value_2:
                if search_value_2 in row:
                # if we need to find only one value, add the row to the result immediately
                # otherwise, return only the row with both values
                    result.append(row)
            else:
                result.append(row)

    log.info((f"read_by_value: filtered values {result}"))
    return result, ""



def delete_row_by_value(sheet_name, search_value, search_value_2=None) -> tuple[bool, str]:
    """Searches for a row containing search_value (or both search_value and search_value_2 if provided) 
    in sheet_name and deletes the first one found"""

    row_number, err = find_row_index(sheet_name, search_value, search_value_2)
    log.info(f"delete_row_by_value: deleting from {sheet_name} {row_number}")
    if err:
        return False, f"cannot delete row from {sheet_name}: {err}"
    
    if not row_number:
        return False, f"cannot delete row from {sheet_name}: no row found"

    spreadsheets = authenticate_to_gs()
    try:
        request = spreadsheets.batchUpdate(
            spreadsheetId=GS_SETTINGS.google.spreadsheet_id,
            body={
                "requests": [
                    {
                        "deleteDimension": {
                            "range": {
                                "sheetId": SHEET_IDS[sheet_name],
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
    except:
        return False, "cannot delete row from {sheet_name}: database unavailable"
    # TODO: result always exist, need to check specific content
    if not result:
        return False, "cannot delete row from {sheet_name}: wrong result"
    
    return True, ""


def update_row_by_value(sheet_name, search_value, search_value_2, new_data) -> tuple[bool, str]:
    """Searches for a row containing search_value in sheet_name and updates the first one found with new_data"""

    last_column = column_number_to_excel_column_name(len(new_data))
    spreadsheets = authenticate_to_gs()
    row_number, err = find_row_index(sheet_name, search_value, search_value_2)
    log.info(f"update_row_by_value: updating {sheet_name} {row_number}")
    if err:
        log.info(f"update_row_by_value: cannot update row in {sheet_name}: {err}")
        return False, f"cannot update row in {sheet_name}: {err}"
    
    if not row_number:
        log.info(f"update_row_by_value: cannot update row in {sheet_name}: {err}")
        return False, f"cannot update row in {sheet_name}: no row found"
    
    try:
        request = spreadsheets.values().update(
            spreadsheetId=GS_SETTINGS.google.spreadsheet_id,
            range=f"{sheet_name}!A{row_number}:{last_column}{row_number}",
            valueInputOption="RAW",
            body={"values": [new_data]},
        )
        result = request.execute()
        log.info(f"update_row_by_value: result {result}")
    except:
        return False, f"cannot update row in {sheet_name}: database unavailable"

    # TODO: result always exist, need to check specific content
    if not result:
        log.info(f"update_row_by_value: cannot update row in {sheet_name}: wrong result {result}")
        return False, f"cannot update row in {sheet_name}: wrong result"
    
    return True, ""

if __name__ == "__main__":


    GS_SETTINGS = Dynaconf(
        envvar_prefix="PLUTARCH",
        settings_file="config/settings.toml",
        sysenv_fallback=True,
    )

    SHEET_IDS = {
        "players": GS_SETTINGS.google.players_sheet_id,
        "games": GS_SETTINGS.google.games_sheet_id,
        "registrations": GS_SETTINGS.google.registrations_sheet_id,
        "auctions": GS_SETTINGS.google.auctions_sheet_id,
    }


    # Test reading and writing
    
    #print("Current Players:", read_sheet("players"))
    #write_to_sheet("auctions", ["2024-12-01", "@test_user", "link", 12334, None])
    #delete_row_by_value("players", "Petya Petrov")
    # update_row_by_value(
    #     "players", "@Achestnova", ["@Achestnova", "Anastasiia Chestnova", 65]
    # )
    # print("Updated Players:", read_sheet("players"))
