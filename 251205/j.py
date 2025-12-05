import pathlib

import pytest


X = '''\
3-5
10-14
16-20
12-18

1
5
8
11
17
32'''


def load(src: str) -> tuple[list[tuple[int, int]], list[int]]:
    '''
    >>> rr, ii = load(X)
    >>> rr[-1]
    (12, 18)
    >>> ii[-1]
    32
    '''
    ranges = []
    iids = []
    for line in src.split():
        if '-' not in line:
            iids.append(int(line))
            continue
        a, b = list(map(int, line.split('-')))
        ranges.append((a, b))
    return ranges, iids


def isfresh(ingredient: int, ranges: list[tuple[int, int]]) -> bool:
    return any(a <= ingredient <= b for a, b in ranges)


@pytest.mark.parametrize(
    'ingredient,expected', (
        (1, False), (5, True), (8, False), (11, True), (17, True), (32, False),
    )
)
def test_freshnesz(ingredient: int, expected: bool) -> None:
    ranges, _ = load(X)
    assert isfresh(ingredient, ranges) is expected


def count_fresh(ingredients: list[int], ranges: list[tuple[int, int]]) -> int:
    '''
    >>> rr, ii = load(X)
    >>> count_fresh(ii, rr)
    3
    '''
    return sum(isfresh(i, ranges) for i in ingredients)


def overlap(r1: tuple[int, int], r2: tuple[int, int]) -> bool:
    '''
    >>> overlap((1, 3), (5, 6))
    False
    >>> overlap((1, 3), (0, 4))
    True
    >>> overlap((1, 3), (4, 5))
    True
    >>> overlap((1, 4), (2, 3))
    True
    >>> overlap((2, 6), (5, 8))
    True
    '''
    (a, b), (c, d) = sorted([r1, r2])
    return c < b + 2


def fold(ranges: list[tuple[int, int]]) -> list[tuple[int, int]]:
    '''
    >>> fold([(2, 4), (3, 5), (4, 6)])
    [(2, 6)]
    '''
    result = [ranges[0]]
    for a, b in ranges[1:]:
        if overlap((a, b), (r := result[-1])):
            result[-1] = ((min(a, r[0]), max(b, r[1])))
        else:
            result.append((a, b))
    return result


def merge(ranges: list[tuple[int, int]]) -> list[tuple[int, int]]:
    '''
    >>> merge([(5, 8), (2, 6)])
    [(2, 8)]

    >>> rr, _ = load(X)
    >>> merge(rr)
    [(3, 5), (10, 20)]
    '''
    return fold(sorted(ranges))


def size(ranges: list[tuple[int, int]]) -> int:
    '''
    >>> rr, _ = load(X)
    >>> size(rr)
    14
    '''
    return sum(1 + b - a for a, b in merge(ranges))


if __name__ == '__main__':
    rr, ii = load(pathlib.Path('input.txt').read_text())
    print(count_fresh(ii, rr))
    print(size(rr))
