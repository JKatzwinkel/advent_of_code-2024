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
        if all(c in '.#@O[]' for c in row):
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
        self._scale = 1

    def scale(self) -> Self:
        self._scale = 2
        cells = []
        for y in range(self.height):
            row = []
            for c in self.cells[
                y*self.width:(y+1)*self.width
            ]:
                if c == 'O':
                    row.extend(['[', ']'])
                else:
                    row.extend([c] * 2)
            cells.extend(row)
        self.cells = cells
        self.width *= 2
        self.robot.pos = (
            self.robot.pos[0] * 2,
            self.robot.pos[1]
        )
        return self

    def pushable_boxes(
        self, pos: tuple[int, int], direction: int
    ) -> set[tuple[tuple[int, int], bool]]:
        boxes = set()
        adj = step(pos, direction)
        if self[adj] == '#':
            return {(pos, False)}
        boxes.add((pos, True))
        if self[adj] == '.':
            return boxes
        if self[adj] in 'O[]':
            boxes.update(
                self.pushable_boxes(adj, direction)
            )
        if direction in [0, 2]:
            if self[adj] == '[':
                boxes.update(
                    self.pushable_boxes(
                        step(adj, 1), direction
                    )
                )
            elif self[adj] == ']':
                boxes.update(
                    self.pushable_boxes(
                        step(adj, 3), direction
                    )
                )
        return boxes

    def push(
        self, pos: tuple[int, int], direction: int
    ) -> bool:
        pushable = self.pushable_boxes(pos, direction)
        if not all(b for _, b in pushable):
            return False
        changes = []
        for p, _ in pushable:
            changes.append((step(p, direction), self[p]))
            self[p] = '.'
        for p, c in changes:
            self[p] = c
        return True

    def gps(self) -> int:
        result = 0
        for i, c in enumerate(self.cells):
            if c not in 'O[':
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
        if '[' in cells:
            self._scale = 2
        self.cells += cells
        self.width = len(cells)
        self.height += 1
        return self

    def __str__(self) -> str:
        lines = [
            self.cells[y*self.width:(y+1)*self.width]
            for y in range(self.height)
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
        if not self.grid.push(self.pos, direction):
            return self
        self.pos = step(self.pos, direction)
        return self


LARGE = '''
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


@pytest.fixture
def large() -> StringIO:
    return StringIO(LARGE)


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
    [(0, True), (1, True), (3, True), (6, False)]
)
def test_boxes_pushed(x: int, pushed: bool) -> None:
    grid = load(StringIO('..O.OO.OOO#'))
    assert grid.push((x, 0), 1) == pushed


def test_push_boxes() -> None:
    grid = load(StringIO('.@OOO.'))
    grid.push((1, 0), 1)
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


def test_scale_large(large: StringIO) -> None:
    grid = load(large).scale()
    assert grid.width == 20
    assert str(grid) == dedent(
        '''\
        ####################
        ##....[]....[]..[]##
        ##............[]..##
        ##..[][]....[]..[]##
        ##....[]@.....[]..##
        ##[]##....[]......##
        ##[]....[]....[]..##
        ##..[][]..[]..[][]##
        ##........[]......##
        ####################'''
    )


def test_push_double_boxes_large(large: StringIO) -> None:
    grid = load(large).scale()
    while grid.robot.moves:
        grid.robot.move()
    expected = dedent(
        '''\
        ####################
        ##[].......[].[][]##
        ##[]...........[].##
        ##[]........[][][]##
        ##[]......[]....[]##
        ##..##......[]....##
        ##..[]............##
        ##..@......[].[][]##
        ##......[][]..[]..##
        ####################'''
    )
    assert str(grid) == expected
    assert grid.gps() == 9021


def test_push_double_boxes() -> None:
    grid = load(StringIO(
        '''
        ##############
        ##......##..##
        ##..........##
        ##...[][]...##
        ##....[]....##
        ##.....@....##
        ##############'''
    ))
    grid.robot.move('^')
    grid.robot.move('^')
    assert str(grid) == dedent(
        '''\
        ##############
        ##......##..##
        ##...[][]...##
        ##....[]....##
        ##.....@....##
        ##..........##
        ##############'''
    )


def test_push_double_boxes_2() -> None:
    grid = load(StringIO(
        '''
        ##############
        ##......##..##
        ##..........##
        ##....[][]@.##
        ##....[]....##
        ##..........##
        ##############
        <vv<<^^<<^^'''
    ))
    while grid.robot.moves:
        grid.robot.move()
    assert str(grid) == dedent(
        '''\
        ##############
        ##...[].##..##
        ##...@.[]...##
        ##....[]....##
        ##..........##
        ##..........##
        ##############'''
    )


def test_push_double_boxes_3() -> None:
    grid = load(StringIO(
        '''
        ####################
        ##....[]....[]..[]##
        ##............[]..##
        ##..[][]....[]..[]##
        ##...[].......[]..##
        ##[]##....[]......##
        ##[]......[]..[]..##
        ##..[][]..@[].[][]##
        ##........[]......##
        ####################'''
    ))
    grid.robot.move('^')
    assert str(grid) == dedent(
        '''\
        ####################
        ##....[]....[]..[]##
        ##............[]..##
        ##..[][]....[]..[]##
        ##...[]...[]..[]..##
        ##[]##....[]......##
        ##[]......@...[]..##
        ##..[][]...[].[][]##
        ##........[]......##
        ####################'''
    )


def test_input_part2() -> None:
    with open('input.txt') as f:
        grid = load(f).scale()
    while grid.robot.moves:
        grid.robot.move()
    assert grid.gps() == 1509724


if __name__ == '__main__':
    import time
    grid = load(StringIO(LARGE)).scale()
    print(f'{grid}')
    while grid.robot.moves:
        grid.robot.move()
        for i in range(grid.height):
            print(
                f'\033[A{" " * grid.width}\033[A'
            )
        print(f'{grid}')
        time.sleep(.02)
