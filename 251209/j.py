from functools import reduce

X = '''
7,1
11,1
11,7
9,7
9,5
2,5
2,3
7,3'''


type Point = tuple[int, int]


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
