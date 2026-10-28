from .board import Board


class Player:
    def __init__(self, nickname: str) -> None:
        self.nickname = nickname
        self.board = Board()