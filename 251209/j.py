from functools import reduce
from itertools import combinations, dropwhile, product
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


def out(corner: list[Point]) -> Point:
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


def rect(a: Point, b: Point) -> list[Point]:
    '''
    >>> rect((2, 5), (9, 7))
    [(2, 5), (2, 7), (9, 5), (9, 7)]
    '''
    return list(product(*zip(a, b)))  # type: ignore


def fence(posts: list[Point]) -> dict[Point, Point]:
    '''
    >>> f = fence(load(X))
    >>> f[7, 1]
    (-1, -1)
    '''
    result = dict()
    posts = [posts[-1]] + posts
    for i in range(1, len(posts) - 1):
        result[posts[i]] = out(posts[i-1:i+2])
    return result


def go(p: Point, v: Point) -> Point:
    '''
    >>> go((7, 1), (-1, -1))
    (6, 0)
    '''
    return p[0] + v[0], p[1] + v[1]


def outside(
    a: Point, b: Point, facing: dict[Point, Point]
) -> bool:
    box = rect(a, b)
    for p in box:



def bigrect_inside(points: list[Point]) -> tuple[int, Point, Point]:
    '''
    >>> bigrect_inside(load(X))
    (24, (9, 5), (2, 3))
    '''
    pairs = sorted(
        combinations(points, 2), key=lambda p: area(*p),
        reverse=True,
    )
    f = fence(points)
    pairs = dropwhile(lambda pair: outside(*pair, f), pairs)
    a, b = pairs[0]
    return area(a, b), a, b


if __name__ == '__main__':
    a, p, q = bigrect(load(Path('input.txt').read_text()))
    print(f'{a}m² between {p} ⊞ {q}')
