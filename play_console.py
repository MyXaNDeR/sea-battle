import random

from app.game.ai import AIPlayer
from app.game.game import Game
from app.game.input_utils import parse_coordinate
from app.game.models import Player
from app.game.render import render_board
from app.game.setup import random_place_ships


RESULT_MESSAGES = {
    "miss": "Мимо!",
    "hit": "Попадание!",
    "sunk": "Убил!",
    "already_shot": "В эту клетку уже стреляли.",
    "invalid": "Некорректная клетка.",
}


def print_boards(player: Player, opponent: Player) -> None:
    print(f"\nПоле игрока: {player.nickname}")
    print(render_board(player.board, hide_ships=False))

    print(f"\nПоле соперника: {opponent.nickname}")
    print(render_board(opponent.board, hide_ships=True))


def get_player_shot(board_size: int) -> tuple[int, int]:
    while True:
        text = input("Твой выстрел (например, A5): ")
        coordinate = parse_coordinate(text, board_size)

        if coordinate is None:
            print("Неверный формат. Пример: A5")
            continue

        return coordinate


def create_players(mode: str) -> tuple[Player, Player]:
    if mode == "1":
        return Player("Игрок"), Player("Компьютер")

    first_name = input("Никнейм первого игрока: ").strip() or "Игрок 1"
    second_name = input("Никнейм второго игрока: ").strip() or "Игрок 2"

    return Player(first_name), Player(second_name)


def play_human_turn(game: Game) -> None:
    current = game.current_player
    opponent = game.opponent

    print(f"\nХод игрока: {current.nickname}")
    print_boards(current, opponent)

    while True:
        row, col = get_player_shot(current.board.size)
        result = game.make_shot(row, col)

        print(f"\nРезультат: {RESULT_MESSAGES[result]}")

        if result != "already_shot" and result != "invalid":
            break


def play_ai_turn(game: Game, ai: AIPlayer) -> None:
    human = game.opponent

    input(f"\nХод компьютера. Нажми Enter...")

    shot = ai.choose_shot()
    result = game.make_shot(shot[0], shot[1])
    ai.register_result(shot, result, human.board)

    shot_name = f"{chr(ord('A') + shot[1])}{shot[0] + 1}"
    print(f"\nКомпьютер выстрелил в {shot_name}: {RESULT_MESSAGES[result]}")


def play_game(mode: str) -> None:
    player_1, player_2 = create_players(mode)

    random_place_ships(player_1.board)
    random_place_ships(player_2.board)

    game = Game(player_1, player_2)
    ai = AIPlayer(board_size=player_1.board.size)

    print("\nКорабли расставлены. Начинаем игру!")

    while not game.is_finished:
        if game.current_player is player_2 and mode == "1":
            play_ai_turn(game, ai)
        else:
            play_human_turn(game)

        if game.is_finished:
            break

        print("\n" + "-" * 40)

    print("\nИгра окончена!")

    if game.winner is None:
        print("Победитель не определён.")
    else:
        print(f"Победитель: {game.winner.nickname}!")


def show_menu() -> str:
    print("\n=== МОРСКОЙ БОЙ ===")
    print("1 — Играть против компьютера")
    print("2 — Играть против другого игрока")
    print("0 — Выйти")

    while True:
        choice = input("Выбери режим: ").strip()

        if choice in ("0", "1", "2"):
            return choice

        print("Введите 0, 1 или 2.")


def main() -> None:
    while True:
        mode = show_menu()

        if mode == "0":
            print("Спасибо за игру!")
            break

        play_game(mode)


if __name__ == "__main__":
    main()