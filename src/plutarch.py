import logging
import time
from dataclasses import dataclass
from models import Player, Game, Registration, AvailableSlot, Prio
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
    

    def register(self, user_name, game_date) -> bool:

        p = self.get_player(user_name)
        if not p:
            reason = "You are not a member. Please ask admin to add you."
            self.l.info(f"Cannot register: {user_name} does not exist in the DB")
            return reason, False

        g = self.get_game(game_date)
        if not g:
             reason = f"There is no game on {game_date}"
             self.l.info(f"Cannot register: Incorrect game date")
             return reason, False

        # TODO: Remove user from auction if it sells the ticket
        # TODO: Check current capacity, if already full:
        #           Check current time.
        #           Kick low prio to waiting list if we have time.
        #           Reject request if too late           
        r = Registration(
            requested_at=int(time.time()),
            game_date=g.game_date,
            user_name=p.user_name,
            prio=p.prio,
        )
        
        self.db.create(r)
        
        # TODO: Check current registered players
        # If more than capacity, we need to un-register low-prioriy and move them to waiting list
        # TODO: Inform unregistered people
        self.l.info(f"Registered {r.user_name} for a game on {r.game_date}")
        reason = ""
        return reason, True
        
    
    def list_participants(self, game_date):

        g = self.get_game(game_date)
        if not g:
             self.l.info(f"Incorrect game date")
             return []
            
        reg = self.db.read_table("registrations", g.game_date)
        self.l.info(f"Current registrations: {reg}")
        return reg


    def leave_game(self, user_name, game_date, payment_link):

        # Check if person can sell the slot
        # Eligable candidates must
        #   have prio 1
        #   be registered
        #   not in list of seller already (cannot register/sell twice)

        p = self.get_player(user_name)
        if not p:
            self.l.info(f"Cannot sell: {user_name} does not exist in the DB")
            return False, False
        
        # Requested at means nothing here
        reg = self.db.read(Registration(game_date=game_date, user_name=user_name, requested_at=0, prio=p.prio))
        if not reg:
            self.l.info(f"Cannot sell: {user_name} is not registered for the game")
            return False, False

        if p.prio != Prio.FULL:
            self.l.info(f"Cannot sell: {user_name} does not have a valid subscription. Unregistering")
            self._unregister(reg)
            return True, False

        self.l.info(f"Placing order of {user_name} to auction")

        order = AvailableSlot(
            game_date=game_date,
            seller_user_name=user_name,
            tikkie_link=payment_link,
            requested_at=int(time.time() * 1000),
            is_sent=False
        )
        
        self._unregister(reg)
        self.db.create(order)
        return True, True

    def _move_to_waiting_list(self, r: Registration):
        self.l.info(f"Moving {r.user_name} to a waiting list")


    def _unregister(self, r: Registration):
        self.l.info(f"Removing {r.user_name} from participants on {r.game_date}")
        self.db.delete(r)
        # TODO: Update balance
    

    def _update_balance(self, p: Player):
        self.l.info(f"Updating balance of {p.user_name}. Current balance {p.balance}")
    

    def collect_money(self, p: Player):
        tikkie = "https://make-me-rich"
        self.l.info(f"Sending tikkie to {p.user_name}. Link: {tikkie}")