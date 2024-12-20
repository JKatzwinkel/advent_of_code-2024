from __future__ import annotations

from collections import Counter
from io import StringIO, TextIOBase
from typing import Self


def load(src: TextIOBase) -> Maze:
    maze = Maze()
    y = 0
    for line in src:
        if not (row := line.strip()):
            continue
        maze.tiles.extend([c for c in row])
        maze.width = len(row)
        y += 1
    maze.height = y
    return maze


class Maze:
    def __init__(self) -> None:
        self.width = 0
        self.height = 0
        self.tiles: list[str] = []

    @property
    def start(self) -> P:
        y, x = divmod(
            self.tiles.index('S'), self.width
        )
        return x, y

    def __getitem__(self, pos: P) -> str:
        x, y = pos
        return self.tiles[x+y*self.width]

    def solve(self) -> Self:
        p = self.start
        self.path = [p]
        while self[p] != 'E':
            for d in DIRS:
                a = step(p, d)
                if self[a] == '#' or a in self.path:
                    continue
                self.path.append(p := a)
                break
        return self


type P = tuple[int, int]
DIRS = [(0, -1), (1, 0), (0, 1), (-1, 0)]


def step(pos: P, direction: P) -> P:
    x, y = map(sum, zip(pos, direction))
    return x, y


def shortcuts(
    path: list[P], max_dist: int = 2, min_dist: int = 2
) -> dict[int, int]:
    savings: dict[int, int] = Counter()
    opposites = find_in_range(
        path, max_dist=max_dist, min_dist=min_dist
    )
    for a, i, b, j in opposites:
        saves = j - i - dist(a, b)
        savings[saves] += 1
    return savings


def find_in_range(
    path: list[P], max_dist: int = 2, min_dist: int = 2
) -> list[tuple[P, int, P, int]]:
    results = []
    for i in range(len(path) - min_dist - 1):
        for j in range(i + min_dist + 1, len(path)):
            if 2 <= dist(path[i], path[j]) <= max_dist:
                results.append(
                    (path[i], i, path[j], j)
                )
    return results


def dist(a: P, b: P) -> int:
    return abs(b[0] - a[0]) + abs(b[1] - a[1])


def test_find_opposites() -> None:
    path = [
        (1, 1), (1, 2), (1, 3), (2, 3),
        (3, 3), (3, 2), (3, 1)
    ]
    assert find_in_range(path) == [
        ((1, 1), 0, (3, 1), 6),
        ((1, 2), 1, (3, 2), 5),
    ]


EXAMPLE = '''
###############
#...#...#.....#
#.#.#.#.#.###.#
#S#...#.#.#...#
#######.#.#.###
#######.#.#...#
#######.#.###.#
###..E#...#...#
###.#######.###
#...###...#...#
#.#####.#.###.#
#.#...#.#.#...#
#.#.#.#.#.#.###
#...#...#...###
###############'''


def test_load() -> None:
    m = load(StringIO(EXAMPLE))
    assert m.start == (1, 3)
    assert m[m.start] == 'S'


def test_race() -> None:
    m = load(StringIO(EXAMPLE)).solve()
    assert len(m.path) - 1 == 84


def test_cheats() -> None:
    m = load(StringIO(EXAMPLE)).solve()
    s = shortcuts(m.path)
    assert s == {
        2: 14, 4: 14, 6: 2, 8: 4, 10: 2,
        12: 3, 20: 1, 36: 1, 38: 1, 40: 1, 64: 1,
    }


def test_cheats_range_20() -> None:
    m = load(StringIO(EXAMPLE)).solve()
    s = shortcuts(m.path, 20, 50)
    assert {
        k: v for k, v in s.items()
        if k >= 50
    } == {
        50: 32, 52: 31, 54: 29, 56: 39,
        58: 25, 60: 23, 62: 20, 64: 19,
        66: 12, 68: 14, 70: 12, 72: 22,
        74: 4, 76: 3,
    }


if __name__ == '__main__':
    with open('input.txt') as f:
        m = load(f).solve()
    s = shortcuts(m.path, 20, 100)
    print(sum(v for k, v in s.items() if k >= 100))
