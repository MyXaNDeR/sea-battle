from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.games.service import (
    create_ai_game,
    create_pvp_game,
    get_game,
    get_pvp_game,
    join_pvp_game,
    make_player_shot,
    make_pvp_shot,
    serialize_board,
)
from app.users.models import User
from app.users.router import get_current_web_user


router = APIRouter(prefix="/games", tags=["Games"])


class Shot(BaseModel):
    row: int = Field(ge=0, le=9)
    col: int = Field(ge=0, le=9)


@router.post("/ai")
def start_ai_game(
    current_user: User = Depends(get_current_web_user),
    db: Session = Depends(get_db),
):
    game_id = create_ai_game(current_user.id, db)

    return {"game_id": game_id}


@router.get("/ai/{game_id}")
def get_ai_game(
    game_id: str,
    current_user: User = Depends(get_current_web_user),
):
    game = get_game(game_id, current_user.id)

    if game is None:
        raise HTTPException(status_code=404, detail="Игра не найдена")

    return {
        "game_id": game_id,
        "your_board": serialize_board(
            game["human"].board,
            hide_ships=False,
        ),
        "enemy_board": serialize_board(
            game["computer"].board,
            hide_ships=True,
        ),
        "is_finished": game["is_finished"],
        "winner": game["winner"],
    }


@router.post("/ai/{game_id}/shot")
def make_ai_shot(
    game_id: str,
    shot: Shot,
    current_user: User = Depends(get_current_web_user),
    db: Session = Depends(get_db),
):
    game = get_game(game_id, current_user.id)

    if game is None:
        raise HTTPException(status_code=404, detail="Игра не найдена")

    if game["is_finished"]:
        raise HTTPException(status_code=400, detail="Игра уже завершена")

    result = make_player_shot(game, shot.row, shot.col, db)

    return {
        "game_id": game_id,
        "your_board": serialize_board(
            game["human"].board,
            hide_ships=False,
        ),
        "enemy_board": serialize_board(
            game["computer"].board,
            hide_ships=True,
        ),
        **result,
    }


@router.post("/pvp")
def start_pvp_game(
    current_user: User = Depends(get_current_web_user),
    db: Session = Depends(get_db),
):
    game_id = create_pvp_game(current_user.id, db)

    return {"game_id": game_id}


@router.post("/pvp/{game_id}/join")
def join_pvp_game_route(
    game_id: str,
    current_user: User = Depends(get_current_web_user),
    db: Session = Depends(get_db),
):
    joined = join_pvp_game(game_id, current_user.id, db)

    if not joined:
        raise HTTPException(
            status_code=400,
            detail="Не удалось присоединиться к игре",
        )

    return {"game_id": game_id}


@router.get("/pvp/{game_id}")
def get_pvp_game_state(
    game_id: str,
    current_user: User = Depends(get_current_web_user),
):
    game = get_pvp_game(game_id, current_user.id)

    if game is None:
        raise HTTPException(status_code=404, detail="Игра не найдена")

    if current_user.id == game["player_1_id"]:
        your_board = game["player_1"].board
        enemy_board = game["player_2"].board
    else:
        your_board = game["player_2"].board
        enemy_board = game["player_1"].board

    return {
        "game_id": game_id,
        "your_board": serialize_board(your_board, hide_ships=False),
        "enemy_board": serialize_board(enemy_board, hide_ships=True),
        "your_turn": game["current_player_id"] == current_user.id,
        "is_finished": game["is_finished"],
        "winner_id": game["winner_id"],
    }


@router.post("/pvp/{game_id}/shot")
def make_pvp_shot_route(
    game_id: str,
    shot: Shot,
    current_user: User = Depends(get_current_web_user),
    db: Session = Depends(get_db),
):
    game = get_pvp_game(game_id, current_user.id)

    if game is None:
        raise HTTPException(status_code=404, detail="Игра не найдена")

    result = make_pvp_shot(
        game=game,
        user_id=current_user.id,
        row=shot.row,
        col=shot.col,
        db=db,
    )

    if "error" in result:
        raise HTTPException(
            status_code=400,
            detail=result["error"],
        )

    if current_user.id == game["player_1_id"]:
        your_board = game["player_1"].board
        enemy_board = game["player_2"].board
    else:
        your_board = game["player_2"].board
        enemy_board = game["player_1"].board

    return {
        "game_id": game_id,
        "your_board": serialize_board(your_board, hide_ships=False),
        "enemy_board": serialize_board(enemy_board, hide_ships=True),
        "your_turn": game["current_player_id"] == current_user.id,
        "is_finished": game["is_finished"],
        "winner_id": game["winner_id"],
        "result": result["result"],
    }