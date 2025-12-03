import pathlib

import pytest


@pytest.mark.parametrize(
    'pack,jolt', (
        (987654321111111, 98),
        (811111111111119, 89),
        (234234234234278, 78),
        (818181911112111, 92),
    )
)
def test_joltage_example(pack: int, jolt: int) -> None:
    assert joltage(pack) == jolt


@pytest.mark.parametrize(
    'pack,jolt', (
        (987654321111111, 987654321111),
        (811111111111119, 811111111119),
        (234234234234278, 434234234278),
        (818181911112111, 888911112111),
    )
)
def test_joltage_example2(pack: int, jolt: int) -> None:
    assert joltage(pack, 12) == jolt


def joltage(pack: int | str, figs: int = 2) -> int:
    digits = []
    i = 0
    while figs > 0:
        figs -= 1
        n, j = maxat(
            f'{pack}'[i:-figs] if figs else f'{pack}'[i:]
        )
        digits.append(n)
        i += j
    return sum(n * 10 ** i for i, n in enumerate(reversed(digits)))


def maxat(s: str) -> tuple[int, int]:
    m, j = 0, 0
    for i, c in enumerate(s):
        if (n := int(c)) > m:
            m, j = n, i + 1
        if n == 9:
            break
    return m, j


if __name__ == '__main__':
    banks = pathlib.Path('input.txt').read_text().split()
    result = sum(joltage(bank) for bank in banks)
    print(result)
