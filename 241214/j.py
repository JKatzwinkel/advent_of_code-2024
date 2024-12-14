from __future__ import annotations

from collections import Counter
from functools import reduce
from io import StringIO, TextIOBase
import re
from textwrap import dedent
from typing import Iterable, Iterator, Self

import pytest


ROBEX = re.compile(r'p=(\d+,\d+) v=(-?\d+,-?\d+)')


def load(src: TextIOBase) -> list[Robot]:
    robots = []
    for line in src:
        if not (coords := ROBEX.findall(line)):
            continue
        robots.append(
            Robot(
                V(*eval(coords[0][0])),
                V(*eval(coords[0][1]))
            )
        )
    return robots


class Robot:
    def __init__(self, pos: V, v: V) -> None:
        self.pos = pos
        self.v = v


class Grid:
    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.robots: list[Robot] = []

    def with_robots(self, robots: list[Robot]) -> Self:
        self.robots.extend(robots)
        return self

    def __str__(self) -> str:
        robots_at = Counter(
            robot.pos for robot in self.robots
        )
        lines = []
        for z in range(self.height):
            lines.append(
                ''.join(
                    str(robots_at[V(x, z)])
                    if V(x, z) in robots_at else '.'
                    for x in range(self.width)
                )
            )
        return '\n'.join(lines)

    def tick(self, times: int = 1) -> Self:
        for robot in self.robots:
            robot.pos = (
                robot.pos + robot.v * times
            ) % V(self.width, self.height)
        return self

    def quadrants(self) -> list[int]:
        counts: dict[int, int] = Counter()
        for robot in self.robots:
            x, z = robot.pos
            if (
                x == self.width // 2
                or z == self.height // 2
            ):
                continue
            quadrant = (
                int(x / (self.width / 2)) +
                int(z / (self.height / 2)) * 2
            )
            counts[quadrant] += 1
        return [
            count for quadrant, count in sorted(
                counts.items(), key=lambda t: t[0]
            )
        ]

    def safety(self) -> int:
        return reduce(int.__mul__, self.quadrants())


class V(Iterable[int]):
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

    def __add__(self, v: Self) -> Self:
        x, y = v
        return self.__class__(self.x + x, self.y + y)

    def __iter__(self) -> Iterator[int]:
        self._iter = iter([self.x, self.y])
        return self

    def __next__(self) -> int:
        return next(self._iter)

    def __eq__(self, other: object) -> bool:
        assert isinstance(other, self.__class__)
        x, y = other
        return self.x == x and self.y == y

    def __mul__(self, factor: int) -> Self:
        return self.__class__(self.x * factor, self.y * factor)

    def __rmul__(self, factor: int) -> Self:
        return self.__mul__(factor)

    def __mod__(self, div: Self) -> Self:
        return self.__class__(
            self.x % div.x, self.y % div.y
        )

    def __repr__(self) -> str:
        return f'↗({self.x}, {self.y})'

    def __hash__(self) -> int:
        return self.y * 10 ** 10 + self.x


@pytest.fixture
def example() -> StringIO:
    return StringIO(
        '''
        p=0,4 v=3,-3
        p=6,3 v=-1,-3
        p=10,3 v=-1,2
        p=2,0 v=2,-1
        p=0,0 v=1,3
        p=3,0 v=-2,-2
        p=7,6 v=-1,-3
        p=3,0 v=-1,-2
        p=9,3 v=2,3
        p=7,3 v=-1,2
        p=2,4 v=2,-3
        p=9,5 v=-3,-3'''
    )


def test_load(example: TextIOBase) -> None:
    robots = load(example)
    assert len(robots) == 12
    assert robots[0].pos == V(0, 4)
    assert robots[0].v == V(3, -3)


def test_grid(example: TextIOBase) -> None:
    grid = Grid(11, 7).with_robots(load(example))
    assert f'{grid}' == dedent(
        '''\
        1.12.......
        ...........
        ...........
        ......11.11
        1.1........
        .........1.
        .......1...'''
    )


def test_tick() -> None:
    grid = Grid(11, 7).with_robots(
        [Robot(V(2, 4), V(2, -3))]
    )
    assert str(grid) == dedent(
        '''\
        ...........
        ...........
        ...........
        ...........
        ..1........
        ...........
        ...........'''
    )
    assert str(grid.tick(5)) == dedent(
        '''\
        ...........
        ...........
        ...........
        .1.........
        ...........
        ...........
        ...........'''
    )


def test_count_robots(example: TextIOBase) -> None:
    grid = Grid(11, 7).with_robots(
        load(example)
    ).tick(100)
    assert str(grid) == dedent(
        '''\
        ......2..1.
        ...........
        1..........
        .11........
        .....1.....
        ...12......
        .1....1....'''
    )
    count = grid.quadrants()
    assert count == [1, 3, 4, 1]
    assert grid.safety() == 12


def test_input() -> None:
    with open('input.txt') as f:
        robots = load(f)
    assert len(robots) == 500
    grid = Grid(101, 103).with_robots(robots).tick(100)
    assert grid.safety() == 226236192


if __name__ == '__main__':
    with open('input.txt') as f:
        robots = load(f)
    grid = Grid(101, 103).with_robots(robots).tick(100)
    with open('output.txt', 'w+') as f:
        f.write(str(grid))
