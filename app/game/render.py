from .board import Board


LETTERS = "ABCDEFGHIJ"


def render_board(board: Board, hide_ships: bool = True) -> str:
    lines = ["   " + " ".join(LETTERS)]

    for row in range(board.size):
        cells = []

        for col in range(board.size):
            cells.append(
                _get_cell_symbol(board, row, col, hide_ships)
            )

        lines.append(f"{row + 1:2} " + " ".join(cells))

    return "\n".join(lines)


def _get_cell_symbol(
    board: Board,
    row: int,
    col: int,
    hide_ships: bool,
) -> str:
    if (row, col) in board.shots:
        for ship in board.ships:
            if (row, col) in ship.hits:
                return "X"

        return "O"

    if not hide_ships:
        for ship in board.ships:
            if (row, col) in ship.cells:
                return "■"

    return "."