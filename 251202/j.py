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
