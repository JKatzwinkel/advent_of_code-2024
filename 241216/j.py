from __future__ import annotations

from collections import defaultdict
from functools import reduce
from io import StringIO, TextIOBase
import itertools
from textwrap import dedent
from typing import NamedTuple, Self

import pytest


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
    def start(self) -> tuple[int, int]:
        y, x = divmod(
            self.tiles.index('S'), self.width
        )
        return x, y

    def __getitem__(self, pos: tuple[int, int]) -> str:
        x, y = pos
        try:
            return self.tiles[x+y*self.width]
        except IndexError:
            raise IndexError(
                f'out of bounds: {pos}'
            )

    def solve(self) -> Path:
        return Pathfinder(self).find().path

    def plot(
        self, path: Path | None = None,
        ansi: bool = True,
    ) -> str:
        tiles = self._lines()
        if path:
            tmpl = '\033[32m{}\033[00m' if ansi else '{}'
            for q, p in zip(
                path.steps[1:], path.steps[:-1]
            ):
                d = direction(p, q)
                x, y = p
                if tiles[y][x] in 'SE':
                    continue
                tiles[y][x] = tmpl.format(
                    ARROWS[d]
                )
        return '\n'.join(
            ''.join(row) for row in tiles
        )

    def _lines(self) -> list[list[str]]:
        return [
            self.tiles[
                y*self.width:(y+1)*self.width
            ] for y in range(self.height)
        ]


DIRS = [(0, -1), (1, 0), (0, 1), (-1, 0)]
ARROWS = '^>v<'

type P = tuple[int, int]


def step(
    pos: P, direction: int
) -> tuple[int, int]:
    '''
    >>> step((5, 5), -1)
    (4, 5)
    '''
    v = DIRS[direction % 4]
    x, y = map(sum, zip(pos, v))
    return x, y


def direction(a: P, b: P) -> int:
    '''
    >>> direction((4, 2), (3, 2))
    3
    >>> direction((3, 3), (3, 2))
    0
    '''
    dx, dy = b[0] - a[0], b[1] - a[1]
    v = (
        0 if not dx else dx // abs(dx),
        0 if not dy else dy // abs(dy),
    )
    return DIRS.index(v)


class Pathfinder:
    def __init__(self, maze: Maze) -> None:
        self.maze = maze
        start = self.maze.start
        self.frontier = [(start, step(start, 3), 0)]
        self.visited: dict[
            P, set[tuple[P, int]]
        ] = defaultdict(set)
        self.results: set[Path] = set()

    def find(self) -> Self:
        while self.frontier:
            self.search()
        return self

    def search(self) -> bool:
        self.frontier.remove(
            candidate := min(
                self.frontier, key=lambda c: c[2]
            )
        )
        pos, prev, cost = candidate
        # print(f'visiting {pos} from {prev} for {cost}')
        if self.is_improvement(pos, cost):
            self.visited[pos].add(
                (prev, cost)
            )
            if self.maze[pos] == 'E':
                self.backtrack(pos, cost)
                return True
        d = direction(prev, pos)
        for t in range(-1, 2):
            steppy = step(pos, d + t)
            steppy_cost = cost + 1 + abs(t) * 1000
            if not self.is_improvement(
                steppy, steppy_cost
            ):
                continue
            self.frontier.append(
                (steppy, pos, steppy_cost)
            )
        return True

    def is_improvement(self, pos: P, cost: int) -> bool:
        if self.maze[pos] == '#':
            return False
        if pos not in self.visited:
            return True
        best = min(
            self.visited[pos], key=lambda t: t[1]
        )[1]
        return cost <= best

    def backtrack(self, pos: P, cost: int) -> Self:
        for path in self._backtrack(
            pos, [Path([pos], 0)]
        ):
            self.results.add(
                Path(path.steps[1:], path.cost - 1)
            )
        cheapest = min(
            path.cost for path in self.results
        )
        self.results = set([
            path for path in self.results
            if path.cost == cheapest
        ])
        print('results: ', self.results)
        return self

    def _backtrack(
        self, pos: P, paths: list[Path]
    ) -> list[Path]:
        # print('pos: ', pos)
        # print('paths: ', paths)
        origins = self.visited[pos]
        if not origins:
            return paths
        # print('origins: ', origins)
        cheapest = min(t[1] for t in origins)
        prevs = [
            t[0] for t in origins if t[1] == cheapest
        ]
        paths = reduce(
            list.__add__,
            (
                self._backtrack(
                    prev, [
                        path.prepend(prev)
                        for prev, path
                        in itertools.product(
                            [prev], paths
                        )
                    ]
                )
                for prev in prevs
            )
        )
        return paths

    @property
    def path(self) -> Path:
        return min(self.results, key=lambda p: p.cost)


