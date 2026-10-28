import random

from .board import Board
from .ship import Ship


SHIP_SIZES = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]


def random_place_ships(
    board: Board,
    ship_sizes: list[int] | None = None,
    max_attempts: int = 1000,
) -> None:
    if ship_sizes is None:
        ship_sizes = SHIP_SIZES.copy()

    for size in ship_sizes:
        placed = False

        for _ in range(max_attempts):
            is_horizontal = random.choice([True, False])

            if is_horizontal:
                row = random.randint(0, board.size - 1)
                col = random.randint(0, board.size - size)
            else:
                row = random.randint(0, board.size - size)
                col = random.randint(0, board.size - 1)

            ship = Ship(
                start_row=row,
                start_col=col,
                size=size,
                is_horizontal=is_horizontal,
            )

            if board.place_ship(ship):
                placed = True
                break

        if not placed:
            raise RuntimeError(
                f"Не удалось разместить корабль размером {size}"
            )