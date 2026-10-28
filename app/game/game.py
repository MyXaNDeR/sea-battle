from .models import Player


class Game:
    def __init__(self, player_1: Player, player_2: Player) -> None:
        self.players = [player_1, player_2]
        self.current_player_index = 0
        self.winner: Player | None = None
        self.is_finished = False

    @property
    def current_player(self) -> Player:
        return self.players[self.current_player_index]

    @property
    def opponent(self) -> Player:
        return self.players[1 - self.current_player_index]

    def make_shot(self, row: int, col: int) -> str:
        if self.is_finished:
            return "game_over"

        result = self.opponent.board.receive_shot(row, col)

        if result == "miss":
            self._switch_turn()

        if self.opponent.board.all_ships_sunk():
            self.winner = self.current_player
            self.is_finished = True

        return result

    def _switch_turn(self) -> None:
        self.current_player_index = 1 - self.current_player_index