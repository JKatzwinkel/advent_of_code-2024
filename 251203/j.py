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


def joltage(pack: int | str) -> int:
    a, i = maxat(f'{pack}'[:-1])
    b, _ = maxat(f'{pack}'[i+1:])
    return a * 10 + b


def maxat(s: str) -> tuple[int, int]:
    m, j = 0, -1
    for i, c in enumerate(s):
        if (n := int(c)) > m:
            m, j = n, i
    return m, j
