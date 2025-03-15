import logging
from models import Player, Game, Registration, AvailableSlot, Prio
#import gs
from helpers import next_sunday, sunday_in_two_weeks
class Database():

    def __init__(self):
       
        self.l = logging.getLogger("database")
        self.players: dict[str: Player] = {}
        self.games: dict[str: Game] = {}
        self.registrations: dict[str: Registration] = {}
        self.auction: dict[str: AvailableSlot] = {}
        self.__fill_tables()

    def __fill_tables(self):

        p = Player(
            user_name="@kchestnov",
            name="Konstantin Chestnov",
            balance=0,
            can_sell=False,
            prio=Prio.FULL,
        )
        self.players[p.user_name] = p

        p = Player(
            user_name="@AChestnova",
            name="Anastasiia Chestnova",
            balance=0,
            can_sell=False,
            prio=Prio.HALF,
        )
        self.players[p.user_name] = p

        for d in [next_sunday().strftime("%Y-%m-%d"), sunday_in_two_weeks().strftime("%Y-%m-%d")]:
            g = Game(
                game_date=d,
                cap=14,
                price=10,
                is_summarized=False
            )
            self.games[d] = g

        for d in [next_sunday().strftime("%Y-%m-%d")]:
            r = Registration(
                requested_at=12233445,
                game_date=d,
                user_name="@Incognito",
                prio=2
            )
            self.registrations[d] = r
   
    def exists(self, data):

        match data:
            case Player():
                return data.user_name in self.players
            case Game():
                return data.game_date in self.games
            case Registration():
                k = data.game_date + "_" + data.user_name
                return k in self.registrations
            case AvailableSlot():
                k = data.game_date + "_" + data.seller_user_name
                return k in self.auction
     
    def create(self, data):

        if self.exists(data):
            return
        
        match data:
            case Player():
                self.players[data.user_name] = data
            case Game():
                self.games[data.game_date] = data
            case Registration():
                k = data.game_date + "_" + data.user_name
                self.registrations[k] = data
            case AvailableSlot():
                k = data.game_date + "_" + data.seller_user_name
                self.auction[k] = data
    
    def read(self, data) -> Player|Game|Registration|AvailableSlot:
        
        if not self.exists(data):
            return

        match data:
            case Player():
                return self.players[data.user_name]
            case Game():
                return self.games[data.game_date]
            case Registration():
                k = data.game_date + "_" + data.user_name
                return self.registrations[k]
            case AvailableSlot():
                k = data.game_date + "_" + data.seller_user_name
                return self.auction[k]

    def filter(self, d: dict, f: str) -> list[Player]|list[Game]|list[Registration]|list[AvailableSlot]:
        filtered = []
        for k, v in d.items():
            if f in k:
                filtered.append(v)
        return filtered

    def read_table(self, table: str, filter: str) -> list[Player]|list[Game]|list[Registration]|list[AvailableSlot]:
        match table:
            case "players":
                return self.spreadsheet_helper.read_table(table)
            case "games":
                return self.filter(self.games, filter)
            case "registrations":
                return self.filter(self.registrations, filter)
            case "auction":
                return self.filter(self.auction, filter)

    def update(self, data):

        if not self.exists(data):
            self.create(data)
        
        match data:
            case Player():
                self.players[data.user_name] = data
            case Game():
                self.games[data.game_date] = data
            case Registration():
                k = data.game_date + "_" + data.user_name
                self.registrations[k] = data
            case AvailableSlot():
                k = data.game_date + "_" + data.seller_user_name
                self.auction[k] = data 
    
    def delete(self, data):

        if not self.exists(data):
            return
        
        match data:
            case Player():
                del self.players[data.user_name]
            case Game():
                del self.games[data.game_date]
            case Registration():
                k = data.game_date + "_" + data.user_name
                del self.registrations[k]
            case AvailableSlot():
                k = data.game_date + "_" + data.seller_user_name
                del self.auction[k] 
