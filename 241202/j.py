from collections import Counter
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


def is_safe(report: list[int], dampener: bool = False) -> bool:
    '''
    >>> is_safe([7, 6, 4, 2, 1])
    True

    >>> is_safe([1, 3, 2, 4, 5])
    False

    >>> is_safe([8, 6, 4, 4, 1])
    False

    >>> is_safe([8, 6, 4, 4, 1], dampener=True)
    True

    >>> is_safe([1, 2, 7, 8, 9], dampener=True)
    False

    >>> is_safe([2, 1, 3, 4, 5], dampener=True)
    True
    '''
    def _is_bad(change: int) -> bool:
        if abs(change) not in (1, 2, 3):
            return True
        return sig(change) != sign
    changes = [
        b - a for a, b in zip(report[:-1], report[1:])
    ]
    sign = Counter(map(sig, changes)).most_common()[0][0]
    bad = []
    for i, change in enumerate(changes):
        if _is_bad(change):
            bad.append(i)
            continue
        sign = sig(change)
    if not bad:
        return True
    if not dampener:
        return False
    return any(
        is_safe(report[:i] + report[i+1:]) for i in bad
    )


def count_safe(reports: list[list[int]], dampener: bool = False) -> int:
    return sum(
        1 for report in reports
        if is_safe(report, dampener=dampener)
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
    safe = [is_safe(report, dampener=True) for report in reports]
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
    assert count_safe(reports, dampener=True) > 542
