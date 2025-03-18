
from dataclasses import dataclass, fields
from typing import Protocol
from enum import IntEnum, StrEnum

class Priorities(IntEnum):
    FULL = 1
    HALF = 2
    ONE_TIME = 3

class BotStorage(StrEnum):
    USER_ID = "user_id"
    REGISTRATIONS = "registrations"
    REGISTRATION_DATES = "registration_dates"
    UPCOMING_GAME_DATES = "upcoming_game_dates"
    PLAYER = "player"

@dataclass
class Storable(Protocol):  # Optional: Define a protocol for type safety

    @classmethod
    def sheet_name(cls) -> str:
        raise NotImplementedError

    @property
    def unique_keys(self) -> tuple[str, str]:
        raise NotImplementedError
    
    # TODO: Implement it here and remove from Child classes
    @classmethod
    def from_list(cls, data: list[str]):
        raise NotImplementedError
    
@dataclass
class Player(Storable):
    user_name: str
    name: str|None = None 
    balance: int|None = None
    can_sell: int|None = None
    prio: int|None = None

    @classmethod
    def sheet_name(cls) -> str:
        """Returns key attributes used for searching."""
        return "players"

    @property
    def unique_keys(self) -> tuple[str, str]:
        """Returns key attributes used for searching."""
        return self.user_name, ""
    
    def __iter__(self):
        return iter((self.user_name, self.name, self.balance, self.can_sell, self.prio))

    @classmethod
    def from_list(cls, data: list[str]):
        """Parses and converts a list of strings into a Game instance."""
        
        # TODO: need to figure a way to grab real amount of fields and do not hardcore them
        if len(data) != len(fields(cls)): 
            raise ValueError(f"Expected exactly {len(fields(cls))} values")
        
        user_name, name, balance, can_sell, prio = data                 # Unpack strings
        return cls(user_name, name, int(balance), int(can_sell), int(prio))  # Convert fields    


@dataclass
class Game(Storable):
    game_date: str
    cap: int|None = None
    price: int|None = None
    is_summarized: int|None = None

    @classmethod
    def sheet_name(cls) -> str:
        """Returns key attributes used for searching."""
        return "games"

    @property
    def unique_keys(self) -> tuple[str, str]:
        """Returns key attributes used for searching."""
        return self.game_date, ""
    
    def __iter__(self):
        return iter((self.game_date, self.cap, self.price, self.is_summarized))

    @classmethod
    def from_list(cls, data: list[str]):
        """Parses and converts a list of strings into a Game instance."""
        
        if len(data) != len(fields(cls)): 
            raise ValueError(f"Expected exactly {len(fields(cls))} values")
        
        game_date, cap, price, is_summarized = data                         # Unpack strings
        return cls(game_date, int(cap), int(price), int(is_summarized))     # Convert fields    


@dataclass
class Registration(Storable):
    game_date: str
    requested_at: int|None = None
    user_name: str|None = None
    prio: int|None = None

    @classmethod
    def sheet_name(cls) -> str:
        """Returns key attributes used for searching."""
        return "registrations"

    #TODO: need to add some logic here
    # This is not unique
    @property
    def unique_keys(self) -> tuple[str, str]:
        """Returns key attributes used for searching."""
        return self.game_date, self.user_name
    
    def __iter__(self):
        return iter((self.game_date, self.requested_at, self.user_name, self.prio))

    @classmethod
    def from_list(cls, data: list[str]):
        """Parses and converts a list of strings into a Game instance."""
        
        if len(data) != len(fields(cls)): 
            raise ValueError(f"Expected exactly {len(fields(cls))} values")
        
        game_date, requested_at, user_name, prio = data                         # Unpack strings
        return cls(game_date, int(requested_at), user_name, int(prio))     # Convert fields    

@dataclass
class AvailableSlot(Storable):
    game_date: str
    seller_user_name: str
    requested_at: int|None = None
    tikkie_link: str|None = None 
    is_sent: int|None = None 
    buyer_user_name: str|None = None

    @classmethod
    def sheet_name(cls) -> str:
        """Returns key attributes used for searching."""
        return "auctions"

    #TODO: need to add some logic here
    # This is not unique
    @property
    def unique_keys(self) -> tuple[str, str]:
        """Returns key attributes used for searching."""
        return self.game_date, self.seller_user_name
    
    def __iter__(self):
        return iter((self.game_date, self.seller_user_name, self.requested_at, self.tikkie_link, self.is_sent, self.buyer_user_name))
    
    @classmethod
    def from_list(cls, data: list[str]):
        """Parses and converts a list of strings into a Game instance."""
        
        if len(data) != len(fields(cls)): 
            raise ValueError(f"Expected exactly {len(fields(cls))} values")
        
        game_date, seller_user_name, requested_at, tikkie_link, is_sent, buyer_user_name = data                    # Unpack strings
        return cls(game_date, seller_user_name, int(requested_at), tikkie_link, int(is_sent), buyer_user_name)     # Convert fields    