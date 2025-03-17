import logging
import database.gs as gs
from models import Storable, Player, Game, Registration, AvailableSlot


TABLE_TO_OBJECT_MAP = {
    Player.sheet_name(): Player,
    Game.sheet_name(): Game,
    Registration.sheet_name(): Registration,
    AvailableSlot.sheet_name(): AvailableSlot
}
    
class Database():

    def __init__(self):
       
        self.log = logging.getLogger("database")


    def exists(self, data: Storable) -> tuple[bool, str]:

        value1, value2 = data.unique_keys
        result, err = gs.find_row_index(sheet_name=data.sheet_name(), search_value=value1, search_value_2=value2)
        if err:
            return False, f"cannot find item: {err}"
        
        if not result:
            return False, ""
        return True, ""

    def create(self, data: Storable) -> tuple[bool, str]:

        exist, err = self.exists(data)
        if exist:
            return True, ""
        
        _, err = gs.write_to_sheet(sheet_name=data.sheet_name(), new_data=list(data))
        if err:
            return False, f"cannot create item: {err}"
        
        return True, err
     

    def read(self, data: Storable) -> tuple[Storable|None, str]:

        value1, value2 = data.unique_keys
        raw_data, err = gs.read_by_value(sheet_name=data.sheet_name(), search_value=value1, search_value_2=value2)
        if err:
            return None, f"cannot read item: {err}"
        if not raw_data:
            return None, ""
        
        assert len(raw_data) == 1, "read should return only 1 value"
        
        storable = TABLE_TO_OBJECT_MAP[data.sheet_name()]
        result = storable.from_list(raw_data[0])

        return result, ""
        

    def read_table(self, table: str, filter: str) -> tuple[list[Storable], str]:
        """Reads the given sheet and returns a list of objects of the corresponding type. If filter is provided, the rows are filtered"""
        
        raw_data, err = gs.read_by_value(sheet_name=table, search_value=filter)
        if err:
            return [], f"cannot read table: {err}"
        if not raw_data:
            return [], ""
        
        storable = TABLE_TO_OBJECT_MAP[table]

        result = []
        for i in range(len(raw_data)):
            item = storable.from_list(raw_data[i])
            result.append(item)
                
        return result, ""


    def update(self, data) -> tuple[bool, str]:
        # TODO: not used yet, adjust to the use case. The current implementation is a bit odd, 
        # since we are updating only metadata and not the key field(s)

        exist, err = self.exists(data)
        if err:
            return False, f"cannot update item: {err}"
        if not exist:
            return False, f"cannot update: {err}"
        
        value1, value2 = data.unique_keys
        _, err = gs.update_row_by_value(sheet_name=data.sheet_name(), search_value=value1, search_value_2=value2, new_data=list(data))
     
        if err:
            return False, f"cannot update item: {err}"
        
        return True, err


    def delete(self, data) -> tuple[bool, str]:

        exist, err = self.exists(data)
        if err:
            return False, f"cannot delete item: {err}"
        if not exist:
            return True, ""
        
        value1, value2 = data.unique_keys
        _, err = gs.delete_row_by_value(sheet_name=data.sheet_name(), search_value=value1, search_value_2=value2)
        
        if err:
            return False, f"cannot delete item: {err}"
        
        return True, err