from __future__ import annotations

from io import StringIO, TextIOBase
from textwrap import dedent
from typing import Self

import pytest


def load(src: TextIOBase) -> Grid:
    grid = Grid()
    moves = []
    for line in src:
        if not (row := line.strip()):
            continue
        if all(c in '.#@O' for c in row):
            grid += [c for c in row]
        else:
            moves.extend([c for c in row])
    grid.robot.moves = moves
    return grid


class Grid:
    def __init__(self) -> None:
        self.width = 0
        self.height = 0
        self.cells: list[str] = []
        self.robot = Robot(self, -1, -1)

    def boxes_pushed(
        self, pos: tuple[int, int], direction: int
    ) -> int:
        boxes = 0
        while self[(pos := step(pos, direction))] == 'O':
            boxes += 1
        if self[pos] == '#':
            return -1
        return boxes

    def push_boxes(
        self, pos: tuple[int, int], direction: int,
        boxes: int
    ) -> Self:
        self[step(pos, direction)] = '.'
        self[step(pos, direction, boxes + 1)] = 'O'
        return self

    def gps(self) -> int:
        result = 0
        for i, c in enumerate(self.cells):
            if c != 'O':
                continue
            y, x = divmod(i, self.width)
            result += y * 100 + x
        return result

    def __getitem__(self, pos: tuple[int, int]) -> str:
        x, y = pos
        return self.cells[x + y * self.width]

    def __setitem__(
        self, pos: tuple[int, int], value: str
    ) -> None:
        x, y = pos
        self.cells[x + y * self.width] = value

    def __add__(self, cells: list[str]) -> Self:
        if '@' in cells:
            self.robot = Robot(
                self, cells.index('@'), self.height
            )
            cells = (
                cells[:cells.index('@')] + ['.']
                + cells[cells.index('@')+1:]
            )
        self.cells += cells
        self.width = len(cells)
        self.height += 1
        return self

    def __str__(self) -> str:
        lines = [
            self.cells[i*self.width:(i+1)*self.width]
            for i in range(self.height)
        ]
        lines[self.robot.pos[1]][self.robot.pos[0]] = '@'
        return '\n'.join(
            ''.join(line) for line in lines
        )


DIRS = [(0, -1), (1, 0), (0, 1), (-1, 0)]


def step(
    pos: tuple[int, int], direction: int,
    times: int = 1
) -> tuple[int, int]:
    x, y = pos
    dx, dy = DIRS[direction]
    return x + dx * times, y + dy * times


class Robot:
    MOVES = '^>v<'

    def __init__(self, grid: Grid, x: int, y: int) -> None:
        self.grid = grid
        grid.robot = self
        self.pos = (x, y)
        self.moves: list[str] = []

    def move(self, move: str = '') -> Self:
        direction = self.__class__.MOVES.index(
            move or self.moves.pop(0)
        )
        if (
            effect := self.grid.boxes_pushed(
                self.pos, direction
            )
        ) < 0:
            return self
        if effect:
            self.grid.push_boxes(
                self.pos, direction, effect
            )
        self.pos = step(self.pos, direction)
        return self


@pytest.fixture
def large() -> StringIO:
    return StringIO(
        '''
        ##########
        #..O..O.O#
        #......O.#
        #.OO..O.O#
        #..O@..O.#
        #O#..O...#
        #O..O..O.#
        #.OO.O.OO#
        #....O...#
        ##########

        <vv>^<v^>v>^vv^v>v<>v^v<v<^vv<<<^><<><>>v<vvv<>^v^>^<<<><<v<<<v^vv^v>^
        vvv<<^>^v^^><<>>><>^<<><^vv^^<>vvv<>><^^v>^>vv<>v<<<<v<^v>^<^^>>>^<v<v
        ><>vv>v^v^<>><>>>><^^>vv>v<^^^>>v^v^<^^>v^^>v^<^v>v<>>v^v^<v>v^^<^^vv<
        <<v<^>>^^^^>>>v^<>vvv^><v<<<>^^^vv^<vvv>^>v<^^^^v<>^>vvvv><>>v^<<^^^^^
        ^><^><>>><>^^<<^^v>>><^<v>^<vv>>v>>>^v><>^v><<<<v>>v<v<v>vvv>^<><<>^><
        ^>><>^v<><^vvv<^^<><v<<<<<><^v<<<><<<^^<v<^^^><^>>^<v^><<<^>>^v<v^v<v^
        >^>>^v>vv>^<<^v<>><<><<v<<v><>v<^vv<<<>^^v^>^^>>><<^v>>v^v><^^>>^<>vv^
        <><^^>^^^<><vvvvv^v<v<<>^v<v>v<<^><<><<><<<^^<<<^<<>><<><^^^>^^<>^>v<>
        ^^>vv<^v^v<vv>^<><v<^v>^^^>>>^^vvv^>vvv<>>>^<^>>>>>^<<^v>^vvv<>^<><<v>
        v^^>>><<^^<>>^v^<v^vv<>v^<<>^<^v^v><^<<<><<^<v><v<>vv>>v><v^<vv<>v^<<^
        '''
    )


@pytest.fixture
def small() -> StringIO:
    return StringIO(
        '''
        ########
        #..O.O.#
        ##@.O..#
        #...O..#
        #.#.O..#
        #...O..#
        #......#
        ########

        <^^>>>vv<v>>v<<'''
    )


def test_load(small: StringIO) -> None:
    grid = load(small)
    assert grid.width == grid.height == 8
    assert grid[3, 1] == 'O'
    assert grid.robot.pos == (2, 2)
    assert len(grid.robot.moves) == 15


@pytest.mark.parametrize(
    'x, pushed',
    [(0, 0), (1, 1), (3, 2), (6, -1)]
)
def test_boxes_pushed(x: int, pushed: int) -> None:
    grid = load(StringIO('..O.OO.OOO#'))
    assert grid.boxes_pushed((x, 0), 1) == pushed


def test_push_boxes() -> None:
    grid = load(StringIO('.@OOO.'))
    grid.push_boxes(
        (1, 0), 1, grid.boxes_pushed((1, 0), 1)
    )
    assert str(grid) == '.@.OOO'


def test_plot() -> None:
    txt = '''\
    #####
    #.O.#
    #...#
    #@..#
    #####'''
    grid = load(StringIO(txt))
    assert str(grid) == dedent(txt)


def test_move(small: StringIO) -> None:
    grid = load(small)
    assert grid.robot.move().pos == (2, 2)
    assert len(grid.robot.moves) == 14
    assert grid.robot.move('v').pos == (2, 3)
    assert len(grid.robot.moves) == 14


def test_walk(small: StringIO) -> None:
    grid = load(small)
    while grid.robot.moves:
        grid.robot.move()
    assert str(grid) == dedent(
        '''\
        ########
        #....OO#
        ##.....#
        #.....O#
        #.#O@..#
        #...O..#
        #...O..#
        ########'''
    )
    assert grid.gps() == 2028


def test_large_walk(large: StringIO) -> None:
    grid = load(large)
    while grid.robot.moves:
        grid.robot.move()
    assert str(grid) == dedent(
        '''\
        ##########
        #.O.O.OOO#
        #........#
        #OO......#
        #OO@.....#
        #O#.....O#
        #O.....OO#
        #O.....OO#
        #OO....OO#
        ##########'''
    )
    assert grid.gps() == 10092


def test_input_part1() -> None:
    with open('input.txt') as f:
        grid = load(f)
    while grid.robot.moves:
        grid.robot.move()
    assert grid.gps() == 1475249
