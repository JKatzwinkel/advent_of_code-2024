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
