from __future__ import annotations

from collections import defaultdict
from io import StringIO, TextIOBase
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
        self.tiles = []

    @property
    def start(self) -> tuple[int, int]:
        y, x = divmod(
            self.tiles.index('S'), self.width
        )
        return x, y

    def __getitem__(self, pos: tuple[int, int]) -> str:
        x, y = pos
        return self.tiles[x+y*self.width]

    def solve(self) -> Path:
        return Pathfinder(self).find().path

    def plot(self, path: Path | None = None) -> str:
        tiles = [
            self.tiles[
                y*self.width:(y+1)*self.width
            ] for y in range(self.height)
        ]
        if path:
            for pos, direction in path.steps:
                x, y = pos
                tiles[y][x] = ARROWS[direction]
        return '\n'.join(
            ''.join(row) for row in tiles
        )

    def __str__(self) -> str:
        return self.plot()


DIRS = [(0, -1), (1, 0), (0, 1), (-1, 0)]
ARROWS = '^>v<'


def step(
    pos: tuple[int, int], direction: int
) -> tuple[int, int]:
    '''
    >>> step((5, 5), -1)
    (4, 5)
    '''
    v = DIRS[direction % 4]
    x, y = map(sum, zip(pos, v))
    return x, y


class Pathfinder:
    Node = NamedTuple(
        'Node', [
            ('parent', tuple[int, int]),
            ('direction', int),
            ('cost', int)
        ]
    )

    def __init__(self, maze: Maze) -> None:
        self.maze = maze
        self.frontier = {
            self.maze.start: (1, 0)
        }
        self.visited = defaultdict(
            lambda: (1, -1)
        )

    def find(self) -> Self:
        while self.frontier:
            pos, node = self.frontier.popitem()
            direction, cost = node
            for turn in range(-1, 2):
                fee = 1 + 999 * abs(turn)
                adj = step(pos, direction + turn)
                if self.maze[adj] == '#':
                    continue
                best_dir, best_cost = self.visited[adj]
                if best_cost < 0:
                    self.frontier[adj] = (
                        direction + turn, cost + fee
                    )
                    continue
                if best_cost > cost + fee:
                    continue
                self.visited[adj] = (
                    direction + turn, cost + fee
                )
            self.visited[pos] = direction, cost
            if self.maze[pos] == 'E':
                self.backtrack(pos)
                break
        return self

    def backtrack(self, pos: tuple[int, int]) -> Self:
        direction, cost = self.visited[pos]
        path = [(pos, direction)]
        while pos != self.maze.start:
            pos = step(pos, direction + 2)
            path.append((pos, direction))
            direction, _ = self.visited[pos]
        self.path = Path(path[::-1], cost)
        return self


class Path:
    def __init__(
        self,
        steps: list[tuple[tuple[int, int], int]],
        cost: int
    ) -> None:
        self.steps = steps
        self.cost = cost

    def __len__(self) -> int:
        return len(self.steps)


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
    assert p.steps == [
        ((1, 2), 1), ((2, 2), 1), ((3, 2), 1),
        ((4, 2), 0), ((4, 1), 0)
    ]


def test_plot_ex1(ex1: StringIO) -> None:
    maze = load(ex1)
    p = maze.solve()
    print(maze.plot(p))
    assert maze.plot(p) == dedent(
        '''\
        ###############
        #.......#....E#
        #.#.###.#.###^#
        #.....#.#...#^#
        #.###.#####.#^#
        #.#.#.......#^#
        #.#.#####.###^#
        #..>>>>>>>>v#^#
        ###^#.#####v#^#
        #>>^#.....#v#^#
        #^#.#.###.#v#^#
        #^....#...#v#^#
        #^###.#.#.#v#^#
        #S..#.....#>>^#
        ###############'''
    )


def test_cost_ex1(ex1: StringIO) -> None:
    maze = load(ex1)
    p = maze.solve()
    assert len(p) == 43
    assert p.cost == 7036
