from __future__ import annotations


X = '''
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

S = '''
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

    def find_accessables(self) -> list[tuple[int, int]]:
        result = []
        for y in range(self.height):
            for x in range(self.width):
                if self[x, y] != '@':
                    continue
                if self.adjacent_rolls((x, y)) < 4:
                    result.append((x, y))
        return result


def test_part1() -> None:
    g = load(X)
    assert len(g.find_accessables()) == 13
