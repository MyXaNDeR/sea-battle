from .ship import Ship


class Board:
    def __init__(self, size: int = 10) -> None:
        self.size = size
        self.ships: list[Ship] = []
        self.shots: set[tuple[int, int]] = set()

    def can_place_ship(self, ship: Ship) -> bool:
        for row, col in ship.cells:
            if not self._is_inside(row, col):
                return False

            if self._has_neighbor_ship(row, col):
                return False

        return True

    def place_ship(self, ship: Ship) -> bool:
        if not self.can_place_ship(ship):
            return False

        self.ships.append(ship)
        return True

    def receive_shot(self, row: int, col: int) -> str:
        if not self._is_inside(row, col):
            return "invalid"

        if (row, col) in self.shots:
            return "already_shot"

        self.shots.add((row, col))

        for ship in self.ships:
            if ship.receive_hit(row, col):
                if ship.is_sunk:
                    return "sunk"
                return "hit"

        return "miss"

    def all_ships_sunk(self) -> bool:
        return all(ship.is_sunk for ship in self.ships)

    def _is_inside(self, row: int, col: int) -> bool:
        return 0 <= row < self.size and 0 <= col < self.size

    def _has_neighbor_ship(self, row: int, col: int) -> bool:
        for ship in self.ships:
            for ship_row, ship_col in ship.cells:
                if abs(row - ship_row) <= 1 and abs(col - ship_col) <= 1:
                    return True

        return False