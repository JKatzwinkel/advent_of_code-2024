from __future__ import annotations

import contextlib
from io import StringIO, TextIOBase
import re
from typing import Self, Iterable, Iterator

import pytest


BUTTON_EX = re.compile(r'Button .: X\+(\d+), Y\+(\d+)')
PRIZE_EX = re.compile(r'Prize: X=(\d+), Y=(\d+)')


def load(src: TextIOBase) -> list[Machine]:
    results = []
    machine = Machine()
    for line in src:
        if (v := BUTTON_EX.findall(line)):
            x, y = v[0]
            machine.buttons.append(V(int(x), int(y)))
        elif (p := PRIZE_EX.findall(line)):
            x, y = p[0]
            machine.prize = V(int(x), int(y))
        else:
            results.append(machine)
            machine = Machine()
    results.append(machine)
    return [r for r in results if r.buttons]


class V(Iterable[int]):
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

    def __add__(self, v: Self) -> Self:
        x, y = v
        return self.__class__(self.x + x, self.y + y)

    def __iter__(self) -> Iterator[int]:
        self._iter = iter([self.x, self.y])
        return self

    def __next__(self) -> int:
        return next(self._iter)

    def __eq__(self, other: object) -> bool:
        assert isinstance(other, self.__class__)
        x, y = other
        return self.x == x and self.y == y

    def __mul__(self, factor: int) -> Self:
        return self.__class__(self.x * factor, self.y * factor)

    def __rmul__(self, factor: int) -> Self:
        return self.__mul__(factor)

    def __repr__(self) -> str:
        return f'↗({self.x}, {self.y})'


def det(matrix: tuple[V, V]) -> int:
    a, c = matrix[0]
    b, d = matrix[1]
    return a * d - b * c


def solve(matrix: tuple[V, V], right: V) -> V:
    determinant = det(matrix)
    if determinant == 0:
        raise ValueError(
            f'A*x=b {matrix}*x={right} not solvable: '
            'determinant is 0!'
        )
    a, c = matrix[0]
    b, d = matrix[1]
    e, f = right
    x1 = det((V(e, f), V(b, d))) / determinant
    x2 = det((V(a, c), V(e, f))) / determinant
    x = V(round(x1), round(x2))
    if x.x * matrix[0] + x.y * matrix[1] != right:
        raise ValueError(
            f'A*x=b {matrix}*x={right} not solvable '
            'with rounded values.'
        )
    return x


class Machine:
    COST = {0: 3, 1: 1}

    def __init__(self) -> None:
        self.buttons: list[V] = []
        self.prize = V(0, 0)

    def solve(self) -> tuple[int, int, int]:
        with contextlib.suppress(ValueError):
            a, b = solve(
                (self.buttons[0], self.buttons[1]),
                self.prize
            )
            cost = self.cost((a, b))
            return (a, b, cost)
        return (0, 0, 0)


    def cost(self, presses: tuple[int, int]) -> int:
        return sum(
            count * self.__class__.COST[i]
            for i, count in enumerate(presses)
        )


def cost(machines: list[Machine]) -> int:
    solutions = [
        machine.solve() for machine in machines
    ]
    return sum(
        solution[-1] for solution in solutions
        if solution[-1] > 0
    )


def test_solve(examples: str) -> None:
    machines = load(StringIO(examples))
    assert machines[0].solve() == (80, 40, 280)
    assert machines[1].solve() == (0, 0, 0)
    assert machines[2].solve() == (38, 86, 200)
    assert cost(machines) == 480


@pytest.fixture
def examples() -> str:
    return '''
        Button A: X+94, Y+34
        Button B: X+22, Y+67
        Prize: X=8400, Y=5400

        Button A: X+26, Y+66
        Button B: X+67, Y+21
        Prize: X=12748, Y=12176

        Button A: X+17, Y+86
        Button B: X+84, Y+37
        Prize: X=7870, Y=6450

        Button A: X+69, Y+23
        Button B: X+27, Y+71
        Prize: X=18641, Y=10279'''


def test_load(examples: str) -> None:
    machines = load(StringIO(examples))
    assert len(machines) == 4
    assert machines[0].buttons == [V(94, 34), V(22, 67)]
    assert machines[0].prize == V(8400, 5400)


def test_input() -> None:
    with open('input.txt') as f:
        machines = load(f)
    assert len(machines) == 320
    assert cost(machines) == 34393
