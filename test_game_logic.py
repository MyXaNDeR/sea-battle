import random

from app.game.ai import AIPlayer
from app.game.models import Player
from app.game.setup import random_place_ships


random.seed(42)

player_1 = Player("XaNDeR")
player_2 = Player("AI")

random_place_ships(player_1.board)
random_place_ships(player_2.board)

ai = AIPlayer(board_size=player_1.board.size)
shots = 0

while not player_1.board.all_ships_sunk() and shots < 200:
    shot = ai.choose_shot()
    result = player_1.board.receive_shot(shot[0], shot[1])
    ai.register_result(shot, result, player_1.board)
    shots += 1

    print(f"Выстрел {shot}: {result}")

print(f"ИИ сделал выстрелов: {shots}")
print(f"Все корабли player_1 потоплены: {player_1.board.all_ships_sunk()}")