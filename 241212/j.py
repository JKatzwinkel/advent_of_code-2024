from __future__ import annotations

from collections import defaultdict
from io import StringIO, TextIOBase

import pytest


@pytest.fixture
def smol_example() -> StringIO:
    return StringIO(
        '''AAAA
        BBCD
        BBCC
        EEEC'''
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
    return list(set(regions.values()))


def test_load(smol_example: StringIO) -> None:
    regions = load(smol_example)
    assert len(regions) == 5
    assert regions[0].area == 4


type Point = tuple[int, int]


class Region:
    def __init__(self) -> None:
        self.plots: set[Point] = set()
        self.perimeter = 0
        self.plant = ''

    @property
    def area(self) -> int:
        return len(self.plots)

    def __repr__(self) -> str:
        return f'<{self.__class__}{self.plots}>'
