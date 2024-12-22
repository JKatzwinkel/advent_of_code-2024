from io import StringIO, TextIOBase


def load(src: TextIOBase) -> list[int]:
    numbers = []
    for line in src:
        if not line.strip():
            continue
        numbers.append(int(line.strip()))
    return numbers


PRUNE_MASK = (1 << 24) - 1


def evolve(secret: int) -> int:
    '''
    >>> evolve(123)
    15887950
    '''
    secret = secret ^ (secret << 6) & PRUNE_MASK
    secret = secret ^ (secret >> 5) & PRUNE_MASK
    secret = secret ^ (secret << 11) & PRUNE_MASK
    return secret


def e2k(seed: int) -> int:
    secret = seed
    for _ in range(2000):
        secret = evolve(secret)
    return secret


EXAMPLE = '''
15887950
16495136
527345
704524
1553684
12683156
11100544
12249484
7753432
5908254'''


def test_evolution() -> None:
    expected = load(StringIO(EXAMPLE))
    secret = 123
    for expect in expected:
        secret = evolve(secret)
        assert secret == expect


def test_2000_evolutions() -> None:
    assert e2k(1) == 8685429
    assert e2k(10) == 4700978
    assert e2k(100) == 15273692
    assert e2k(2024) == 8667524
    assert sum(
        map(e2k, [1, 10, 100, 2024])
    ) == 37327623


if __name__ == '__main__':
    with open('input.txt') as f:
        seeds = load(f)
    print(sum(map(e2k, seeds)))
