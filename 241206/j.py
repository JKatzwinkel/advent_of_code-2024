from __future__ import annotations

from collections import Counter
from copy import copy
from enum import Enum
from io import TextIOBase
from typing import Self

import tqdm

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
            game.guard = Guard(game, (x, y))
        tiles.append(char == '#')
    game.board.tiles.extend(tiles)


def test_load() -> None:
    with open('test.txt', 'r') as f:
        game = load(f)
    assert game.board.width == 10
    assert game.board.height == 10
    assert game.guard.pos == (4, 6)


def _find_all(
    trail: list[tuple[int, int]], elem: tuple[int, int]
) -> list[int]:
    result = []
    start = 0
    while start < len(trail):
        try:
            result.append(i := trail.index(elem, start))
            start = i + 1
        except ValueError:
            break
    return result


def contains_loop(trail: list[tuple[int, int]]) -> bool:
    def _still_fits(index: int, offset: int) -> bool:
        if index - offset < 0:
            return False
        return trail[index - offset] == trail[-(offset + 1)]
    candidates = _find_all(trail[:-1], trail[-1])
    offset = 1
    while len(candidates) > 0:
        if len(trail) - offset <= candidates[-1] + 1:
            return True
        candidates = [
            index for index in candidates
            if _still_fits(index, offset)
        ]
        offset += 1
    return False


def test_contains_loop() -> None:
    assert _find_all(
       [(0, 1), (1, 1), (2, 1), (2, 2), (1, 2), (1, 1), (1, 0)],
       (1, 1)
    ) == [1, 5]
    assert contains_loop(
       [
           (0, 1), (1, 1), (2, 1), (2, 2), (1, 2), (1, 1), (2, 1),
           (2, 2), (1, 2)
        ]
    )
    assert not contains_loop(
        [
            (1, 1), (2, 1), (3, 1), (3, 2), (2, 2), (2, 1), (2, 0)
        ]
    )


class State(Enum):
    LEFT = 1
    STUCK = 2


class Game:
    def __init__(self):
        self.guard = None
        self.board = None

    def loop(self) -> State:
        while not self.guard.outside() and not self.guard.stuck():
            self.guard.move()
        if self.guard.outside():
            return State.LEFT
        return State.STUCK

    def __copy__(self) -> Self:
        result = self.__class__()
        result.guard = copy(self.guard)
        result.guard.game = result
        result.board = copy(self.board)
        return result

    def with_obstacle(self, pos: tuple[int, int]) -> Self | None:
        if pos == self.guard.pos:
            return None
        result = copy(self)
        result.board = self.board.with_obstacle(pos)
        if not result.board:
            return None
        return result


def test_copy_game_with_obstacle() -> None:
    with open('test.txt') as f:
        game = load(f)
    assert (copied := game.with_obstacle((3, 6)))
    assert copied.board[3, 6] == '#'
    assert game.board[3, 6] == '.'


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

    def __setitem__(self, pos: tuple[int, int], value: str) -> None:
        x, y = pos
        self.tiles[x + y * self.width] = value in ('#', 'O')

    def __copy__(self) -> Self:
        result = self.__class__()
        result.width = self.width
        result.height = self.height
        result.tiles = copy(self.tiles)
        return result

    def with_obstacle(self, pos: tuple[int, int]) -> Self:
        result = copy(self)
        result[pos] = 'O'
        return result


def test_sample_board() -> None:
    with open('test.txt') as f:
        game = load(f)
    assert game.board[2, 3] == '#'
    assert game.board[3, 3] == '.'
    assert not game.board[10, 2]


class Guard:
    def __init__(self, game: Game, pos: tuple[int, int]):
        self.pos = pos
        self.dir = 0
        self.game = game
        self.visited = Counter({pos})
        self.trail: list[tuple[int, int]] = []

    def tile_ahead(self) -> tuple[int, int]:
        v = DIRS[self.dir % 4]
        x, y = map(sum, zip(self.pos, v))
        return x, y

    def move(self) -> None:
        while self.game.board[self.tile_ahead()] == '#':
            self.dir += 1
        self.trail.append(self.pos)
        self.pos = self.tile_ahead()
        if self.pos in self.game.board:
            self.visited[self.pos] += 1

    def outside(self) -> bool:
        return self.pos not in self.game.board

    def stuck(self) -> bool:
        if not self.visited.total() > self.tiles_visited:
            return False
        return contains_loop(self.trail)

    @property
    def tiles_visited(self) -> int:
        return len(self.visited)

    def __copy__(self) -> Self:
        result = self.__class__(self.game, self.pos)
        result.dir = self.dir
        result.visited = copy(self.visited)
        return result


def test_move_guard() -> None:
    with open('test.txt') as f:
        game = load(f)
    game.guard.move()
    assert game.guard.tiles_visited == 2


def test_test_input() -> None:
    with open('test.txt') as f:
        game = load(f)
    assert game.loop() == State.LEFT
    assert game.guard.tiles_visited == 41


def test_get_guard_stuck() -> None:
    with open('test.txt') as f:
        assert (game := load(f).with_obstacle((3, 6)))
    assert game.loop() == State.STUCK


def find_obstacle_placements(filename: str) -> list[tuple[int, int]]:
    with open(filename) as f:
        game = load(f)
    orig = copy(game)
    assert game.loop() == State.LEFT
    results = []
    pb = tqdm.tqdm(total=game.guard.tiles_visited)
    for pos in [p for p in game.guard.visited][1:]:
        pb.update(1)
        if not (variant := orig.with_obstacle(pos)):
            continue
        if variant.loop() == State.STUCK:
            results.append(pos)
    pb.close()
    return results


def test_find_obstacle_placements() -> None:
    positions = find_obstacle_placements('test.txt')
    assert len(positions) == 6


if __name__ == '__main__':
    with open('input.txt') as f:
        game = load(f)
    assert game.loop() == State.LEFT
    print(f'tiles patrolled by guard: {game.guard.tiles_visited}')
    positions = find_obstacle_placements('input.txt')
    print(
        'possible position for obstacles resulting in infinite loop: '
        f'{len(positions)}'
    )
