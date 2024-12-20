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

    def __contains__(self, pos: P) -> bool:
        x, y = pos
        return (
            0 <= x < self.width and
            0 <= y < self.height
        )

    def solve(self) -> Self:
        self.path = Pathfinder(self).find().path
        return self


type P = tuple[int, int]
DIRS = [(0, -1), (1, 0), (0, 1), (-1, 0)]


def step(pos: P, direction: P) -> P:
    x, y = map(sum, zip(pos, direction))
    return x, y


class Pathfinder:
    def __init__(self, maze: Maze) -> None:
        self.maze = maze
        self.visited: dict[P, tuple[P, int]] = {}
        self.frontier = [
            (self.maze.start, (-1, -1), 0)
        ]
        self.path: list[P] = []

    def find(self) -> Self:
        while self.search():
            ...
        return self

    def search(self) -> bool:
        pos, via, cost = self.frontier.pop(0)
        if not self._better(pos, cost):
            return len(self.frontier) > 0
        self.visited[pos] = (via, cost)
        if self.maze[pos] == 'E':
            self.backtrack(pos)
            return False
        for d in DIRS:
            adj = step(pos, d)
            if self._better(adj, cost + 1):
                self.frontier.append((adj, pos, cost + 1))
        return len(self.frontier) > 0

    def backtrack(self, pos: P) -> None:
        path = [pos]
        while (pos := self.visited[pos][0]) in self.maze:
            path.append(pos)
        self.path = path[::-1]

    def _better(self, pos: P, cost: int) -> bool:
        if self.maze[pos] == '#':
            return False
        if pos not in self.visited:
            return True
        return self.visited[pos][1] > cost


def shortcuts(path: list[P]) -> dict[int, int]:
    savings: dict[int, int] = Counter()
    opposites = find_opposites(path)
    for a, b in opposites:
        saves = path.index(b) - path.index(a) - 2
        savings[saves] += 1
    return savings


def find_opposites(path: list[P]) -> list[tuple[P, P]]:
    results = []
    for i in range(len(path) - 3):
        tail = path[i+3:]
        for p in tail:
            if dist(path[i], p) != 2:
                continue
            results.append((path[i], p))
    return results


def dist(a: P, b: P) -> int:
    return abs(b[0] - a[0]) + abs(b[1] - a[1])


def test_find_opposites() -> None:
    path = [
        (1, 1), (1, 2), (1, 3), (2, 3),
        (3, 3), (3, 2), (3, 1)
    ]
    assert find_opposites(path) == [
        ((1, 1), (3, 1)),
        ((1, 2), (3, 2)),
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


if __name__ == '__main__':
    with open('input.txt') as f:
        m = load(f).solve()
    s = shortcuts(m.path)
    print(sum(v for k, v in s.items() if k >= 100))
