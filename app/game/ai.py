import random

from .board import Board


class AIPlayer:
    def __init__(self, board_size: int = 10) -> None:
        self.size = board_size
        self.available_cells = {
            (row, col)
            for row in range(board_size)
            for col in range(board_size)
        }
        self.target_cells: list[tuple[int, int]] = []

    def choose_shot(self) -> tuple[int, int]:
        if self.target_cells:
            return self.target_cells.pop()

        return random.choice(list(self.available_cells))

    def register_result(
        self,
        shot: tuple[int, int],
        result: str,
        opponent_board: Board,
    ) -> None:
        row, col = shot
        self.available_cells.discard(shot)

        if result in ("hit", "sunk"):
            self._add_neighbors(row, col)

        if result == "sunk":
            self._remove_cells_near_sunk_ships(opponent_board)

    def _add_neighbors(self, row: int, col: int) -> None:
        neighbors = [
            (row + 1, col),
            (row - 1, col),
            (row, col + 1),
            (row, col - 1),
        ]

        for cell in neighbors:
            if cell in self.available_cells:
                self.target_cells.append(cell)

    def _remove_cells_near_sunk_ships(
        self,
        opponent_board: Board,
    ) -> None:
        sunk_cells = []

        for ship in opponent_board.ships:
            if ship.is_sunk:
                sunk_cells.extend(ship.cells)

        self.target_cells = [
            cell
            for cell in self.target_cells
            if not self._is_near_any_cell(cell, sunk_cells)
        ]

    @staticmethod
    def _is_near_any_cell(
        cell: tuple[int, int],
        other_cells: list[tuple[int, int]],
    ) -> bool:
        row, col = cell

        for other_row, other_col in other_cells:
            if abs(row - other_row) <= 1 and abs(col - other_col) <= 1:
                return True

        return False