from __future__ import annotations

from collections import defaultdict
import itertools
from io import StringIO, TextIOBase

import pytest


@pytest.fixture
def example_data() -> StringIO:
    return StringIO('''
    ......#....#
    ...#....0...
    ....#0....#.
    ..#....0....
    ....0....#..
    .#....A.....
    ...#........
    #......#....
    ........A...
    .........A..
    ..........#.
    ..........#.
    ''')


def load(src: TextIOBase) -> Board:
    result = Board()
    y = 0
    for line in src:
        if not line.split('\n')[0].strip():
            continue
        read_input_line(y, line, result)
        y += 1
    result.height = y
    return result


def read_input_line(y: int, line: str, result: Board) -> None:
    line = line.split('\n')[0].strip()
    result.width = len(line)
    for x, char in enumerate(line):
        if char in '.#':
            continue
        result.add_antenna(char, (x, y))


def test_load(example_data: StringIO) -> None:
    board = load(example_data)
    assert board.frequencies == ['0', 'A']
    assert (8, 1) in board['0']
    assert board.width == 12
    assert board.height == 12


def v(a: tuple[int, int], b: tuple[int, int]) -> tuple[int, int]:
    return b[0] - a[0], b[1] - a[1]


def vadd(a: tuple[int, int], v: tuple[int, int]) -> tuple[int, int]:
    return a[0] + v[0], a[1] + v[1]


def vsub(a: tuple[int, int], v: tuple[int, int]) -> tuple[int, int]:
    return a[0] - v[0], a[1] - v[1]


def test_vectors() -> None:
    a = (2, 7)
    b = (8, 3)
    assert vadd(a, v(a, b)) == b
    assert vsub(b, v(a, b)) == a


class Board:
    def __init__(self) -> None:
        self.height = 0
        self.width = 0
        self.antennas: dict[str, set[tuple[int, int]]] = defaultdict(set)

    def add_antenna(self, freq: str, pos: tuple[int, int]) -> None:
        self.antennas[freq].add(pos)

    @property
    def frequencies(self) -> list[str]:
        return list(self.antennas.keys())

    def __getitem__(self, freq: str) -> set[tuple[int, int]]:
        return self.antennas.get(freq, set())

    def __contains__(self, pos: tuple[int, int]) -> bool:
        x, y = pos
        if not 0 <= x < self.width:
            return False
        return 0 <= y < self.height

    def antinodes(self, freq: str) -> set[tuple[int, int]]:
        antennas = self[freq]
        result = set()
        for a, b in itertools.permutations(antennas, 2):
            if (pos := vadd(b, v(a, b))) not in self:
                continue
            result.add(pos)
        return result

    def all_antinodes(self) -> set[tuple[int, int]]:
        result = set()
        for freq in self.frequencies:
            result.update(self.antinodes(freq))
        return result


def test_place_antinodes_for_single_freq(example_data: StringIO) -> None:
    board = load(example_data)
    antinodes = board.antinodes('0')
    assert (6, 0) in antinodes
    assert (3, 6) in antinodes


def test_place_antinodes(example_data: StringIO) -> None:
    board = load(example_data)
    antinodes = board.all_antinodes()
    assert len(antinodes) == 14
