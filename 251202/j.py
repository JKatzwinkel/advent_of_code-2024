import pathlib


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


def inv(n: int) -> bool:
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
    if (ll := len(s)) % 2:
        return False
    return s[:ll//2] == s[ll//2:]


def invs(r: tuple[int, int]) -> list[int]:
    '''
    >>> invs((11, 22))
    [11, 22]
    >>> invs((95, 115))
    [99]
    >>> invs((1188511880, 1188511890))
    [1188511885]
    >>> invs((1698522, 1698528))
    []
    '''
    return list(filter(inv, range(r[0], r[1]+1)))


def all_invalids(ranges: list[tuple[int, int]]) -> list[int]:
    return [i for r in ranges for i in invs(r)]


def test_invs() -> None:
    rr = read_input(X)
    assert sum(all_invalids(rr)) == 1227775554


if __name__ == '__main__':
    rr = read_input(pathlib.Path('input.txt').read_text())
    print(sum(all_invalids(rr)))
