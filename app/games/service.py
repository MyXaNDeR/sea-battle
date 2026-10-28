import random
import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.game.ai import AIPlayer
from app.game.board import Board
from app.game.models import Player
from app.game.setup import random_place_ships
from app.games.models import Game


games: dict[str, dict] = {}
pvp_games: dict[str, dict] = {}


def create_ai_game(user_id: int, db: Session) -> str:
    game_id = str(uuid.uuid4())

    human = Player("Игрок")
    computer = Player("Компьютер")

    random_place_ships(human.board)
    random_place_ships(computer.board)

    db_game = Game(
        player_1_id=user_id,
        player_2_id=None,
        winner_id=None,
        mode="ai",
    )

    db.add(db_game)
    db.commit()
    db.refresh(db_game)

    games[game_id] = {
        "user_id": user_id,
        "human": human,
        "computer": computer,
        "ai": AIPlayer(board_size=human.board.size),
        "is_finished": False,
        "winner": None,
        "db_game_id": db_game.id,
    }

    return game_id


def get_game(game_id: str, user_id: int) -> dict | None:
    game = games.get(game_id)

    if game is None or game["user_id"] != user_id:
        return None

    return game


def make_player_shot(
    game: dict,
    row: int,
    col: int,
    db: Session,
) -> dict:
    computer_board = game["computer"].board

    result = computer_board.receive_shot(row, col)

    response = {
        "player_result": result,
        "ai_shot": None,
        "ai_result": None,
        "is_finished": False,
        "winner": None,
    }

    if computer_board.all_ships_sunk():
        game["is_finished"] = True
        game["winner"] = "human"

        finish_game(
            db=db,
            game=game,
            winner_id=game["user_id"],
        )

        response["is_finished"] = True
        response["winner"] = "human"

        return response

    if result == "miss":
        ai = game["ai"]
        human_board = game["human"].board

        ai_shot = ai.choose_shot()
        ai_result = human_board.receive_shot(ai_shot[0], ai_shot[1])

        ai.register_result(
            shot=ai_shot,
            result=ai_result,
            opponent_board=human_board,
        )

        response["ai_shot"] = ai_shot
        response["ai_result"] = ai_result

        if human_board.all_ships_sunk():
            game["is_finished"] = True
            game["winner"] = "computer"

            finish_game(
                db=db,
                game=game,
                winner_id=None,
            )

            response["is_finished"] = True
            response["winner"] = "computer"

    return response


def finish_game(
    db: Session,
    game: dict,
    winner_id: int | None,
) -> None:
    db_game = db.get(Game, game["db_game_id"])

    if db_game is None:
        return

    db_game.winner_id = winner_id
    db_game.finished_at = datetime.now(timezone.utc)

    db.commit()


def serialize_board(
    board: Board,
    hide_ships: bool,
) -> list[list[str]]:
    result = []

    for row in range(board.size):
        board_row = []

        for col in range(board.size):
            board_row.append(
                get_cell_state(
                    board=board,
                    row=row,
                    col=col,
                    hide_ships=hide_ships,
                )
            )

        result.append(board_row)

    return result


def get_cell_state(
    board: Board,
    row: int,
    col: int,
    hide_ships: bool,
) -> str:
    if (row, col) in board.shots:
        for ship in board.ships:
            if (row, col) in ship.hits:
                return "hit"

        return "miss"

    if not hide_ships:
        for ship in board.ships:
            if (row, col) in ship.cells:
                return "ship"

    return "empty"


def create_pvp_game(user_id: int, db: Session) -> str:
    game_id = str(uuid.uuid4())[:8].upper()

    player_1 = Player("Игрок 1")
    player_2 = Player("Игрок 2")

    random_place_ships(player_1.board)
    random_place_ships(player_2.board)

    db_game = Game(
        player_1_id=user_id,
        player_2_id=None,
        winner_id=None,
        mode="pvp",
    )

    db.add(db_game)
    db.commit()
    db.refresh(db_game)

    pvp_games[game_id] = {
        "db_game_id": db_game.id,
        "player_1_id": user_id,
        "player_2_id": None,
        "player_1": player_1,
        "player_2": player_2,
        "current_player_id": user_id,
        "is_finished": False,
        "winner_id": None,
    }

    return game_id


def join_pvp_game(
    game_id: str,
    user_id: int,
    db: Session,
) -> bool:
    game = pvp_games.get(game_id)

    if game is None:
        return False

    if game["player_1_id"] == user_id:
        return True

    if game["player_2_id"] is None:
        game["player_2_id"] = user_id

        db_game = db.get(Game, game["db_game_id"])

        if db_game is None:
            return False

        db_game.player_2_id = user_id
        db.commit()

        return True

    return game["player_2_id"] == user_id


def get_pvp_game(game_id: str, user_id: int) -> dict | None:
    game = pvp_games.get(game_id)

    if game is None:
        return None

    if user_id not in (game["player_1_id"], game["player_2_id"]):
        return None

    return game


def make_pvp_shot(
    game: dict,
    user_id: int,
    row: int,
    col: int,
    db: Session,
) -> dict:
    if game["is_finished"]:
        return {
            "error": "Игра уже завершена",
        }

    if game["current_player_id"] != user_id:
        return {
            "error": "Сейчас ход другого игрока",
        }

    if user_id == game["player_1_id"]:
        opponent_board = game["player_2"].board
        opponent_id = game["player_2_id"]
    else:
        opponent_board = game["player_1"].board
        opponent_id = game["player_1_id"]

    result = opponent_board.receive_shot(row, col)

    if result == "miss":
        game["current_player_id"] = opponent_id

    response = {
        "result": result,
        "is_finished": False,
        "winner_id": None,
    }

    if opponent_board.all_ships_sunk():
        game["is_finished"] = True
        game["winner_id"] = user_id

        db_game = db.get(Game, game["db_game_id"])

        if db_game is not None:
            db_game.winner_id = user_id
            db_game.finished_at = datetime.now(timezone.utc)
            db.commit()

        response["is_finished"] = True
        response["winner_id"] = user_id

    return response