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


def dial(sequence: list[str]) -> int:
    p, zc = 50, 0
    for c in sequence:
        d = int(c[1:]) * (-1 if c.startswith('L') else 1)
        p = (p + d) % 100
        if p == 0:
            zc += 1
    return zc
