import logging
from database.gs import *
from models import Player, Game, Registration, AvailableSlot

class Database():

    def __init__(self):
       
        self.l = logging.getLogger("database")

    def exists(self, data):

        try:
            match data:
                case Player():
                    res = gs.find_row_index(sheet_name="players", search_value=data.user_name)
                    return res is not None
                case Game():
                    res = gs.find_row_index(sheet_name="games", search_value=data.game_date)
                    return res is not None
                case Registration():
                    res = gs.find_row_index(sheet_name="registrations", search_value=data.game_date, search_value_2=data.user_name)
                    return res is not None
                case AvailableSlot():
                    res = gs.find_row_index(sheet_name="auctions", search_value=data.game_date, search_value_2=data.user_name)
                    return res is not None
        except:
            return False
        

    def create(self, data):

        if self.exists(data):
            return True
        
        try:
            match data:
                case Player():
                    new_data = [data.user_name, data.name, data.balance, data.can_sell, data.prio]
                    result = gs.write_to_sheet(sheet_name="players", new_data=new_data)
                case Game():
                    new_data = [data.game_date, data.cap, data.price, data.is_summarized]
                    result = gs.write_to_sheet(sheet_name="games", new_data=new_data)
                case Registration():
                    new_data = [data.requested_at, data.game_date, data.user_name, data.prio]
                    result = gs.write_to_sheet(sheet_name="registrations", new_data=new_data)
                case AvailableSlot():
                    new_data = [data.game_date, data.seller_user_name, data.tikkie_link, data.is_sent, data.buyer_user_name]
                    result = gs.write_to_sheet(sheet_name="auctions", new_data=new_data)

        except:
            return False
        return result
     

    def read(self, data) -> Player|Game|Registration|AvailableSlot|None:
        
        try:
            match data:
                case Player():
                    raw_data = gs.read_by_value(sheet_name="players", search_value=data.user_name)[0]
                    return Player(
                        user_name=raw_data[0],
                        name=raw_data[1],
                        balance=raw_data[2],
                        can_sell=raw_data[3],
                        prio=raw_data[4]
                    )                       

                case Game():
                    raw_data = gs.read_by_value(sheet_name="games", search_value=data.game_date)[0]
                    return Game(
                        game_date=raw_data[0],
                        cap=raw_data[1],
                        price=raw_data[2],
                        is_summarized=raw_data[3],
                    )

                case Registration():
                    raw_data = gs.read_by_value(sheet_name="registrations", search_value=data.game_date, search_value_2=data.user_name)[0]
                    return Registration(
                        game_date=raw_data[0],
                        user_name=raw_data[1],
                        requested_at=raw_data[2],
                        prio=raw_data[3],
                    )

                case AvailableSlot():
                    raw_data = gs.read_by_value(sheet_name="auctions", search_value=data.game_date, search_value_2=data.user_name)[0]
                    return AvailableSlot(
                        game_date=raw_data[0],
                        seller_user_name=raw_data[1],
                        requested_at=raw_data[2],
                        tikkie_link=raw_data[3],
                        is_sent=raw_data[4],
                        buyer_user_name=raw_data[5],
                    )
            
        except:
            return None
        

    def read_table(self, table: str, filter: str) -> list[Player]|list[Game]|list[Registration]|list[AvailableSlot]:
        """Reads the given sheet and returns a list of objects of the corresponding type. If filter is provided, the rows are filtered"""
        
        result = []
        try:
            raw_data = gs.read_by_value(sheet_name=table, search_value=filter)
            match table:
                case "players":
                    for row in range(len(raw_data)):
                        result.append(Player(
                            user_name=raw_data[0],
                            name=raw_data[1], 
                            balance=raw_data[2],
                            can_sell=raw_data[3],
                            prio=raw_data[4],
                        ))

                case "games":
                    for row in range(len(raw_data)):
                        result.append(Game(
                            game_date=raw_data[0],
                            cap=raw_data[1], 
                            price=raw_data[2],
                            is_summarized=raw_data[3],
                    ))

                case Registration():
                    for row in range(len(raw_data)):
                        result.append(Registration(
                            requested_at=raw_data[0],
                            game_date=raw_data[1],
                            user_name=raw_data[2],
                            prio=raw_data[3],
                    ))

                case AvailableSlot():
                    for row in range(len(raw_data)):
                        result.append(AvailableSlot(
                            game_date=raw_data[0],
                            seller_user_name=raw_data[1],
                            tikkie_link=raw_data[2],
                            requested_at=raw_data[3],
                            is_sent=raw_data[4],
                            buyer_user_name=raw_data[5],
                    ))
        except:
            return None
        return result


    def update(self, data):
        # TODO: not used yet, adjust to the use case. The current implementation is a bit odd, 
        # since we are updating only metadata and not the key field(s)

        if not self.exists(data):
            self.create(data)
        
        try:
            match data:
                case Player():
                    new_data = [data.user_name, data.name, data.balance, data.can_sell, data.prio]
                    result = gs.update_row_by_value(sheet_name="players", search_value=data.user_name, new_data=new_data)
                case Game():
                    new_data = [data.game_date, data.cap, data.price, data.is_summarized]
                    result = gs.update_row_by_value(sheet_name="games", search_value=data.game_date, new_data=new_data)
                case Registration():
                    new_data = [data.requested_at, data.game_date, data.user_name, data.prio]
                    result = gs.update_row_by_value(sheet_name="registrations", search_value=data.game_date, search_value_2=data.user_name, new_data=new_data)
                case AvailableSlot():
                    new_data = [data.game_date, data.seller_user_name, data.tikkie_link, data.is_sent, data.buyer_user_name]
                    result = gs.update_row_by_value(sheet_name="auctions", search_value=data.game_date, search_value_2=data.user_name, new_data=new_data)
        except:
            return False
        return result


    def delete(self, data):
        
        try:
            match data:
                case Player():
                    result = gs.delete_row_by_value(sheet_name="players", search_value=data.user_name)
                case Game():
                    result = gs.delete_row_by_value(sheet_name="games", search_value=data.game_date)
                case Registration():
                    result = gs.delete_row_by_value(sheet_name="registrations", search_value=data.game_date, search_value_2=data.user_name)
                case AvailableSlot():
                    result = gs.delete_row_by_value(sheet_name="auctions", search_value=data.game_date, search_value_2=data.user_name)
        
        except:
            return False
        return result