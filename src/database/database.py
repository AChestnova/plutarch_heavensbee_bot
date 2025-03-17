import logging
import database.gs as gs
from models import Player, Game, Registration, AvailableSlot

class Database():

    def __init__(self):
       
        self.l = logging.getLogger("database")


    def exists(self, data) -> tuple[bool, str]:

        reason = ""
        match data:
            case Player():
                result, reason = gs.find_row_index(sheet_name="players", search_value=data.user_name)
            case Game():
                result, reason = gs.find_row_index(sheet_name="games", search_value=data.game_date)
            case Registration():
                result, reason = gs.find_row_index(sheet_name="registrations", search_value=data.game_date, search_value_2=data.user_name)
            case AvailableSlot():
                result, reason = gs.find_row_index(sheet_name="auctions", search_value=data.game_date, search_value_2=data.seller_user_name)

        if reason:
            return False, f"cannot find item: {reason}"
        
        if not result:
            return False, ""
        return True, ""

    def create(self, data) -> tuple[bool, str]:

        exist, reason = self.exists(data)
        if exist:
            return True, ""
        
        match data:
            case Player():
                new_data = [data.user_name, data.name, data.balance, data.can_sell, data.prio]
                _, reason = gs.write_to_sheet(sheet_name="players", new_data=new_data)
            case Game():
                new_data = [data.game_date, data.cap, data.price, data.is_summarized]
                _, reason = gs.write_to_sheet(sheet_name="games", new_data=new_data)
            case Registration():
                new_data = [data.game_date, data.requested_at, data.user_name, data.prio]
                _, reason = gs.write_to_sheet(sheet_name="registrations", new_data=new_data)
            case AvailableSlot():
                new_data = [data.game_date, data.seller_user_name, data.requested_at, data.tikkie_link, data.is_sent, data.buyer_user_name]
                _, reason = gs.write_to_sheet(sheet_name="auctions", new_data=new_data)

        if reason:
            return False, f"cannot create item: {reason}"
        
        return True, reason
     

    def read(self, data) -> tuple[Player|Game|Registration|AvailableSlot|None, str]:
        
        match data:
            case Player():
                raw_data, reason = gs.read_by_value(sheet_name="players", search_value=data.user_name)
                if reason:
                    return None, f"cannot read item: {reason}"
                if not raw_data:
                    return None, ""
                raw_data = raw_data[0]
                result = Player(
                    user_name=raw_data[0],
                    name=raw_data[1],
                    balance=raw_data[2],
                    can_sell=raw_data[3],
                    prio=int(raw_data[4])
                )                       

            case Game():
                raw_data, reason = gs.read_by_value(sheet_name="games", search_value=data.game_date)
                if reason:
                    return None, f"cannot read item: {reason}"
                if not raw_data:
                    return None, ""
                raw_data = raw_data[0]
                result = Game(
                    game_date=raw_data[0],
                    cap=raw_data[1],
                    price=raw_data[2],
                    is_summarized=raw_data[3],
                )

            case Registration():
                raw_data, reason = gs.read_by_value(sheet_name="registrations", search_value=data.game_date, search_value_2=data.user_name)
                if reason:
                    return None, f"cannot read item: {reason}"
                if not raw_data:
                    return None, ""
                raw_data = raw_data[0]
                result = Registration(
                    game_date=raw_data[0],
                    requested_at=raw_data[1],
                    user_name=raw_data[2],
                    prio=raw_data[3],
                )

            case AvailableSlot():
                raw_data, reason = gs.read_by_value(sheet_name="auctions", search_value=data.game_date, search_value_2=data.seller_user_name)
                if reason:
                    return None, f"cannot read item: {reason}"
                if not raw_data:
                    return None, ""
                raw_data = raw_data[0]
                result = AvailableSlot(
                    game_date=raw_data[0],
                    seller_user_name=raw_data[1],
                    requested_at=raw_data[2],
                    tikkie_link=raw_data[3],
                    is_sent=raw_data[4],
                    buyer_user_name=raw_data[5],
                )
        
        return result, ""
        

    def read_table(self, table: str, filter: str) -> tuple[list[Player]|list[Game]|list[Registration]|list[AvailableSlot], str]:
        """Reads the given sheet and returns a list of objects of the corresponding type. If filter is provided, the rows are filtered"""
        
        result = []
        raw_data, reason = gs.read_by_value(sheet_name=table, search_value=filter)
        if reason:
            return [], f"cannot read table: {reason}"
        if not raw_data:
            return [], ""
        match table:
            case "players":
                for i in range(len(raw_data)):
                    row = raw_data[i]
                    result.append(Player(
                        user_name=row[0],
                        name=row[1], 
                        balance=row[2],
                        can_sell=row[3],
                        prio=row[4],
                    ))

            case "games":
                for i in range(len(raw_data)):
                    row = raw_data[i]
                    result.append(Game(
                        game_date=row[0],
                        cap=row[1], 
                        price=row[2],
                        is_summarized=row[3],
                ))

            case "registrations":
                self.l.info(f"read_table: registrations: iterating over {raw_data}")
                for i in range(len(raw_data)):
                    row = raw_data[i]
                    result.append(Registration(
                        game_date=row[0],
                        requested_at=row[1],
                        user_name=row[2],
                        prio=row[3],
                ))

            case "auctions":
                for i in range(len(raw_data)):
                    row = raw_data[i]
                    result.append(AvailableSlot(
                        game_date=row[0],
                        seller_user_name=row[1],
                        requested_at=row[2],
                        tikkie_link=row[3],
                        is_sent=row[4],
                        buyer_user_name=row[5],
                ))
                    
                
        return result, ""


    def update(self, data) -> tuple[bool, str]:
        # TODO: not used yet, adjust to the use case. The current implementation is a bit odd, 
        # since we are updating only metadata and not the key field(s)

        exist, reason = self.exists(data)
        if reason:
            return False, f"cannot update item: {reason}"
        if not exist:
            return False, f"cannot update: {reason}"
        
        match data:
            case Player():
                new_data = [data.user_name, data.name, data.balance, data.can_sell, data.prio]
                _, reason = gs.update_row_by_value(sheet_name="players", search_value=data.user_name, new_data=new_data)
            case Game():
                new_data = [data.game_date, data.cap, data.price, data.is_summarized]
                _, reason= gs.update_row_by_value(sheet_name="games", search_value=data.game_date, new_data=new_data)
            case Registration():
                new_data = [data.game_date, data.requested_at, data.user_name, data.prio]
                _, reason= gs.update_row_by_value(sheet_name="registrations", search_value=data.game_date, search_value_2=data.user_name, new_data=new_data)
            case AvailableSlot():
                new_data = [data.game_date, data.seller_user_name, data.requested_at, data.tikkie_link, data.is_sent, data.buyer_user_name]
                _, reason= gs.update_row_by_value(sheet_name="auctions", search_value=data.game_date, search_value_2=data.user_name, new_data=new_data)
    
        if reason:
            return False, f"cannot update item: {reason}"
        
        return True, reason


    def delete(self, data) -> tuple[bool, str]:

        exist, reason = self.exists(data)
        if reason:
            return False, f"cannot delete item: {reason}"
        if not exist:
            return True, ""
        
        result = False
        match data:
            case Player():
                _, reason = gs.delete_row_by_value(sheet_name="players", search_value=data.user_name)
            case Game():
                _, reason = gs.delete_row_by_value(sheet_name="games", search_value=data.game_date)
            case Registration():
                _, reason = gs.delete_row_by_value(sheet_name="registrations", search_value=data.game_date, search_value_2=data.user_name)
            case AvailableSlot():
                _, reason = gs.delete_row_by_value(sheet_name="auctions", search_value=data.game_date, search_value_2=data.seller_user_name)
        
        if reason:
            return False, f"cannot delete item: {reason}"
        
        return True, reason