from __future__ import annotations

from collections import defaultdict
from io import StringIO, TextIOBase
import os
from typing import Iterable, Iterator, Self


import pytest


def load(src: TextIOBase) -> tuple[Garden, list[Region]]:
    return Loader(src).load()


class Loader:
    def __init__(self, src: TextIOBase) -> None:
        self.garden = Garden()
        self.plot_regions = self.garden.plot_regions
        self.src = src

    def merge(self, pos1: Point, pos2: Point) -> Region:
        merged = self.plot_regions[pos1].add_all(
            self.plot_regions[pos2]
        )
        for plot in merged:
            self.plot_regions[plot] = merged
        return merged

    def load(self) -> tuple[Garden, list[Region]]:
        z = 0
        prev = ''
        for row in self.src:
            if not (plots := row.split('\n')[0].strip()):
                continue
            self.garden.add(plots)
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
        self.garden.height = z
        return self.garden, self.garden.regions


def price(
    regions: list[Region] | Region, /, *,
    bulk: bool = False
) -> int:
    if isinstance(regions, Region):
        return price([regions], bulk=bulk)
    return sum(prices(regions, bulk=bulk))


def prices(
    regions: list[Region], bulk: bool = False
) -> list[int]:
    return [region.price(bulk=bulk) for region in regions]


type Point = tuple[int, int]
type Direction = tuple[int, int]

DIRS: list[Direction] = [
    UP := (0, -1), RIGHT := (1, 0),
    DOWN := (0, 1), LEFT := (-1, 0)
]


def step_into(v: Direction, pos: Point) -> Point:
    x, z = map(sum, zip(pos, v))
    return x, z


def rotate(v: Direction) -> Direction:
    '''
    >>> rotate(UP)
    (-1, 0)

    >>> rotate(DOWN)
    (1, 0)

    '''
    i = DIRS.index(v)
    return DIRS[(i - 1) % 4]


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
    def __init__(
        self, plant: str = '', /, *, garden: Garden | None = None
    ) -> None:
        self.garden = garden
        self.plots: set[Point] = set()
        self.plant = plant

    def price(self, /, *, bulk: bool = False) -> int:
        if not bulk:
            return self.area * self.perimeter
        return self.area * len(self.sides)

    @property
    def area(self) -> int:
        return len(self.plots)

    @property
    def perimeter(self) -> int:
        return sum(
            map(len, self.borders().values())
        )

    def borders(self) -> dict[Point, list[Direction]]:
        result = defaultdict(list)
        for plot in self.plots:
            result[plot] = [
                direction for direction in DIRS
                if step_into(
                    direction, plot
                ) not in self
            ]
        return result

    @property
    def sides(self) -> list[Side]:
        sides: dict[Point, dict[Direction, Side]] = {
            pos: {
                direction: Side(pos, pos, direction)
                for direction in directions
            }
            for pos, directions in self.borders().items()
        }
        done = False
        while not done:
            done = True
            for pos, directions in sides.items():
                for direction, side in directions.items():
                    adjacent = step_into(
                        rotate(direction), side.start
                    )
                    if adjacent not in sides:
                        continue
                    if direction in sides[adjacent]:
                        side.start = adjacent
                        sides[adjacent][direction] = side
                        done = False
        return list(set(
            side
            for pos, directions in sides.items()
            for direction, side in directions.items()
        ))

    def add_all(self, other: Self) -> Self:
        self.plots.update(other.plots)
        self._perimeter = 0
        return self

    def add(self, plot: Point) -> Self:
        self.plots.add(plot)
        self._perimeter = 0
        return self

    def __contains__(self, plot: Point) -> bool:
        return plot in self.plots

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


class Garden:
    def __init__(self) -> None:
        self.plots = ''
        self.width = 0
        self.height = 0
        self.plot_regions: dict[Point, Region] = defaultdict(
            Region
        )

    @property
    def regions(self) -> list[Region]:
        return sorted(
            list(set(self.plot_regions.values()))
        )

    def add(self, plots: str) -> Self:
        self.plots += plots
        self.width = max(self.width, len(plots))
        return self


