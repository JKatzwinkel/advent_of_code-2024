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
        self.tiles: list[str] = []

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

    def plot(
        self, path: Path | None = None,
        ansi: bool = True,
    ) -> str:
        tiles = self._lines()
        if path:
            tmpl = '\033[32m{}\033[00m' if ansi else '{}'
            for pos, direction in path.steps:
                x, y = pos
                if tiles[y][x] in 'SE':
                    continue
                tiles[y][x] = tmpl.format(
                    ARROWS[direction]
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
            ('direction', int),
            ('cost', int)
        ]
    )

    def __init__(self, maze: Maze) -> None:
        self.maze = maze
        self.frontier = {
            self.maze.start: self.__class__.Node(1, 0)
        }
        self.visited: dict[
            tuple[int, int], Pathfinder.Node
        ] = {}
        self.results: list[Path] = []

    def _probe(
        self, pos: tuple[int, int], direction: int,
        cost: int
    ) -> None:
        if self.maze[pos] == '#':
            return
        current = self.frontier.get(
            pos, self.visited.get(pos)
        )
        if not current or current.cost > cost:
            self.frontier[pos] = self.__class__.Node(
                direction, cost
            )

    def go(self) -> Self:
        pos, node = min(
            self.frontier.items(), key=lambda t: t[1][1]
        )
        self.frontier.pop(pos)
        current = self.visited.get(pos)
        if not current or current.cost > node.cost:
            self.visited[pos] = self.__class__.Node(
                node.direction, node.cost
            )
        if self.maze[pos] == 'E':
            self.backtrack(pos)
            return self
        for turn in range(-1, 2):
            fee = 1 + 1000 * abs(turn)
            adj = step(pos, node.direction + turn)
            self._probe(
                adj, node.direction + turn,
                node.cost + fee
            )
        return self

    def find(self) -> Self:
        while self.frontier:
            self.go()
        return self

    def backtrack(self, pos: tuple[int, int]) -> Self:
        direction, cost = self.visited[pos]
        path = [(pos, direction)]
        while pos != self.maze.start:
            pos = step(pos, direction + 2)
            path.append((pos, direction))
            direction, _ = self.visited[pos]
        self.results.append(Path(path[::-1], cost))
        return self

    @property
    def path(self) -> Path:
        return min(self.results, key=lambda p: p.cost)

    def __str__(self) -> str:
        def _plot(
            nodes: dict[tuple[int, int], Pathfinder.Node],
            ansi: str
        ) -> None:
            for pos, node in nodes.items():
                x, y = pos
                direction, cost = node
                lines[y][x] = (
                    f'{ansi}'
                    f'{ARROWS[direction % 4]}{cost:>4}'
                    '\033[0m'
                )
        lines = [
            [tile * 5 for tile in line]
            for line in self.maze._lines()
        ]
        _plot(self.visited, '\033[32m')
        _plot(self.frontier, '\033[34m')
        return '\n'.join(
            ' '.join(line) for line in lines
        )


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
    p = maze.solve()
    assert p.cost == 7036


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


if __name__ == '__main__':
    maze = load(StringIO(
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
    ))
    pf = Pathfinder(maze).find()
    print(maze.plot(pf.path))
