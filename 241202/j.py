from io import StringIO, TextIOBase

import pytest


def load(src: TextIOBase) -> list[list[int]]:
    result = []
    for line in src:
        if not (numbers := line.split()):
            continue
        result.append(
            list(map(int, numbers))
        )
    return result


def is_safe(report: list[int]) -> bool:
    changes = [
        b - a for a, b in zip(report[:-1], report[1:])
    ]
    if not all(
        abs(change) in (1, 2, 3) for change in changes
    ):
        return False
    return len(
        set(
            change // abs(change) for change in changes
        )
    ) == 1


@pytest.fixture
def example() -> StringIO:
    return StringIO(
        '''7 6 4 2 1
           1 2 7 8 9
           9 7 6 2 1
           1 3 2 4 5
           8 6 4 4 1
           1 3 6 7 9'''
    )


def test_safe(example: TextIOBase) -> None:
    reports = load(example)
    safe = list(map(is_safe, reports))
    assert safe == [
        True, False, False, False, False, True
    ]
    assert len(list(filter(is_safe, reports))) == 2


def test_load(example: TextIOBase) -> None:
    reports = load(example)
    assert len(reports) == 6
    assert len(reports[0]) == 5


def test_input() -> None:
    with open('input.txt') as f:
        reports = load(f)
    assert len(list(filter(is_safe, reports))) == 510
