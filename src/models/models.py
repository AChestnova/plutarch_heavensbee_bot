
import time
import datetime
from dataclasses import dataclass
from typing import Optional

from enum import Enum

# class syntax
class Prio(Enum):
    FULL = 1
    HALF = 2
    ONETIME = 3

@dataclass
class Player:
    user_name: str
    name: Optional[str]
    balance: Optional[int] = 0
    can_sell: Optional[bool] = False
    prio: Optional[int] = Prio.ONETIME

@dataclass
class Game:
    game_date: str
    cap: Optional[int]
    price: Optional[int]
    is_summarized: Optional[bool] = False

@dataclass
class Registration:
    game_date: str
    user_name: str
    requested_at: Optional[int] 
    prio: Optional[int]

@dataclass
class AvailableSlot:
    game_date: str
    seller_user_name: str
    requested_at: Optional[int]
    tikkie_link: Optional[str]
    is_sent: Optional[bool]
    buyer_user_name: Optional[str]