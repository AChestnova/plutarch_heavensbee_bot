from spreadsheet_helper import Player, Game, Registration, AvailableSlot

class Database():

    def __init__(self):
        # Required
        self.players: list[Player] = []
        # Optionals
        self.games: list[Game] = []
        self.registrations: list[Registration] = []
        self.auction: list[AvailableSlot] = []
        self._add_players

    def _add_players(self):

        # Add Full members
        for i in range(5):
            p = Player(
                name = "player_" + str(i),
                balance = 60,
                can_sell = True,
                prio = 1,
            )
            self.players.append(p)
        # Add Semi members
        for i in range(5,15):
            p = Player(
                name = "player_" + str(i),
                balance = 14,
                can_sell = False,
                prio = 2,
            )
            self.players.append(p)
        # Add One-time-pass members
        for i in range(15,40):
            p = Player(
                name = "player_" + str(i),
                balance = 14,
                can_sell = False,
                prio = 2,
            )
            self.players.append(p)
    
    def get(self, table str, filter str):
        return

    def add(self, data):
        if isinstance(data, Player):
            self.players.append(Player)
        if isinstance(data, Game):
            self.games.append(Game)
        if isinstance(data, Registration):
            self.registrations.append(Registration)
        if isinstance(data, AvailableSlot):
            self.auction.append(AvailableSlot)
    
    def exists(self, data):
        if isinstance(data, Player):
            return Player in self.players
        if isinstance(data, Game):
            return Game in self.games
        if isinstance(data, Registration):
            return Registration in self.registrations
        if isinstance(data, AvailableSlot):
            return AvailableSlot in self.auction