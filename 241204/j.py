from __future__ import annotations

from io import StringIO, TextIOBase
import itertools
from typing import Iterable, Iterator, Self

import pytest


def load(src: TextIOBase) -> Puzzle:
    result = Puzzle()
    y = 0
    for line in src:
        if not (data := line.strip()):
            continue
        result.append(data)
        y += 1
    result.height = y
    return result


class B(Iterable[int]):
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

    def __iter__(self) -> Iterator[int]:
        self._iter = iter([self.x, self.y])
        return self

    def __next__(self) -> int:
        return next(self._iter)

    def __repr__(self) -> str:
        return (
            f'<{self.__class__.__name__}('
            f'{self.x}, {self.y})>'
        )

    def __eq__(self, other: object) -> bool:
        assert isinstance(other, self.__class__)
        x, y = other
        return self.x == x and self.y == y

    def __hash__(self) -> int:
        return self.y * 10 ** 8 + self.x


class P(B):
    def move(
        self, direction: D, distance: int = 1
    ) -> P:
        xv, yv = direction
        return P(
            self.x + xv * distance,
            self.y + yv * distance
        )


class D(B):
    '''
    >>> D(-1, 1)
    ↙

    >>> D(0, -1)
    ↑

    >>> D(2, 1)
    <D(2, 1)>

    >>> D(1, 1).go_from(P(3, 4))
    <P(4, 5)>

    >>> D(1, 1) * D(-1, 1)
    0
    '''

    def go_from(self, pos: P, distance: int = 1) -> P:
        return pos.move(self, distance)

    def is_diagonal(self) -> bool:
        return self.x != 0 and self.y != 0

    @classmethod
    def contain_x(self, *vectors: Self) -> bool:
        '''
        >>> D.contain_x(D(-1, 1), D(0, 1), D(1, -1))
        False

        >>> D.contain_x(D(-1, -1), D(0, 1), D(1, -1))
        True

        >>> D.contain_x()
        False
        '''
        return any(
            v1 * v2 == 0
            for v1, v2 in itertools.combinations(
                vectors, 2
            )
        )

    def __mul__(self, v: Self) -> int:
        return self.x * v.x + self.y * v.y

    def __repr__(self) -> str:
        if self not in DIRS:
            return super(D, self).__repr__()
        return ARROWS[DIRS.index(self)]


DIRS = [
    D(x, y)
    for x, y in itertools.product(*([[-1, 0, 1]] * 2))
    if x or y
]
ARROWS = '↖←↙↑↓↗→↘'


class Puzzle:
    def __init__(self) -> None:
        self.width = 0
        self.height = 0
        self.letters = ''

    def __contains__(
        self, pos: P | tuple[int, int]
    ) -> bool:
        x, y = pos
        if not 0 <= x < self.width:
            return False
        return 0 <= y < self.height

    def __getitem__(
        self, pos: P | tuple[int, int]
    ) -> str:
        if pos not in self:
            return ''
        x, y = pos
        i = x + y * self.width
        return self.letters[i]

    def append(self, row: str) -> None:
        self.letters += row
        self.width = len(row)

    def search(
        self, word: str, offset: int = 0
    ) -> dict[P, list[D]]:
        frontier = {
            P(x, y): DIRS.copy()
            for x in range(self.width)
            for y in range(self.height)
            if self[x, y] == word[offset]
        }
        for dist, letter in enumerate(word):
            new_frontier = {}
            for pos, directions in frontier.items():
                new_frontier[pos] = [
                    direction
                    for direction in directions
                    if self[
                        pos.move(
                            direction, dist - offset
                        )
                    ] == letter
                ]
            frontier = new_frontier
        return {
            pos: directions
            for pos, directions in frontier.items()
            if directions
        }

    def count(self, word: str) -> int:
        frontier = self.search(word)
        return sum(map(len, frontier.values()))

    def find_x(self, word: str) -> dict[P, list[D]]:
        result = self.search(word, len(word) // 2)
        return {
            pos: directions
            for pos, directions in result.items()
            if D.contain_x(
                *(
                    d for d in directions
                    if d.is_diagonal()
                )
            )
        }

    def count_x(self, word: str) -> int:
        return sum(
            1
            for directions in self.find_x(word).values()
        )


def test_load(example_1: str) -> None:
    grid = load(StringIO(example_1))
    assert grid.height == 10
    assert len(grid.letters) == grid.width * grid.height


@pytest.fixture
def example_1() -> str:
    return '''
        MMMSXXMASM
        MSAMXMSMSA
        AMXSXMAAMM
        MSAMASMSMX
        XMASAMXAMM
        XXAMMXXAMA
        SMSMSASXSS
        SAXAMASAAA
        MAMMMXMMMM
        MXMXAXMASX'''


def test_pick_letter(example_1: str) -> None:
    grid = load(StringIO(example_1))
    p = P(0, 0)
    assert p in grid
    assert grid[p] == 'M'
    assert grid[p.move(D(1, 1), 2)] == 'X'


def test_find_word(example_1: str) -> None:
    grid = load(StringIO(example_1))
    result = grid.search('XMAS')
    assert len(result) == 12, '\n'.join(
        f'{pos}: {directions}'
        for pos, directions in result.items()
    )
    assert P(0, 4) in result, f'{result}'
    assert f'{result[P(0, 4)]}' == '[→]'
    assert grid.count('XMAS') == 18


def test_find_word_x() -> None:
    grid = load(StringIO(
        '''M.S
           .A.
           M.S'''
    ))
    result = grid.find_x('MAS')
    assert P(1, 1) in result
    assert str(result[P(1, 1)]) == '[↗, ↘]'
    assert grid.count_x('MAS') == 1


@pytest.fixture
def example_clean() -> str:
    return '''
        .M.S......
        ..A..MSMS.
        .M.S.MAA..
        ..A.ASMSM.
        .M.S.M....
        ..........
        S.S.S.S.S.
        .A.A.A.A..
        M.M.M.M.M.
        ..........'''


def test_find_word_centers(example_clean: str) -> None:
    grid = load(StringIO(example_clean))
    result = grid.search('MAS', 1)
    assert len(result) == 9
    assert str(result[P(7, 2)]) == '[↖, ↓, ↗]'


def test_count_word_x(example_clean: str) -> None:
    grid = load(StringIO(example_clean))
    assert grid.count_x('MAS') == 9, (
        f'{grid}\n\n' + '\n'.join(
            f'{pos}: {directions}'
            for pos, directions
            in grid.find_x('MAS').items()
        )
    )


def test_input() -> None:
    with open('input.txt') as f:
        grid = load(f)
    assert grid.count('XMAS') == 2685
    assert grid.count_x('MAS') == 2048
