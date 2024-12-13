from collections import Counter
from io import StringIO, TextIOBase

import pytest


def load(src: TextIOBase) -> list[tuple[int, int]]:
    results = []
    for line in src:
        if not (numbers := line.split()):
            continue
        n, m = tuple(map(int, numbers))
        results.append((n, m))
    return results


def rotate(lists: list[tuple[int, int]]) -> tuple[list[int], list[int]]:
    l1, l2 = [
        sorted(pair[i] for pair in lists) for i in [0, 1]
    ]
    return l1, l2


def distances(l1: list[int], l2: list[int]) -> list[int]:
    return [abs(pair[0] - pair[1]) for pair in zip(l1, l2)]


def similarity(l1: list[int], l2: list[int]) -> int:
    value_counts: Counter[int] = Counter()
    for n in l2:
        value_counts[n] += 1
    result = 0
    for n in l1:
        result += n * value_counts[n]
    return result


@pytest.fixture
def example() -> StringIO:
    return StringIO(
        '''3   4
           4   3
           2   5
           1   3
           3   9
           3   3'''
    )


def test_load(example: TextIOBase) -> None:
    locations = load(example)
    assert len(locations) == 6


def test_distances(example: TextIOBase) -> None:
    dist = distances(*rotate(load(example)))
    assert sum(dist) == 11


def test_similarity(example: TextIOBase) -> None:
    l1, l2 = rotate(load(example))
    assert similarity(l1, l2) == 31


def test_input() -> None:
    with open('input.txt') as f:
        locations = rotate(load(f))
    assert sum(distances(*locations)) == 1938424
    assert similarity(*locations) == 22014209
