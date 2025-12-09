from functools import reduce
from itertools import combinations
from pathlib import Path

X = '''
7,1
11,1
11,7
9,7
9,5
2,5
2,3
7,3'''

F = '''
..............
.......#XXX#..
.......X...X..
..#XXXX#...X..
..X........X..
..#XXXXXX#.X..
.........X.X..
.........#X#..
..............
'''


type Point = tuple[int, int]


def load(src: str) -> list[Point]:
    '''
    >>> load(X)[0]
    (7, 1)
    '''
    return [
        tuple(map(int, line.split(',')))  # type: ignore
        for line in src.split()
    ]


def area(a: Point, b: Point) -> int:
    '''
    >>> area((2, 5), (9, 7))
    24

    >>> area((7, 1), (11, 7))
    35

    >>> area((7, 3), (2, 3))
    6

    >>> area((2, 5), (11, 1))
    50
    '''
    w, h = [
        reduce(int.__sub__, sorted((a[i], b[i]), reverse=True))
        for i in (0, 1)
    ]
    return (w + 1) * (h + 1)


def bigrect(points: list[Point]) -> tuple[int, Point, Point]:
    '''
    >>> bigrect(load(X))[0]
    50
    '''
    pairs = sorted(combinations(points, 2), key=lambda p: area(*p))
    a, b = pairs[-1]
    return area(a, b), a, b


def sig(n: int) -> int:
    '''
    >>> sig(-4)
    -1
    >>> sig(0)
    0
    >>> sig(1)
    1
    '''
    if n == 0:
        return 0
    return n // abs(n)


def left(a: Point, b: Point) -> Point:
    '''
    >>> left((7, 1), (11, 1))
    (0, -1)

    >>> left((7, 3), (7, 1))
    (-1, 0)

    >>> left((11, 1), (11, 7))
    (1, 0)

    >>> left((9, 5), (2, 5))
    (0, 1)
    '''
    return sig(b[1] - a[1]), sig(a[0] - b[0])


def out(corner: tuple[Point, Point, Point]) -> Point:
    '''
    >>> pp = load(X)
    >>> out(pp[:3])
    (1, -1)
    >>> out(pp[1:4])
    (1, 1)
    >>> out(pp[2:5])
    (-1, 1)
    '''
    return tuple(  # type: ignore
        w + v for w, v in zip(
            left(*corner[:2]), left(*corner[1:3])
        )
    )


if __name__ == '__main__':
    a, p, q = bigrect(load(Path('input.txt').read_text()))
    print(f'{a}m² between {p} ⊞ {q}')