class Side:
    '''
    >>> Side((0, 1), (2, 1), (0, -1))
    <Side[(0, 1) -> (2, 1) ↑ (0, -1)]>

    >>> Side((2, 0), (2, 4), (-1, 0))
    <Side[(2, 0) -> (2, 4) ← (-1, 0)]>
    '''

    ARROWS = '↑→↓←'

    def __init__(
        self, start: Point, end: Point, facing: Direction
    ) -> None:
        self.start = start
        self.end = end
        self.facing = facing

    def __repr__(self) -> str:
        arrow = self.__class__.ARROWS[
            DIRS.index(self.facing)
        ]
        return (
            f'<Side[{self.start} -> {self.end} '
            f'{arrow} {self.facing}]>'
        )


# TESTS


def plot_garden(
    garden: Garden, /, region: Region | None = None,
    *, ansi: bool = True
) -> str:
    from p import Plotter
    return Plotter(garden, ansi=ansi).plot(region)


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
    garden, regions = load(medion_example)
    assert regions[0].plant == 'O'
    assert regions[0].perimeter == 36
    assert regions[1].perimeter == 4


def test_sides() -> None:
    garden, regions = load(
        StringIO(
            '''EEEEE
            EXXXX
            EEEEE
            EXXXX
            EEEEE'''
        )
    )
    assert regions[0].plant == 'E'
    assert regions[0].borders()[0, 0] == [UP, LEFT]
    assert len(sides := regions[0].sides) == 12, (
        '\n'.join(side.__repr__() for side in sides)
        + '\n\n' + plot_garden(
            garden, regions[0], ansi=False
        )
    )
    assert price(regions, bulk=True) == 236


def test_bulk_price() -> None:
    garden, regions = load(
        StringIO(
            '''AAAAAA
            AAABBA
            AAABBA
            ABBAAA
            ABBAAA
            AAAAAA'''
        )
    )
    assert price(regions, bulk=True) == 368


def test_smol(smol_example: StringIO) -> None:
    garden, regions = load(smol_example)
    assert len(regions) == 5
    assert regions[0].area == 4
    assert regions[0].plant == 'A'
    assert len(regions[0].sides) == 4
    assert prices(regions) == [
        40, 32, 40, 4, 24
    ]
    assert regions[2].plant == 'C'
    assert len(regions[2].sides) == 8
    assert [
        len(region.sides) for region in regions
    ] == [4, 4, 8, 4, 4]
    assert prices(regions, bulk=True) == [
        16, 16, 32, 4, 12
    ]


def test_smol_sides(smol_example: StringIO) -> None:
    garden, regions = load(smol_example)
    assert plot_garden(
        garden, regions[2], ansi=False
    ) == '\n'.join([
        '         ',
        ' A A A A ',
        '    +-+  ',
        ' B B|C|D ',
        '    + +-+',
        ' B B|C C|',
        '    +-+ +',
        ' E E E|C|',
        '      +-+',
    ])


def test_color_plot() -> None:
    garden, regions = load(StringIO('a'))
    assert plot_garden(garden, regions[0]).endswith(
        '\033[00m'
    )


def test_medion(medion_example: StringIO) -> None:
    garden, regions = load(medion_example)
    assert len(regions) == 5
    assert regions[0].plant == 'O'
    assert prices(regions) == [
        756, 4, 4, 4, 4
    ]
    assert price(regions, bulk=True) == 436


def test_large(large_example: StringIO) -> None:
    garden, regions = load(large_example)
    assert len(regions) == 11
    assert regions[0].plant == 'C'
    assert price(regions[0]) == 4
    assert regions[1].plant == 'C'
    assert price(regions[1]) == 392
    assert price(regions) == 1930
    assert price(regions, bulk=True) == 1206


@pytest.mark.skipif(
    'GITHUB_RUN_ID' not in os.environ, reason='slow'
)
def test_input() -> None:
    with open('input.txt') as f:
        garden, regions = load(f)
    assert price(regions) == 1424472
    assert price(regions, bulk=True) == 870202


if __name__ == '__main__':
    with open('input.txt') as f:
        garden, regions = load(f)
    print(plot_garden(garden))
    print(
        'price of fencing garden wihout bulk discount: '
        f'{price(regions)}'
    )
    print(
        'price of fencing garden with bulk discount: '
        f'{price(regions, bulk=True)}'
    )
