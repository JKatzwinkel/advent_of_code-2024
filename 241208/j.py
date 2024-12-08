from __future__ import annotations

from collections import defaultdict
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
        return self.antennas.get(freq)
