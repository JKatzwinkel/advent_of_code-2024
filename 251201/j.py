import pathlib


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


def test_example2b() -> None:
    assert dial2(['R1000']) == 10


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


def dial2(sequence: list[str]) -> int:
    p, zc = 50, 0
    for d in map(dialize, sequence):
        np = p + d
        zeros, p = divmod(np, 100)
        zc += abs(zeros)
    return zc


if __name__ == '__main__':
    result = dial(pathlib.Path('input.txt').read_text().split())
    print(result)
