from __future__ import annotations

from collections import defaultdict
from io import StringIO, TextIOBase
from typing import Self

import pytest


@pytest.fixture
def smol_example() -> StringIO:
    return StringIO(
        '''AAAA
        BBCD
        BBCC
        EEEC'''
    )


@pytest.fixture
def medion_example() -> StringIO:
    return StringIO(
        '''
        OOOOO
        OXOXO
        OOOOO
        OXOXO
        OOOOO
        '''
    )


@pytest.fixture
def large_example() -> StringIO:
    return StringIO(
        '''
        RRRRIICCFF
        RRRRIICCCF
        VVRRRCCFFF
        VVRCCCJFFF
        VVVVCJJCFE
        VVIVCCJJEE
        VVIIICJJEE
        MIIIIIJJEE
        MIIISIJEEE
        MMMISSJEEE'''
    )


def load(src: TextIOBase) -> list[Region]:
    regions: dict[Point, Region] = defaultdict(Region)
    z = 0
    prev = ''
    for row in src:
        if not (plots := row.split('\n')[0].strip()):
            continue
        for x, plant in enumerate(plots):
            if z > 0 and prev[x] == plant:
                regions[x, z] = regions[x, z-1]
            elif x > 0 and plots[x-1] == plant:
                regions[x, z] = regions[x-1, z]
            else:
                regions[x, z].plant = plant
            regions[x, z].plots.add((x, z))
        z += 1
        prev = plots
    return sorted(list(set(regions.values())))


def test_load(smol_example: StringIO) -> None:
    regions = load(smol_example)
    assert len(regions) == 5
    assert regions[0].area == 4
    assert regions[0].plant == 'A'


def test_load_medion(medion_example: StringIO) -> None:
    regions = load(medion_example)
    assert len(regions) == 5
    assert regions[0].plant == 'O'


def test_load_large(large_example: StringIO) -> None:
    regions = load(large_example)
    assert len(regions) == 11


type Point = tuple[int, int]
DIRS = [(0, -1), (1, 0), (0, 1), (-1, 0)]


def step_into(v: Point, pos: Point) -> Point:
    x, z = map(sum, zip(pos, v))
    return x, z


class Region:
    '''
    >>> r = Region()
    >>> r.plant = 'A'
    >>> r.add((1, 1))
    <Region[A]{(1, 1)}>
    >>> r.area
    1
    >>> r.perimeter
    4
    >>> r.add((2, 1)).perimeter
    6
    '''
    def __init__(self) -> None:
        self.plots: set[Point] = set()
        self.plant = ''

    @property
    def area(self) -> int:
        return len(self.plots)

    @property
    def perimeter(self) -> int:
        result = 0
        for plot in self.plots:
            result += 4 - sum(
                1
                for adjacent in (
                    step_into(direction, plot) for direction in DIRS
                )
                if adjacent in self.plots
            )
        return result

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}[{self.plant}]{self.plots}>'

    def __lt__(self, other: Self) -> bool:
        if self.plant == other.plant:
            return self.area < other.area
        return self.plant < other.plant

    def add(self, plot: Point) -> Self:
        self.plots.add(plot)
        return self

    @property
    def price(self) -> int:
        return self.area * self.perimeter


def test_perimeter(medion_example: StringIO) -> None:
    regions = load(medion_example)
    assert regions[0].plant == 'O'
    assert regions[0].perimeter == 36
    assert regions[1].perimeter == 4


def test_price_01(smol_example: StringIO) -> None:
    regions = load(smol_example)
    assert regions[0].plant == 'A'
    assert [region.price for region in regions] == [40, 32, 40, 4, 24]


def test_price_02(medion_example: StringIO) -> None:
    regions = load(medion_example)
    assert regions[0].plant == 'O'
    assert [region.price for region in regions] == [756, 4, 4, 4, 4]


def test_price_03(large_example: StringIO) -> None:
    regions = load(large_example)
    assert regions[0].plant == 'C'
    assert regions[0].price == 4
    assert regions[1].plant == 'C'
    assert regions[1].price == 392
    assert sum(region.price for region in regions) == 1930
