from __future__ import annotations
import pathlib


X = '''\
..@@.@@@@.
@@@.@.@.@@
@@@@@.@.@@
@.@@@@..@.
@@.@@@@.@@
.@@@@@@@.@
.@.@.@.@@@
@.@@@.@@@@
.@@@@@@@@.
@.@.@@@.@.'''

S = '''\
..xx.xx@x.
x@@.@.@.@@
@@@@@.x.@@
@.@@@@..@.
x@.@@@@.@x
.@@@@@@@.@
.@.@.@.@@@
x.@@@.@@@@
.@@@@@@@@.
x.x.@@@.x.'''

D = '''\
..........
..........
...x@@....
...@@@@...
...@@@@@..
...@.@.@@.
...@@.@@@.
...@@@@@..
....@@@...'''


def load(text: str) -> Grid:
    '''
    >>> g=load(X)
    >>> g.dimensions
    (10, 10)
    '''
    return Grid(text.split())


class Grid:
    '''
    >>> g=Grid(X.split())
    >>> g[2,0]
    '@'
    >>> g.adjacent_rolls((2, 0))
    3
    '''
    def __init__(self, rows: list[str]):
        self.data = ''.join(rows)
        self.width = max(map(len, rows))
        self.height = len(rows)

    def __getitem__(self, pos: tuple[int, int]) -> str:
        if pos not in self:
            return ''
        x, y = pos
        return self.data[x+y*self.width]

    def __setitem__(self, pos: tuple[int, int], s: str) -> None:
        if pos not in self:
            return
        x, y = pos
        i = x+y*self.width
        self.data = self.data[:i] + s[:1] + self.data[i+1:]

    def __contains__(self, pos: tuple[int, int]) -> bool:
        x, y = pos
        return 0 <= x < self.width and 0 <= y < self.height

    @property
    def dimensions(self) -> tuple[int, int]:
        return (self.width, self.height)

    def adjacent_rolls(self, pos: tuple[int, int]) -> int:
        count = 0 - int(self[pos] == '@')
        x, y = pos
        for xv in range(max(0, x-1), min(self.width, x+2)):
            for yv in range(max(0, y-1), min(self.height, y+2)):
                if self[xv, yv] == '@':
                    count += 1
                if count == 4:
                    return count
        return count

    def find_accessibles(self) -> list[tuple[int, int]]:
        result = []
        for y in range(self.height):
            for x in range(self.width):
                if self[x, y] != '@':
                    continue
                if self.adjacent_rolls((x, y)) < 4:
                    result.append((x, y))
        return result

    def remove(self, xx: list[tuple[int, int]]) -> Grid:
        result: Grid = self.__class__.__new__(self.__class__)
        result.width = self.width
        result.height = self.height
        result.data = self.data
        for x in xx:
            result[x] = 'x'
        return result

    def __str__(self) -> str:
        rows = [
            self.data[y*self.width:(y+1)*self.width]
            for y in range(self.height)
        ]
        return '\n'.join(rows)


def test_io() -> None:
    g = load(X)
    assert f'{g}' == X


def test_part1() -> None:
    g = load(X)
    assert len(g.find_accessibles()) == 13


def test_rm() -> None:
    g = load(X)
    c = g.remove(g.find_accessibles())
    assert f'{c}' == S


def work(g: Grid) -> tuple[Grid, int]:
    '''
    >>> c, r = work(load(X))
    >>> r
    13
    '''
    axs = g.find_accessibles()
    c = g.remove(axs)
    return (c, len(axs))


def test_being_done() -> None:
    g = load(D)
    c, r = work(g)
    assert not r, f'{c}'


def workywork(g: Grid) -> list[int]:
    '''
    >>> workywork(load(X))
    [13, 12, 7, 5, 2, 1, 1, 1, 1]

    >>> sum(workywork(load(X)))
    43
    '''
    steps = []
    c, r = work(g)
    while r:
        steps.append(r)
        c, r = work(c)
    return steps


if __name__ == '__main__':
    g = load(pathlib.Path('input.txt').read_text())
    print(len(g.find_accessibles()))
    print(sum(workywork(g)))
