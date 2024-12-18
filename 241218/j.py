from __future__ import annotations

from io import StringIO, TextIOBase
from textwrap import dedent
from typing import Self


EXAMPLE = '''
    5,4
    4,2
    4,5
    3,0
    2,1
    6,3
    2,4
    1,5
    0,6
    3,3
    2,6
    5,1
    1,2
    5,5
    2,5
    6,5
    1,4
    0,4
    6,4
    1,1
    6,1
    1,0
    0,5
    1,6
    2,0'''


def load(src: TextIOBase, width: int) -> Mem:
    positions = [
        eval(line) for line in src if len(line.strip())
    ]
    return Mem(width, positions)


class Mem:
    def __init__(
        self, width: int, falling_bytes: list[tuple[int, int]]
    ) -> None:
        self.width = width
        self.falling = falling_bytes
        self.corrupted: set[tuple[int, int]] = set()

    def fall(self, times: int = 1) -> Self:
        while times > 0 and self.falling:
            self.corrupted.add(self.falling.pop(0))
            times -= 1
        return self

    def __getitem__(self, pos: tuple[int, int]) -> bool:
        return pos in self.corrupted

    def __str__(self) -> str:
        lines = [
            ['.'] * self.width for y in range(self.width)
        ]
        for x, y in self.corrupted:
            lines[y][x] = '#'
        return '\n'.join(
            ''.join(line) for line in lines
        )


def test_load() -> None:
    mem = load(StringIO(EXAMPLE), 7)
    mem.fall(2)
    assert not mem[0, 0]
    assert mem[5, 4]
    assert mem[4, 2]


def test_plot() -> None:
    mem = load(StringIO(EXAMPLE), 7)
    mem.fall(12)
    assert f'{mem}' == dedent(
        '''\
        ...#...
        ..#..#.
        ....#..
        ...#..#
        ..#..#.
        .#..#..
        #.#....'''
    ), f'{mem}'