class Path:
    def __init__(
        self,
        steps: list[P],
        cost: int
    ) -> None:
        self.steps = steps
        self.cost = cost

    def prepend(self, pos: P) -> Path:
        cost = 1
        if len(self.steps) > 1:
            cur_dir = direction(
                self.steps[0], self.steps[1]
            )
            new_dir = direction(
                pos, self.steps[0]
            )
            if cur_dir != new_dir:
                cost += 1000
        return Path(
            [pos] + self.steps, self.cost + cost
        )

    def __len__(self) -> int:
        return len(self.steps)

    def __repr__(self) -> str:
        return f'Path<{self.steps}, {self.cost}>'

    def __eq__(self, o: object) -> bool:
        assert type(o) is Path
        return f'{self}' == f'{o}'

    def __hash__(self) -> int:
        return hash(tuple(self.steps)) * self.cost


@pytest.fixture
def ex1() -> StringIO:
    return StringIO(
        '''
        ###############
        #.......#....E#
        #.#.###.#.###.#
        #.....#.#...#.#
        #.###.#####.#.#
        #.#.#.......#.#
        #.#.#####.###.#
        #...........#.#
        ###.#.#####.#.#
        #...#.....#.#.#
        #.#.#.###.#.#.#
        #.....#...#.#.#
        #.###.#.#.#.#.#
        #S..#.....#...#
        ###############'''
    )


@pytest.fixture
def ex2() -> StringIO:
    return StringIO(
        '''
        #################
        #...#...#...#..E#
        #.#.#.#.#.#.#.#.#
        #.#.#.#...#...#.#
        #.#.#.#.###.#.#.#
        #...#.#.#.....#.#
        #.#.#.#.#.#####.#
        #.#...#.#.#.....#
        #.#.#####.#.###.#
        #.#.#.......#...#
        #.#.###.#####.###
        #.#.#...#.....#.#
        #.#.#.#####.###.#
        #.#.#.........#.#
        #.#.#.#########.#
        #S#.............#
        #################'''
    )


def test_load(ex1: TextIOBase) -> None:
    maze = load(ex1)
    assert maze[maze.start] == 'S'


def test_solve() -> None:
    maze = load(StringIO(
        '''
        ######
        #..#E#
        #S...#
        ######'''
    ))
    pf = Pathfinder(maze).find()
    assert (4, 1) in pf.visited
    p = maze.solve()
    assert p.cost == 1004
    assert p.steps == [
        (1, 2), (2, 2), (3, 2),
        (4, 2), (4, 1)
    ]
    # assert p.steps == [
    #     ((1, 2), 1), ((2, 2), 1), ((3, 2), 1),
    #     ((4, 2), 0), ((4, 1), 0)
    # ]


def test_paths() -> None:
    maze = load(StringIO(
        '''
        ######
        #...E#
        #...##
        #S..##
        ######'''
    ))
    pf = Pathfinder(maze).find()
    assert len(pf.results) == 3


def expect(
    maze: Maze, path: Path, expected: str
) -> None:
    actual = maze.plot(path)
    side_by_side = zip(
        dedent(expected).split('\n'),
        actual.split('\n'),
    )
    out = '\n'.join(
        [' | '.join(sides) for sides in side_by_side]
    )
    assert maze.plot(
        path, ansi=False
    ) == dedent(expected), (
        f'expected | got\n{out}'
    )


def test_plot_ex1(ex1: StringIO) -> None:
    maze = load(ex1)
    p = maze.solve()
    expect(
        maze, p,
        '''\
        ###############
        #.......#....E#
        #.#.###.#.###^#
        #.....#.#...#^#
        #.###.#####.#^#
        #.#.#.......#^#
        #.#.#####.###^#
        #....>>>>>>v#^#
        ###.#^#####v#^#
        #...#^....#v#^#
        #.#.#^###.#v#^#
        #>>>>^#...#v#^#
        #^###.#.#.#v#^#
        #S..#.....#>>^#
        ###############'''
    )


def test_cost_ex1(ex1: StringIO) -> None:
    maze = load(ex1)
    pf = Pathfinder(maze).find()
    assert len(pf.results) == 0
    p = maze.solve()
    assert p.cost == 7036


def test_cost_ex2(ex2: StringIO) -> None:
    maze = load(ex2)
    p = maze.solve()
    assert p.cost == 11048, maze.plot(p)


def test_best_path() -> None:
    maze = load(StringIO(
        '''#######
           #....E#
           #.###.#
           #...#.#
           #S#...#
           #######'''
    ))
    p = maze.solve()
    expect(
        maze, p,
        '''\
           #######
           #>>>>E#
           #^###.#
           #^..#.#
           #S#...#
           #######'''
    )


def test_input() -> None:
    with open('input.txt') as f:
        maze = load(f)
    p = maze.solve()
    assert p.cost == 160624


if __name__ == '__main__':
    with open('input.txt') as f:
        maze = load(f)
    p = maze.solve()
    print(maze.plot(p))
    print(p.cost)
