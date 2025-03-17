import logging
import time
from dataclasses import dataclass
from models import Player, Game, Registration, AvailableSlot, Prio
from database import Database

REGISTRATION_DEADLINE = 24 # Hours


class Plutarch():

    def __init__(self):
        # Required
        self.log = logging.getLogger("plutarch")
        self.db: Database = Database()


    def _get_game(self, game_date: str) -> tuple[Game, str]:
        return self.db.read(Game(game_date=game_date))


    def _get_player(self, user_name: str) -> tuple[Player, str]:
        return self.db.read(Player(user_name=user_name))
    

    def register(self, user_name: str, game_date: str) -> tuple[bool, str]:
        """Register the user for a game
        return success or failure and a reason
        True, "" means success
        False "some reason" has context of failure
        """
        player, reason = self._get_player(user_name)
        if reason:
            self.log.info(f"register: cannot get player details: {reason}")
            return False, "try again later"
        game, reason = self._get_game(game_date)
        if reason:
            self.log.info(f"register: cannot get game details: {reason}")
            return False, "try again later"
        
        if not player:
            return False, f"you are not an active member"
        if not game:
            return False, f"there is no game on that date"
        # Remove user from auction if it sells the ticket
        slot = AvailableSlot(game_date=game_date, seller_user_name=user_name)
        _, reason = self.db.delete(slot)
        if reason:
            self.log.info(f"register: cannot remove slot from auction: {reason}")
            return False, "try again later"
                 
        registration = Registration(
            requested_at=int(time.time()),
            game_date=game.game_date,
            user_name=player.user_name,
            prio=player.prio,
        )
        _, reason = self.db.create(registration)
        if reason:
            self.log.info(f"register: cannot register: {reason}")
            return False, "try again later"
        return True, ""
        # # Here we need to make sure high-prioriy members have a slot
        # # Fetch participants and prioritize them
        # registrations, reason = self.list_participants(game_date)
        # if reason:
        #     self.log.info(f"register: cannot validate current list of users: {reason}")
        #     return False, "try again later"
                    
        # registrations.sort(key=lambda x: (x.prio, x.requested_at))
        # # Check current capacity, if already full:
        # victim_name = ""
        # if len(registrations) > game.cap:
        #     # TODO: Check current time.
        #     # Reject request if too late - call unregister
        #     victim = registrations.pop()
        #     victim_name = victim.user_name
        #     self.leave_game(victim_name, game_date)
        #     # Kick low prio to waiting list if we have time (un-register)
        #     self.log.info(f"Un-registered {victim.user_name} for a game on {registration.game_date}")
        # if user_name == victim_name:
        #     return False, "already full"
        
        # # TODO: Inform unregistered people
        # return True, ""
        
    
    def list_participants(self, game_date: str) -> tuple[list[Registration], str]:

        game, reason = self._get_game(game_date)
        if reason:
            self.log.info(f"list_participants: cannot validate game: {reason}")
            return [], "try again later"
        if not game:
            return [], "" # Return empty set here, we don't care if game exist or not
         
        registrations, reason = self.db.read_table("registrations", game.game_date)
        if reason:
            self.log.info(f"list_participants: cannot read registrations: {reason}")
            return [], "try again later"
        registrations.sort(key=lambda x: (x.prio, x.requested_at)), ""
        return registrations, ""


    def leave_game(self, user_name: str, game_date: str, payment_link: str) -> tuple[bool, bool, str]:
        """Tries to unregister the user and sell his slot
        Returns statuses for unregistration, selling and reason why they might fail, if any
        True True "" means unregistered, sold, without errors
        True False "some reason" means user was unregistered but his slot was not sold for some reason
        False False "some reason" means user was not unregistered neither his slot was sold
        """
        # Check if person can sell the slot
        # Eligable candidates must
        #   have prio 1
        #   be registered
        #   not in list of seller already (cannot register/sell twice)

        player, reason = self._get_player(user_name)
        if reason:
            self.log.info(f"leave_game: cannot get player details: {reason}")
            return  False, False, "try again later"
        
        if not player:
            return False, False, "you are not an active member"
        
        registration, reason = self.db.read(Registration(game_date=game_date, user_name=user_name))
        if reason:
            self.log.info(f"leave_game: cannot read registrations: {reason}")
            return  False, False, "try again later"
        
        if not registration:
            return False, False, f"you are not registered"
        
        # Unregistering first regardless of priority
        # If subsequent placing to auction fails, user can retry by simply registering back
        _, reason = self.db.delete(registration)
        if reason:
            self.log.info(f"leave_game: cannot delete registration: {reason}")
            return  False, False, "try again later"
        # If person does not have full subscription, he cannot sell thus fast return
        if player.prio != 1:
            return True, False, "" # This is not an error
        
        order = AvailableSlot(game_date=game_date, seller_user_name=user_name, requested_at=int(time.time()), tikkie_link=payment_link)
        self.log.info(f"Placing order of {user_name} to auction")
        _, reason = self.db.create(order)
        if reason:
            self.log.info(f"leave_game: cannot sell slot: {reason}")
            return True, False, "try again later"
    
        return True, True, ""

    def _move_to_waiting_list(self, r: Registration):
        self.log.info(f"Moving {r.user_name} to a waiting list")


    def _update_balance(self, p: Player):
        self.log.info(f"Updating balance of {p.user_name}. Current balance {p.balance}")
    

    def collect_money(self, p: Player):
        tikkie = "https://make-me-rich"
        self.log.info(f"Sending tikkie to {p.user_name}. Link: {tikkie}")