
from dataclasses import dataclass

from enum import Enum

# class syntax
class Prio(Enum):
    FULL = 1
    HALF = 2
    ONETIME = 3

@dataclass
class Player:
    user_name: str
    name: str|None = None 
    balance: int|None = None
    can_sell: bool|None = None
    prio: int|None = None

@dataclass
class Game:
    game_date: str
    cap: int|None = None
    price: int|None = None
    is_summarized: bool|None = None

@dataclass
class Registration:
    game_date: str
    user_name: str
    requested_at: int|None = None
    prio: int|None = None

@dataclass
class AvailableSlot:
    game_date: str
    seller_user_name: str
    requested_at: int|None = None
    tikkie_link: str|None = None 
    is_sent: bool|None = None 
    buyer_user_name: str|None = None 