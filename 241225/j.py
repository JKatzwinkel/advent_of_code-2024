from io import StringIO, TextIOBase
import itertools

type Bitting = tuple[int, int, int, int, int]


def _load(data: list[str]) -> tuple[
    Bitting, bool
]:
    is_key = all(c == '.' for c in data[0])
    if is_key:
        data = data[::-1]
    bitting = [5] * 5
    for h, line in enumerate(data[1:]):
        for b, c in enumerate(line):
            if c == '.':
                bitting[b] = min(
                    bitting[b], h
                )
    return tuple(bitting), is_key  # type: ignore


def load(src: TextIOBase) -> tuple[
    list[Bitting], list[Bitting]
]:
    schematics: dict[str, list[Bitting]] = {
        'keys': [], 'locks': []
    }
    data = []
    for line in itertools.chain(
        map(str.strip, src), ['']
    ):
        if line:
            data.append(line)
        elif data:
            bitting, is_key = _load(data)
            schematics[
                'keys' if is_key else 'locks'
            ].append(bitting)
            data = []
    return (
        schematics['locks'],
        schematics['keys'],
    )


def fit(lock: Bitting, key: Bitting) -> bool:
    return all(
        lock[i] + key[i] < 6
        for i in range(5)
    )


def fits(
    locks: list[Bitting], keys: list[Bitting]
) -> list[tuple[Bitting, Bitting]]:
    return [
        (lock, key)
        for lock, key in itertools.product(
            locks, keys
        )
        if fit(lock, key)
    ]


EXAMPLE = '''
#####
.####
.####
.####
.#.#.
.#...
.....

#####
##.##
.#.##
...##
...#.
...#.
.....

.....
#....
#....
#...#
#.#.#
#.###
#####

.....
.....
#.#..
###..
###.#
###.#
#####

.....
.....
.....
#....
#.#..
#.#.#
#####'''


def test_load() -> None:
    lock, _ = _load([
        '#####',
        '.####',
        '.####',
        '.####',
        '.#.#.',
        '.#...',
        '.....',
    ])
    assert lock == (0, 5, 3, 4, 3)
    key, is_key = _load([
        '.....',
        '#....',
        '#....',
        '#...#',
        '#.#.#',
        '#.###',
        '#####',
    ])
    assert is_key
    assert key == (5, 0, 2, 1, 3)


def test_load_example() -> None:
    locks, keys = load(StringIO(EXAMPLE))
    assert locks == [
        (0, 5, 3, 4, 3),
        (1, 2, 0, 5, 3),
    ]
    assert keys == [
        (5, 0, 2, 1, 3),
        (4, 3, 4, 0, 2),
        (3, 0, 2, 0, 1),
    ]


def test_fitting_pairs() -> None:
    locks, keys = load(StringIO(EXAMPLE))
    assert len(fits(locks, keys)) == 3


if __name__ == '__main__':
    with open('input.txt') as f:
        locks, keys = load(f)
    print(len(fits(locks, keys)))
