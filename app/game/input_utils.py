BOARD_LETTERS = "ABCDEFGHIJ"


def parse_coordinate(text: str, board_size: int = 10) -> tuple[int, int] | None:
    text = text.strip().upper()

    if len(text) < 2:
        return None

    letter = text[0]

    if letter not in BOARD_LETTERS:
        return None

    number_part = text[1:]

    if not number_part.isdigit():
        return None

    col = ord(letter) - ord("A")
    row = int(number_part) - 1

    if not (0 <= row < board_size and 0 <= col < board_size):
        return None

    return row, col