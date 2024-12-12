from __future__ import annotations

from collections import defaultdict
from io import StringIO, TextIOBase
from typing import Iterable, Iterator, Self

import pytest


def load(src: TextIOBase) -> list[Region]:
    return Loader(src).load()


class Loader:
    def __init__(self, src: TextIOBase) -> None:
        self.plot_regions: dict[Point, Region] = defaultdict(Region)
        self.src = src

    def merge(self, pos1: Point, pos2: Point) -> Region:
        merged = self.plot_regions[pos1].add_all(
            self.plot_regions[pos2]
        )
        for plot in merged:
            self.plot_regions[plot] = merged
        return merged

    def load(self) -> list[Region]:
        z = 0
        prev = ''
        for row in self.src:
            if not (plots := row.split('\n')[0].strip()):
                continue
            for x, plant in enumerate(plots):
                self.plot_regions[x, z].add((x, z))
                if z > 0 and prev[x] == plant:
                    self.merge((x, z-1), (x, z))
                if x > 0 and plots[x-1] == plant:
                    self.merge((x-1, z), (x, z))
                else:
                    self.plot_regions[x, z].plant = plant
            z += 1
            prev = plots
        return sorted(list(set(self.plot_regions.values())))


def price(regions: list[Region]) -> int:
    return sum(region.price for region in regions)


type Point = tuple[int, int]
DIRS = [(0, -1), (1, 0), (0, 1), (-1, 0)]


def step_into(v: Point, pos: Point) -> Point:
    x, z = map(sum, zip(pos, v))
    return x, z


class Region(Iterable[Point]):
    '''
    >>> r = Region('A')
    >>> r.add((1, 1))
    <Region[A]{(1, 1)}>
    >>> r.area
    1
    >>> r.perimeter
    4
    >>> r.add((2, 1)).perimeter
    6
    '''
    def __init__(self, plant: str = '') -> None:
        self.plots: set[Point] = set()
        self.plant = plant

    @property
    def price(self) -> int:
        return self.area * self.perimeter

    @property
    def area(self) -> int:
        return len(self.plots)

    @property
    def perimeter(self) -> int:
        result = 0
        for plot in self.plots:
            result += sum(
                1 for adjacent in (
                    step_into(direction, plot) for direction in DIRS
                )
                if adjacent not in self.plots
            )
        return result

    def add_all(self, other: Self) -> Self:
        self.plots.update(other.plots)
        return self

    def add(self, plot: Point) -> Self:
        self.plots.add(plot)
        return self

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}[{self.plant}]{self.plots}>'

    def __lt__(self, other: Self) -> bool:
        if self.plant == other.plant:
            return self.area < other.area
        return self.plant < other.plant

    def __iter__(self) -> Iterator[Point]:
        self._iter = iter(self.plots)
        return self

    def __next__(self) -> Point:
        return next(self._iter)


# TESTS


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
        '''RRRRIICCFF
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


def test_region_comparator() -> None:
    a = Region('A').add((1, 1)).add((2, 1))
    b = Region('A').add((3, 1))
    assert max(a, b) == a
    assert sorted([a, b])[-1] == a


def test_perimeter(medion_example: StringIO) -> None:
    regions = load(medion_example)
    assert regions[0].plant == 'O'
    assert regions[0].perimeter == 36
    assert regions[1].perimeter == 4


def test_smol(smol_example: StringIO) -> None:
    regions = load(smol_example)
    assert len(regions) == 5
    assert regions[0].area == 4
    assert regions[0].plant == 'A'
    assert [region.price for region in regions] == [
        40, 32, 40, 4, 24
    ]


def test_medion(medion_example: StringIO) -> None:
    regions = load(medion_example)
    assert len(regions) == 5
    assert regions[0].plant == 'O'
    assert [region.price for region in regions] == [
        756, 4, 4, 4, 4
    ]


def test_large(large_example: StringIO) -> None:
    regions = load(large_example)
    assert len(regions) == 11
    assert regions[0].plant == 'C'
    assert regions[0].price == 4
    assert regions[1].plant == 'C'
    assert regions[1].price == 392
    assert price(regions) == 1930


def test_input() -> None:
    with open('input.txt') as f:
        regions = load(f)
    assert price(regions) == 1424472
