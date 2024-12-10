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
        self.trails: list[list[Point]]

    def search(self) -> Self:
        self.trails = pathfind(self)
        return self

    @property
    def score(self) -> int:
        return len(self.ends)

    @property
    def rating(self) -> int:
        return len(self.trails)

    @property
    def ends(self) -> set[Point]:
        return set(trail[-1] for trail in self.trails)


DIRS = [(0, -1), (1, 0), (0, 1), (-1, 0)]


def step_into(direction: int, pos: Point) -> Point:
    v = DIRS[direction]
    x, z = map(sum, zip(pos, v))
    return x, z


class Pathfinder:
    def __init__(self, head: Trailhead) -> None:
        self.start = head.start
        self.topo = head.topo
        self.result: list[list[Point]] = []
        self.steppy: dict[Point, set[Point]] = defaultdict(set)
        self.frontier: set[Point] = {self.start}

    def run(self) -> Self:
        while self.frontier:
            self.loop()
        return self

    def loop(self) -> None:
        new_frontier: set[Point] = set()
        for pos in self.frontier:
            if (elevation := self.topo[pos]) == 9:
                self.result.extend(self.backtrack(pos))
                continue
            for direction in range(4):
                x, z = step_into(direction, pos)
                if (x, z) not in self.topo:
                    continue
                if self.topo[x, z] != elevation + 1:
                    continue
                self.steppy[x, z].add(pos)
                new_frontier.add((x, z))
        self.frontier = new_frontier.difference(
            self.frontier
        )

    def backtrack(self, pos: Point) -> list[list[Point]]:
        if not (tiles_we_came_from := self.steppy[pos]):
            return [[pos]]
        results = []
        for came_from in tiles_we_came_from:
            for path in self.backtrack(came_from):
                results.append(path + [pos])
        return results


def test_backtrack() -> None:
    topo = load(StringIO('0123456789'))
    head = Trailhead(topo, (0, 0))
    dijk = Pathfinder(head)
    for _ in range(9):
        dijk.loop()
    assert dijk.steppy[9, 0] == {(8, 0)}
    assert dijk.steppy[8, 0] == {(7, 0)}
    paths = dijk.backtrack((9, 0))
    assert paths[0] == [
        (0, 0), (1, 0), (2, 0), (3, 0), (4, 0),
        (5, 0), (6, 0), (7, 0), (8, 0), (9, 0)
    ]


def pathfind(head: Trailhead) -> list[list[Point]]:
    pathfinder = Pathfinder(head)
    return pathfinder.run().result


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


@pytest.mark.parametrize(
    'src, rating',
    [
        (
            '''.....0.
            ..4321.
            ..5..2.
            ..6543.
            ..7..4.
            ..8765.
            ..9....''', 3
        ),
        (
            '''..90..9
            ...1.98
            ...2..7
            6543456
            765.987
            876....
            987....''', 13
        ),
        (
            '''012345
            123456
            234567
            345678
            4.6789
            56789.''', 227
        ),
    ]
)
def test_trailhead_rating(src: str, rating: int) -> None:
    topo = load(StringIO(src))
    heads = topo.find_paths()
    assert len(heads) == 1
    assert heads[0].rating == rating


def test_all_trailheads_rating(example_topo: Topo) -> None:
    heads = example_topo.find_paths()
    assert [head.rating for head in heads] == [
        20, 24, 10, 4, 1, 4, 5, 8, 5
    ]


if __name__ == '__main__':
    with open('input.txt') as f:
        topo = load(f)
    heads = topo.find_paths()
    score = sum(head.score for head in heads)
    print(f'accumulative trailhead score: {score}')
