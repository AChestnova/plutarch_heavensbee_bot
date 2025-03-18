import logging
import time
from models import Player, Game, Registration, AvailableSlot, Priorities
from database import Database
from dataclasses import dataclass

REGISTRATION_DEADLINE = 24 # Hours


class Plutarch():

    def __init__(self):
        # Required
        self.log = logging.getLogger("plutarch")
        self.db: Database = Database()


    def _get_game(self, game_date: str) -> tuple[Game|None, str]:
        return self.db.read(Game(game_date=game_date))


    def get_player(self, user_name: str) -> tuple[Player|None, str]:
        return self.db.read(Player(user_name=user_name))
    

    def register(self, player: Player, game_date: str) -> tuple[bool, str]:
        """Register the user for a game
        return success or failure and an error if any
        True, "" means success
        False "some error" has context of failure
        """
        # Remove user from auction if it sells the ticket
        slot = AvailableSlot(game_date=game_date, seller_user_name=player.user_name)
        _, err = self.db.delete(slot)
        if err:
            self.log.info(f"register: cannot remove slot from auction: {err}")
            return False, "try again later"
                 
        registration = Registration(
            requested_at=int(time.time()),
            game_date=game_date,
            user_name=player.user_name,
            prio=player.prio,
        )
        _, err = self.db.create(registration)
        if err:
            self.log.info(f"register: cannot register: {err}")
            return False, "try again later"
        return True, ""
        # # Here we need to make sure high-prioriy members have a slot
        # # Fetch participants and prioritize them
        # registrations, err = self.list_participants(game_date)
        # if err:
        #     self.log.info(f"register: cannot validate current list of users: {err}")
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
        
    def is_registered(self, user_name: str, game_dates: list[str]) -> list[tuple[Registration|None, str]]:
        result = []
        for game_date in game_dates:
            registration, err = self.db.read(Registration(game_date=game_date, user_name=user_name))
            if err:
                self.log.info(f"list_user_registrations: cannot read registration: {err}")
                result.append((False, "try again later"))
            elif not registration:
                result.append((None, ""))
            else:
                result.append((registration, ""))
        return result

    def list_participants(self, game_date: str) -> tuple[list[Registration], str]:

        registrations, err = self.db.read_table("registrations", game_date)
        if err:
            self.log.info(f"list_participants: cannot read registrations: {err}")
            return [], "try again later"
        
        registrations.sort(key=lambda x: (x.prio, x.requested_at))

        return registrations, ""
    

    def leave_game(self, player: Player, registration: Registration, payment_link: str) -> tuple[bool, bool, str]:
        """Tries to unregister the user and sell his slot
        Returns statuses for unregistration, selling and error why they might fail, if any
        True True "" means unregistered, sold, without errors
        True False "some error" means user was unregistered but his slot was not sold for some error
        False False "some error" means user was not unregistered neither his slot was sold
        """

        # Unregistering first regardless of priority
        # If subsequent placing to auction fails, user can retry by simply registering back
        _, err = self.db.delete(registration)
        if err:
            self.log.info(f"leave_game: cannot delete registration: {err}")
            return  False, False, "try again later"
        # If person does not have full subscription, he cannot sell thus fast return
        if player.prio != Priorities.FULL:
            return True, False, "" # This is not an error
        
        order = AvailableSlot(
            game_date=registration.game_date,
            seller_user_name=player.user_name,
            requested_at=int(time.time()),
            tikkie_link=payment_link,
            is_sent=0,
            buyer_user_name="empty"
            )
        
        _, err = self.db.create(order)
        if err:
            self.log.info(f"leave_game: cannot sell slot: {err}")
            return True, False, "try again later"
    
        return True, True, ""


    def _move_to_waiting_list(self, r: Registration):
        self.log.info(f"Moving {r.user_name} to a waiting list")


    def _update_balance(self, p: Player) -> tuple[bool, str]:
        self.log.info(f"Updating balance of {p.user_name}. Current balance {p.balance}")
        if p.balance <= 0:
            return False, "" # Nothing to update
        p.balance = p.balance -1
        _, err = self.db.update(p)
        if err:
            self.log.info(f"update_balance: cannot query db: {err}")
            return False, "try again later"
        return True, ""

    def collect_money(self, p: Player, r: Registration) -> tuple[AvailableSlot| None, str]:
        """Given Player and its registration
        If Player balance > 0 updates balance
        Otherwise tries to find a slot from auction
        Then sent tikkie link back
        In case no slots are available admin link is sent
        """
        # TODO: This is a VERY HEAVY query, need to optimize
        admin_tikkie = "https://make-me-rich"
        
        updated, err = self._update_balance(p)
        if err:
            self.log.info(f"collect_money: cannot update balance: {err}")
            return None, "try again later"
        # We need to add a record just for the sake of it
        if updated:
            # Send admin link
            slot = AvailableSlot(
                game_date=r.game_date,
                seller_user_name="admin",
                tikkie_link="don't need to pay",
                is_sent=1,
                buyer_user_name=p.user_name,
                requested_at=int(time.time())
            )

            _, err = self.db.create(slot)
            if err:
                self.log.info(f"collect_money: cannot write auction: {err}")
                return None, "try again later" 
            return slot, ""            

        # Now we need to process remaining players (with balance = 0)
        available_slots, err = self.db.read_table("auctions", r.game_date)
        if err:
            self.log.info(f"collect_money: cannot read auction: {err}")
            return None, "try again later"
        # The topmost slot that was not yet processed
        slots = sorted(                                      
            (x for x in available_slots if x.is_sent == 0),  # Filter before sorting
            key=lambda x: x.requested_at                     # Sort by requested_at
        )
        # If we found some slots use it
        if slots:
            slot = slots[0]
            slot.buyer_user_name = p.user_name
        # If there are no slots to buy, send admin link
        else:
            # Send admin link
            slot = AvailableSlot(
                game_date=r.game_date,
                seller_user_name="admin",
                tikkie_link="pay to " + admin_tikkie,
                is_sent=1,
                buyer_user_name=p.user_name,
                requested_at=int(time.time())
            )
            # TODO: Fix db.update
            _, err = self.db.create(slot)
            if err:
                self.log.info(f"collect_money: cannot write auction: {err}")
                return None, "try again later" 
            return slot, ""
        # Update DB
        # TODO: Fix db.update
        slot.is_sent = 1
        _, err = self.db.delete(slot)
        if err:
            self.log.info(f"collect_money: cannot write auction: {err}")
            return None, "try again later"
        _, err = self.db.create(slot)
        if err:
            self.log.info(f"collect_money: cannot write auction: {err}")
            return None, "try again later" 
        return slot, ""