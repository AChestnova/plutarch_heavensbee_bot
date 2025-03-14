import logging
import time
from dataclasses import dataclass
from models import Player, Game, Registration, AvailableSlot
from database import Database

REGISTRATION_DEADLINE = 24 # Hours


class Plutarch():

    def __init__(self):
        # Required
        self.l = logging.getLogger("plutarch")
        self.db: Database = Database()

    def get_game(self, game_date) -> Game:
        return self.db.read(Game(game_date=game_date))

    def get_player(self, user_name) -> Player:
        return self.db.read(Player(user_name=user_name))
    
    def register(self, user_name, game_date):

        p = self.get_player(user_name)
        if not p:
            self.l.info(f"Cannot register: {user_name} does not exist in the DB")

        g = self.get_game(game_date)
        if not g:
             self.l.info(f"Cannot register: Incorrect game date")
             
        r = Registration(
            requested_at=int(time.time()),
            game_date=g.game_date,
            user_name=p.user_name,
            prio=p.prio,
        )

        if not self.db.exists(r):
            self.db.create(r)

        self.l.info(f"Registered {r.user_name} for a game on {r.game_date}")
    
    def list_participants(self, game_date):

        g = self.get_game(game_date)
        if not g:
             self.l.info(f"Incorrect game date")
             return []
            
        reg = self.db.read_table("registrations", g.game_date)
        self.l.info(f"Current registrations: {reg}")
        return reg
        
    def place_order(self, a: AvailableSlot):
        self.l.info(f"Placing order of {a.user_name} to auction")

    def move_to_waiting_list(self, r: Registration):
        self.l.info(f"Moving {r.user_name} to a waiting list")

    def unregister(self, r: Registration):
        self.l.info(f"Removing {r.user_name} from participants on {r.game_date}")
    
    def update_balance(self, p: Player):
        self.l.info(f"Updating balance of {p.user_name}. Current balance {p.balance}")
    
    def collect_money(self, p: Player):
        tikkie = "https://make-me-rich"
        self.l.info(f"Sending tikkie to {p.user_name}. Link: {tikkie}")