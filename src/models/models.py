
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
    name: Optional[str] = ""
    balance: Optional[int] = 0
    can_sell: Optional[bool] = False
    prio: Optional[int] = Prio.ONETIME

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
    game_date: datetime.date
    seller_user_name: str
    tikkie_link: str
    requested_at: int
    is_sent: Optional[bool] = False
    buyer_user_name: Optional[str] = None