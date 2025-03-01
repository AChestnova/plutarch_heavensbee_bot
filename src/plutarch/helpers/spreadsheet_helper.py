"""
Set of functions to manipulate Goodgle spreadsheet
"""
from dataclasses import dataclass
from datetime import time


@dataclass
class Player:
    user_name: str
    name: str
    balance: int
    can_sell: bool
    prio: int

@dataclass
class Game:
    game_date: time
    capacity: int
    price_per_player: int
    is_summarized: bool

@dataclass
class Registration:
    user_name: str
    game_date: time
    requested_at: time
    prio: int

@dataclass
class AvailableSlot:
    game_date: time
    requested_at: time
    user_name: str
    prio: int


class Database():
    pass

class SpreadsheetHelper:
    """Set of functions to manipulate Goodgle spreadsheet"""
    @staticmethod
    def check_tests(message: str) -> str:
        """
        Check if a tests are working
        
        :param message: Any string
        :return: str Same as input
        """
        return message