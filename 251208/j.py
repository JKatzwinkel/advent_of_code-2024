import itertools


X = '''
162,817,812
57,618,57
906,360,560
592,479,940
352,342,300
466,668,158
542,29,236
431,825,988
739,650,466
52,470,668
216,146,977
819,987,18
117,168,530
805,96,715
346,949,466
970,615,88
941,993,340
862,61,35
984,92,344
425,690,689
'''


type Point = tuple[int, int, int]


def load(src: str) -> list[Point]:
    '''
    >>> load(X)[0]
    (162, 817, 812)

    >>> len(load(X))
    20
    '''
    return [
        tuple(map(int, line.split(',')))  # type: ignore
        for line in src.split()
    ]


def distance(a: Point, b: Point) -> float:
    '''
    >>> distance((162,817,812), (425,690,689))
    100427
    '''
    return sum((v1 - v2) ** 2 for v1, v2 in zip(a, b))


def closest_pairs(points: list[Point]) -> list[tuple[Point, Point]]:
    '''
    >>> cp = closest_pairs(load(X))
    >>> cp[0]
    ((162, 817, 812), (425, 690, 689))
    >>> cp[1]
    ((162, 817, 812), (431, 825, 988))
    >>> cp[2]
    ((906, 360, 560), (805, 96, 715))
    >>> cp[3]
    ((431, 825, 988), (425, 690, 689))
    '''
    return sorted(
        itertools.combinations(points, 2),
        key=lambda pair: distance(pair[0], pair[1]),
    )


def connect(
    points: list[Point], steps: int = -1,
) -> list[set[Point]]:
    '''
    >>> cc = connect(load(X), steps=2)
    >>> len(cc)
    18
    >>> len(cc[0])
    3

    >>> cc = connect(load(X), steps=3)
    >>> len(cc)
    17
    >>> len(cc[0])
    3
    >>> len(cc[1])
    2

    >>> cc = connect(load(X), steps=10)
    >>> len(cc)
    11
    >>> [len(c) for c in cc]
    >>> len(cc[0])
    5
    '''
    circuits = {p: {p} for p in points}
    cp = closest_pairs(points)
    for i, (a, b) in enumerate(cp):
        if i == steps:
            break
        circuits[a].update(circuits[b])
        circuits[b] = circuits[a]
    return sorted(
        set(frozenset(v) for v in circuits.values()),  # type: ignore
        key=len, reverse=True,
    )


if __name__ == '__main__':
    cp = closest_pairs(load(X))
    for i, (a, b) in enumerate(cp):
        print(f'{i}: {a} {b} - {distance(a, b)}')
