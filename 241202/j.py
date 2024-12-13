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


def sig(val: int) -> int:
    if val == 0:
        return 0
    return val // abs(val)


def is_safe(report: list[int]) -> bool:
    '''
    >>> is_safe([7, 6, 4, 2, 1])
    True

    >>> is_safe([1, 3, 2, 4, 5])
    False

    >>> is_safe([8, 6, 4, 4, 1])
    False

    '''
    changes = [
        b - a for a, b in zip(report[:-1], report[1:])
    ]
    if any(
        abs(change) not in (1, 2, 3) for change in changes
    ):
        return False
    return len(set(map(sig, changes))) == 1


def with_dampener(report: list[int]) -> bool:
    '''
    >>> with_dampener([8, 6, 4, 4, 1])
    True

    >>> with_dampener([1, 2, 7, 8, 9])
    False

    >>> with_dampener([2, 1, 3, 4, 5])
    True
    '''
    return any(
        is_safe(report[:i] + report[i+1:])
        for i in range(len(report))
    )


def count_safe(reports: list[list[int]], dampener: bool = False) -> int:
    checker = with_dampener if dampener else is_safe
    return sum(
        1 for report in reports
        if checker(report)
    )


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
    assert count_safe(reports) == 2


def test_safe_with_dampener(example: TextIOBase) -> None:
    reports = load(example)
    safe = [with_dampener(report) for report in reports]
    assert safe == [
        True, False, False, True, True, True
    ]


def test_load(example: TextIOBase) -> None:
    reports = load(example)
    assert len(reports) == 6
    assert len(reports[0]) == 5


def test_input() -> None:
    with open('input.txt') as f:
        reports = load(f)
    assert count_safe(reports) == 510
    assert count_safe(reports, dampener=True) == 553
