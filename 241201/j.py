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


def distances(lists: list[tuple[int, int]]) -> list[int]:
    l1, l2 = [
        sorted(pair[i] for pair in lists) for i in [0, 1]
    ]
    return [abs(pair[0] - pair[1]) for pair in zip(l1, l2)]


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
    dist = distances(load(example))
    assert sum(dist) == 11


def test_input() -> None:
    with open('input.txt') as f:
        locations = load(f)
    assert sum(distances(locations)) == 1938424
