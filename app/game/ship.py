from dataclasses import dataclass


@dataclass
class Ship:
    start_row: int
    start_col: int
    size: int
    is_horizontal: bool

    @property
    def cells(self) -> list[tuple[int, int]]:
        if self.is_horizontal:
            return [
                (self.start_row, self.start_col + i)
                for i in range(self.size)
            ]
        return [
            (self.start_row + i, self.start_col)
            for i in range(self.size)
        ]

    @property
    def is_sunk(self) -> bool:
        return all(self.hits[cell] for cell in self.cells)

    def __post_init__(self) -> None:
        self.hits: dict[tuple[int, int], bool] = {
            cell: False for cell in self.cells
        }

    def receive_hit(self, row: int, col: int) -> bool:
        if (row, col) not in self.hits:
            return False

        self.hits[(row, col)] = True
        return True