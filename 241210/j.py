from __future__ import annotations

from collections import defaultdict
from io import StringIO, TextIOBase
from typing import Self

import pytest

type Point = tuple[int, int]


def load(src: TextIOBase) -> Topo:
    result = Topo()
    z = 0
    for line in src:
        if not (payload := line.split('\n')[0].strip()):
            continue
        _load_line(z, payload, result)
        z += 1
    result.height = z
    return result


def _load_line(z: int, line: str, topo: Topo) -> None:
    elevations = []
    for x, char in enumerate(line):
        if char == '.':
            elevations.append(-1)
            continue
        elevations.append(int(char))
    topo.elevation.extend(elevations)
    topo.width = x + 1


def test_load_topo() -> None:
    src = StringIO('''
        0123
        1234
        8765
        9876
    ''')
    topo = load(src)
    assert topo.height == 4
    assert topo.width == 4
    assert topo[1, 1] == 2


class Topo:
    def __init__(self) -> None:
        self.width = 0
        self.height = 0
        self.elevation: list[int] = []

    def __getitem__(self, pos: Point) -> int:
        x, z = pos
        return self.elevation[x + z * self.width]

    def __contains__(self, pos: Point) -> bool:
        x, z = pos
        if not 0 <= x < self.width:
            return False
        return 0 <= z < self.height

    def find_heads(self) -> list[Trailhead]:
        result = []
        for i, elevation in enumerate(self.elevation):
            if elevation != 0:
                continue
            z = i // self.width
            x = i % self.width
            result.append(
                Trailhead(self, (x, z))
            )
        return result

    def find_paths(self) -> list[Trailhead]:
        return [
            head.search() for head in self.find_heads()
        ]


class Trailhead:
    def __init__(self, topo: Topo, start: Point) -> None:
        self.topo = topo
        self.start = start
        self.ends: set[Point] = set()

    def search(self) -> Self:
        self.ends = pathfind(self)
        return self

    @property
    def score(self) -> int:
        return len(self.ends)


DIRS = [(0, -1), (1, 0), (0, 1), (-1, 0)]


def step_into(direction: int, pos: Point) -> Point:
    v = DIRS[direction]
    x, z = map(sum, zip(pos, v))
    return x, z


def pathfind(head: Trailhead) -> set[Point]:
    result: set[Point] = set()
    steppy: dict[Point, set[Point]] = defaultdict(set)
    frontier: set[Point] = {head.start}
    while frontier:
        new_frontier: set[Point] = set()
        for pos in frontier:
            if (elevation := head.topo[pos]) == 9:
                result.add(pos)
                continue
            for direction in range(4):
                x, z = step_into(direction, pos)
                if (x, z) not in head.topo:
                    continue
                if head.topo[x, z] != elevation + 1:
                    continue
                steppy[x, z].add(pos)
                new_frontier.add((x, z))
        frontier = new_frontier.difference(frontier)
    return result


def test_trailhead() -> None:
    topo = load(
        StringIO('''
        ...0...
        ...1...
        ...2...
        6543456
        7.....7
        8.....8
        9.....9''')
    )
    head = Trailhead(topo, (3, 0)).search()
    assert head.ends == {(0, 6), (6, 6)}


@pytest.mark.parametrize(
    'src, start, score',
    [
        (
            '''...0...
            ...1...
            ...2...
            6543456
            7.....7
            8.....8
            9.....9''', (3, 0), 2
        ),
        (
            '''..90..9
            ...1.98
            ...2..7
            6543456
            765.987
            876....
            987....''', (3, 0), 4
        ),
        (
            '''10..9..
            2...8..
            3...7..
            4567654
            ...8..3
            ...9..2
            .....01''', (1, 0), 1
        ),
        (
            '''10..9..
            2...8..
            3...7..
            4567654
            ...8..3
            ...9..2
            .....01''', (5, 6), 2
        ),
    ]
)
def test_trailhead_scores(src: str, start: Point, score: int) -> None:
    topo = load(StringIO(src))
    head = Trailhead(topo, start)
    assert head.search().score == score

@pytest.mark.parametrize(
    'src, number',
    [
        (
            '''..90..9
            ...1.98
            ...2..7
            6543456
            765.987
            876....
            987....''', 1
        ),
        (
            '''10..9..
            2...8..
            3...7..
            4567654
            ...8..3
            ...9..2
            .....01''', 2
        ),
        (
            '''89010123
            78121874
            87430965
            96549874
            45678903
            32019012
            01329801
            10456732''', 9
        ),
    ]
)
def test_find_trailheads(src: str, number: int) -> None:
    topo = load(StringIO(src))
    heads = topo.find_heads()
    assert len(heads) == number


@pytest.fixture
def example_topo() -> Topo:
    return load(
        StringIO(
            '''89010123
            78121874
            87430965
            96549874
            45678903
            32019012
            01329801
            10456732'''
        )
    )


def test_trailhead_starts(example_topo: Topo) -> None:
    heads = example_topo.find_heads()
    assert len(heads) == 9
    starts = [head.start for head in heads]
    assert starts == [
        (2, 0), (4, 0), (4, 2), (6, 4), (2, 5), (5, 5),
        (0, 6), (6, 6), (1, 7)
    ]


def test_trailhead_score_sum(example_topo: Topo) -> None:
    heads = example_topo.find_paths()
    assert sum(head.score for head in heads) == 36
