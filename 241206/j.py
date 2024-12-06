from __future__ import annotations

from io import TextIOBase


DIRS = [(0, -1), (1, 0), (0, 1), (-1, 0)]


def load(src: TextIOBase) -> Game:
    result = Game()
    result.board = Board()
    for y, line in enumerate(src):
        load_line(y, line, result)
    result.board.height = y + 1
    return result


def load_line(y: int, line: str, game: Game) -> None:
    line = line.split('\n')[0]
    game.board.width = len(line)
    tiles = []
    for x, char in enumerate(line):
        if char == '^':
            game.guard = Guard(game.board, (x, y))
        tiles.append(char == '#')
    game.board.tiles.extend(tiles)


def test_load() -> None:
    with open('test.txt', 'r') as f:
        game = load(f)
    assert game.board.width == 10
    assert game.board.height == 10
    assert game.guard.pos == (4, 6)


class Game:
    def __init__(self):
        self.guard = None
        self.board = None


class Board:
    def __init__(self):
        self.width = None
        self.height = None
        self.tiles = []

    def __contains__(self, pos: tuple[int, int]) -> bool:
        x, y = pos
        if not 0 <= x < self.width:
            return False
        return 0 <= y < self.height

    def __getitem__(self, pos: tuple[int, int]) -> str | None:
        if pos not in self:
            return None
        x, y = pos
        return '#' if self.tiles[x + y * self.width] else '.'


def test_sample_board() -> None:
    with open('test.txt') as f:
        game = load(f)
    assert game.board[2, 3] == '#'
    assert game.board[3, 3] == '.'
    assert not game.board[10, 2]


class Guard:
    def __init__(self, board: Board, pos: tuple[int, int]):
        self.pos = pos
        self.dir = 0
        self.board = board
        self.visited = {self.pos}

    def tile_ahead(self) -> tuple[int, int]:
        v = DIRS[self.dir % 4]
        x, y = map(sum, zip(self.pos, v))
        return x, y

    def move(self) -> None:
        while self.board[self.tile_ahead()] == '#':
            self.dir += 1
        self.pos = self.tile_ahead()
        if self.pos in self.board:
            self.visited.add(self.pos)

    def outside(self) -> bool:
        return self.pos not in self.board

    @property
    def steps(self) -> int:
        return len(self.visited)


def test_move_guard() -> None:
    with open('test.txt') as f:
        game = load(f)
    game.guard.move()
    assert game.guard.steps == 2


def test_test_input() -> None:
    with open('test.txt') as f:
        game = load(f)
    while not game.guard.outside():
        game.guard.move()
    assert game.guard.steps == 41


if __name__ == '__main__':
    with open('input.txt') as f:
        game = load(f)
    while not game.guard.outside():
        game.guard.move()
    print(game.guard.steps)
