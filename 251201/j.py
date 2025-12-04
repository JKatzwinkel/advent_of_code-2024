import pathlib

import pytest


X = '''
L68
L30
R48
L5
R60
L55
L1
L99
R14
L82
'''


def test_example() -> None:
    assert dial(X.split()) == 3


def test_example2() -> None:
    assert dial2(X.split()) == 6


@pytest.mark.parametrize(
    'sequence,zeros', (
        (['R1000'], 10),
        (['R1000', 'L50'], 11),
        (['L51'], 1),
        (['L50'], 1),
        (['R50'], 1),
    )
)
def test_example2b(sequence: list[str], zeros: int) -> None:
    assert dial2(sequence) == zeros


def test_example2c() -> None:
    assert dial2(pathlib.Path('input.txt').read_text().split()) == 6689


def dialize(code: str) -> int:
    return int(code[1:]) * (-1 if code.startswith('L') else 1)


def dial(sequence: list[str]) -> int:
    p, zc = 50, 0
    for c in sequence:
        d = dialize(c)
        p = (p + d) % 100
        if p == 0:
            zc += 1
    return zc


def dial2(sequence: list[str], p: int = 50) -> int:
    zc = 0
    for d in map(dialize, sequence):
        s = -1 if d < 0 else 1
        while d:
            p += s
            d -= s
            if p == 100:
                p = 0
            if p == -1:
                p = 99
            if p == 0:
                zc += 1
    return zc


if __name__ == '__main__':
    print(dial(pathlib.Path('input.txt').read_text().split()))
    print(dial2(pathlib.Path('input.txt').read_text().split()))
