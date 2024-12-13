from __future__ import annotations

from io import StringIO, TextIOBase
import re
from typing import Iterable

import pytest

MUL = re.compile(r'mul\((\d{1,3}),(\d{1,3})\)')
TOGGLE = re.compile(r"(do\(\)|don't\(\))")


def load(src: TextIOBase) -> Iterable[tuple[int, int]]:
    doing = True
    for line in src:
        for segm in TOGGLE.split(line):
            if doing:
                yield from scan(segm)
            if TOGGLE.match(segm):
                doing = segm == 'do()'


def scan(memory: str) -> Iterable[tuple[int, int]]:
    for pair in MUL.findall(memory):
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


@pytest.fixture
def example_2() -> str:
    return (
        "xmul(2,4)&mul[3,7]!^don't()_mul(5,5)+mul(32,64](mul(11,8)"
        "undo()?mul(8,5))"
    )


def test_example_1(example_1: str) -> None:
    expr = list(scan(example_1))
    assert expr == [(2, 4), (5, 5), (11, 8), (8, 5)]
    assert compute(expr) == 161


def test_example_2(example_2: str) -> None:
    expr = list(load(StringIO(example_2)))
    assert expr == [(2, 4), (8, 5)]


def test_load(example_1: str) -> None:
    expr = load(StringIO(example_1))
    assert compute(expr) == 161


def test_input() -> None:
    with open('input.txt') as f:
        result = compute(load(f))
    assert result == 104245808


if __name__ == '__main__':
    with open('input.txt') as f:
        result = compute(load(f))
    print(result)
