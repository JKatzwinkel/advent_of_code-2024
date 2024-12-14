from __future__ import annotations

from io import StringIO, TextIOBase
import re
from typing import Iterable, Iterator, Self

import pytest


ROBEX = re.compile(r'p=(\d+,\d+) v=(-?\d,-?\d)')


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

    def __repr__(self) -> str:
        return f'↗({self.x}, {self.y})'


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
