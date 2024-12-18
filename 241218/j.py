from __future__ import annotations

from io import StringIO, TextIOBase
from textwrap import dedent
from typing import Self


EXAMPLE = '''
    5,4
    4,2
    4,5
    3,0
    2,1
    6,3
    2,4
    1,5
    0,6
    3,3
    2,6
    5,1
    1,2
    5,5
    2,5
    6,5
    1,4
    0,4
    6,4
    1,1
    6,1
    1,0
    0,5
    1,6
    2,0'''


def load(src: TextIOBase, width: int) -> Mem:
    positions = [
        eval(line) for line in src if len(line.strip())
    ]
    return Mem(width, positions)


class Mem:
    def __init__(
        self, width: int, falling_bytes: list[P]
    ) -> None:
        self.width = width
        self.falling = falling_bytes
        self.corrupted: set[P] = set()

    def fall(self, times: int = 1) -> Self:
        while times > 0 and self.falling:
            self.corrupted.add(self.falling.pop(0))
            times -= 1
        return self

    def escape(self) -> list[P]:
        return Pathfinder(self).find().result

    def __getitem__(self, pos: P) -> bool:
        return pos in self.corrupted

    def __contains__(self, pos: P) -> bool:
        x, y = pos
        return 0 <= x < self.width and 0 <= y < self.width

    def __str__(self) -> str:
        lines = [
            ['.'] * self.width for y in range(self.width)
        ]
        for x, y in self.corrupted:
            lines[y][x] = '#'
        return '\n'.join(
            ''.join(line) for line in lines
        )


type P = tuple[int, int]
DIRS = [(0, -1), (1, 0), (0, 1), (-1, 0)]


def step(pos: P, direction: tuple[int, int]) -> P:
    '''
    >>> step((1, 1), (0, -1))
    (1, 0)
    '''
    x, y = map(sum, zip(pos, direction))
    return x, y


def dist(a: P, b: P) -> int:
    '''
    >>> dist((1, 2), (5, 0))
    6
    '''
    dx, dy = map(lambda t: t[1]-t[0], zip(a, b))
    return abs(dx) + abs(dy)


class Pathfinder:
    def __init__(self, mem: Mem) -> None:
        self.m = mem
        self.visited: dict[P, tuple[P, int]] = {}
        self.frontier = [((0, 0), (0, 0), 0)]
        self.target = (mem.width - 1, mem.width - 1)
        self.result: list[P] = []

    def find(self, target: P | None = None) -> Self:
        self.target = target or self.target
        while self.search():
            ...
        return self

    def search(self) -> bool:
        node = min(self.frontier, key=self._score)
        pos, via, cost = self.frontier.pop(self.frontier.index(node))
        if not self._improves(pos, cost):
            return len(self.frontier) > 0
        self.visited[pos] = (via, cost)
        if pos == self.target:
            self.backtrack(pos)
            return False
        for direction in DIRS:
            adj = step(pos, direction)
            if adj == via:
                continue
            if self._improves(adj, cost + 1):
                self.frontier.append(
                    (adj, pos, cost + 1)
                )
        return len(self.frontier) > 0

    def backtrack(self, pos: P) -> None:
        path = []
        while pos != (0, 0):
            path.append(pos)
            pos, _ = self.visited[pos]
        self.result = path[::-1]

    def _score(self, node: tuple[P, P, int]) -> int:
        pos, via, cost = node
        return cost + dist(pos, self.target)

    def _improves(self, pos: P, cost: int) -> bool:
        if pos not in self.m or self.m[pos]:
            return False
        if pos not in self.visited:
            return True
        return self.visited[pos][1] > cost


def test_load() -> None:
    mem = load(StringIO(EXAMPLE), 7)
    mem.fall(2)
    assert not mem[0, 0]
    assert mem[5, 4]
    assert mem[4, 2]


def test_plot() -> None:
    mem = load(StringIO(EXAMPLE), 7)
    mem.fall(12)
    assert f'{mem}' == dedent(
        '''\
        ...#...
        ..#..#.
        ....#..
        ...#..#
        ..#..#.
        .#..#..
        #.#....'''
    ), f'{mem}'


def test_pathfinder() -> None:
    mem = load(StringIO('1, 0\n1, 1'), 3).fall(2)
    pf = Pathfinder(mem).find((2, 2))
    assert len(pf.result) == 4


def test_pathfinder_example() -> None:
    mem = load(StringIO(EXAMPLE), 7)
    mem.fall(12)
    p = mem.escape()
    assert len(p) == 22, f'{p}'


def test_input_part1() -> None:
    with open('input.txt') as f:
        mem = load(f, 71)
    mem.fall(1024)
    p = mem.escape()
    assert len(p) == 282


if __name__ == '__main__':
    with open('input.txt') as f:
        mem = load(f, 71)
    mem.fall(1024)
    print(f'{mem}')
    while (path := mem.escape()):
        skip = 0
        while mem.falling[skip] not in path:
            skip += 1
        if skip:
            mem.fall(skip)
        pos = mem.falling[0]
        mem.fall()
        print(
            '\n'.join(
                [f"\033[A{' ' * mem.width}\033[A"] * mem.width
            )
        )
        print(f'{mem}')
    print(f'{pos}. {len(mem.falling)} remaining')
