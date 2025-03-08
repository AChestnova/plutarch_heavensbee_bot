"""
Set of functions to manipulate Goodgle spreadsheet
"""
import time
import datetime
from dataclasses import dataclass
from typing import Optional

@dataclass
class Player:
    user_name: str
    name: Optional[str] = ""
    balance: Optional[int] = 0
    can_sell: Optional[bool] = False
    prio: Optional[int] = 2

@dataclass
class Game:
    game_date: datetime.date
    cap: Optional[int] = 14
    price: Optional[int] = 11
    is_summarized: Optional[bool] = False

@dataclass
class Registration:
    requested_at: int
    game_date: datetime.date
    user_name: str
    prio: int

@dataclass
class AvailableSlot:
    requested_at: int
    game_date: time
    user_name: str
    prio: int
    
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