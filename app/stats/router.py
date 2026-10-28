from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.games.models import Game
from app.users.models import User
from app.users.router import get_current_user


router = APIRouter(prefix="/stats", tags=["Stats"])


class UserStats(BaseModel):
    nickname: str
    wins: int
    losses: int
    total_games: int


@router.get("/me", response_model=UserStats)
def get_my_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserStats:
    games = db.query(Game).filter(
        or_(
            Game.player_1_id == current_user.id,
            Game.player_2_id == current_user.id,
        )
    ).all()

    wins = sum(
        1 for game in games
        if game.winner_id == current_user.id
    )

    losses = sum(
        1 for game in games
        if game.winner_id is not None
        and game.winner_id != current_user.id
    )

    return UserStats(
        nickname=current_user.nickname,
        wins=wins,
        losses=losses,
        total_games=wins + losses,
    )