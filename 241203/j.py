from __future__ import annotations

from io import StringIO, TextIOBase
import re
from typing import Iterable

import pytest

PATTERN = re.compile(r'mul\((\d{1,3}),(\d{1,3})\)')


def load(src: TextIOBase) -> Iterable[tuple[int, int]]:
    for line in src:
        yield from scan(line)


def scan(memory: str) -> Iterable[tuple[int, int]]:
    for pair in PATTERN.findall(memory):
        yield int(pair[0]), int(pair[1])


def compute(expr: Iterable[tuple[int, int]]) -> int:
    return sum(
        pair[0] * pair[1] for pair in expr
    )


@pytest.fixture
def example_1() -> str:
    return (
        'xmul(2,4)%&mul[3,7]!@^do_not_mul(5,5)+mul(32,64]'
        'then(mul(11,8)mul(8,5))'
    )


def test_example(example_1: str) -> None:
    expr = list(scan(example_1))
    assert expr == [(2, 4), (5, 5), (11, 8), (8, 5)]
    assert compute(expr) == 161


def test_load(example_1: str) -> None:
    expr = load(StringIO(example_1))
    assert compute(expr) == 161


if __name__ == '__main__':
    with open('input.txt') as f:
        expr = load(f)
        print(compute(expr))
