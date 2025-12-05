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
