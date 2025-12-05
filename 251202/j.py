from functools import partial
import pathlib

import pytest


X = '''\
11-22,95-115,998-1012,1188511880-1188511890,222220-222224,
1698522-1698528,446443-446449,38593856-38593862,565653-565659,
824824821-824824827,2121212118-2121212124'''


def read_range(src: str) -> tuple[int, int]:
    '''
    >>> read_range('11-22')
    (11, 22)
    '''
    return tuple(map(int, src.split('-')))  # type: ignore


def read_input(src: str) -> list[tuple[int, int]]:
    '''
    >>> read_input(X)[:2]
    [(11, 22), (95, 115)]
    '''
    return list(map(read_range, src.split(',')))


def inv(n: int, strict: bool = False) -> bool:
    '''
    >>> inv(11)
    True
    >>> inv(101)
    False
    >>> inv(1010)
    True
    >>> inv(222222)
    True
    >>> inv(446446)
    True
    >>> inv(446443)
    False
    '''
    s = f'{n}'
    ll = len(s)
    lim = ll if strict else 2
    for x in range(2, lim+1):
        if ll % x:
            continue
        partitions = set()
        for i in range(0, ll, ll//x):
            partitions.add(s[i:i+ll//x])
        if len(partitions) == 1:
            return True
    return False


def invs(
    r: tuple[int, int], strict: bool = False
) -> list[int]:
    '''
    >>> invs((11, 22))
    [11, 22]
    >>> invs((95, 115))
    [99]
    >>> invs((95, 115), strict=True)
    [99, 111]
    >>> invs((1188511880, 1188511890))
    [1188511885]
    >>> invs((1698522, 1698528))
    []
    >>> invs((2121212118, 2121212124), strict=True)
    [2121212121]
    >>> invs((824824821, 824824827), strict=True)
    [824824824]
    '''
    f = partial(inv, strict=strict)
    return list(filter(f, range(r[0], r[1]+1)))


def all_invalids(
    ranges: list[tuple[int, int]],
    strict: bool = False,
) -> list[int]:
    return [
        i for r in ranges
        for i in invs(r, strict=strict)
    ]


@pytest.mark.parametrize(
    'strict,expect', (
        (False,  1227775554),
        (True, 4174379265),
    )
)
def test_invs(strict: bool, expect: int) -> None:
    rr = read_input(X)
    assert sum(
        all_invalids(rr, strict=strict)
    ) == expect


if __name__ == '__main__':
    rr = read_input(pathlib.Path('input.txt').read_text())
    print(sum(all_invalids(rr, strict=True)))
