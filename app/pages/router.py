from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.games.models import Game
from app.users.models import User
from app.users.security import hash_password, verify_password


router = APIRouter(tags=["Pages"])

templates = Jinja2Templates(directory="templates")


@router.get("/")
def index(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
    )


@router.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="register.html",
        context={"error": None},
    )


@router.post("/register")
def register(
    request: Request,
    email: str = Form(...),
    nickname: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    if len(password.encode("utf-8")) > 72:
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={
                "error": "Пароль слишком длинный: максимум 72 байта"
            },
        )

    email_exists = db.query(User).filter(
        User.email == email
    ).first()

    if email_exists:
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={"error": "Этот email уже зарегистрирован"},
        )

    nickname_exists = db.query(User).filter(
        User.nickname == nickname
    ).first()

    if nickname_exists:
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={"error": "Этот никнейм уже занят"},
        )

    user = User(
        email=email,
        nickname=nickname,
        hashed_password=hash_password(password),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return RedirectResponse(url="/login", status_code=303)


@router.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"error": None},
    )


@router.post("/login")
def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(
        User.email == email
    ).first()

    if user is None or not verify_password(
        password,
        user.hashed_password,
    ):
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={"error": "Неверный email или пароль"},
        )

    response = RedirectResponse(url="/profile", status_code=303)

    response.set_cookie(
        key="user_id",
        value=str(user.id),
        httponly=True,
        max_age=60 * 60 * 24,
    )

    return response

@router.get("/play")
def play_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="play.html",
    )

@router.get("/profile")
def profile(
    request: Request,
    db: Session = Depends(get_db),
):
    user_id = request.cookies.get("user_id")

    if user_id is None:
        return RedirectResponse(url="/login", status_code=303)

    user = db.get(User, int(user_id))

    if user is None:
        return RedirectResponse(url="/login", status_code=303)

    games = db.query(Game).filter(
        or_(
            Game.player_1_id == user.id,
            Game.player_2_id == user.id,
        )
    ).all()

    wins = sum(
        1 for game in games
        if game.winner_id == user.id
    )

    losses = sum(
        1 for game in games
        if game.winner_id is not None
        and game.winner_id != user.id
    )

    return templates.TemplateResponse(
        request=request,
        name="profile.html",
        context={
            "user": user,
            "wins": wins,
            "losses": losses,
            "total_games": wins + losses,
        },
    )

@router.get("/play-pvp")
def play_pvp_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="play_pvp.html",
    )