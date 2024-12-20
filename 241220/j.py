from __future__ import annotations

from io import StringIO, TextIOBase


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
