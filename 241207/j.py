from __future__ import annotations

from io import StringIO, TextIOBase
import itertools
from math import log10, floor
from typing import Self

import pytest


def load_equations(src: TextIOBase) -> list[Equation]:
    result = []
    for line in src:
        if not line.split('\n')[0].strip():
            continue
        result.append(Equation.of(line))
    return result


@pytest.fixture
def example_input() -> str:
    return '''
    190: 10 19
    3267: 81 40 27
    83: 17 5
    156: 15 6
    7290: 6 8 6 15
    161011: 16 10 13
    192: 17 8 14
    21037: 9 7 18 13
    292: 11 6 16 20
    '''


def test_load_equations(example_input: str) -> None:
    src = StringIO(example_input)
    equations = load_equations(src)
    assert len(equations) == 9
    assert equations[0].result == 190
    assert equations[0].operands == [10, 19]


class Equation:
    OPERATORS = ['+', '*', '||']

    def __init__(self, result: int, operands: list[int]):
        self.result = result
        self.operands = operands

    @classmethod
    def of(cls, line: str) -> Self:
        segm = line.split('\n')[0].split(':')
        return cls(
            int(segm[0]), list(map(int, segm[1].split()))
        )

    def operations(
        self, operators: list[str] = OPERATORS
    ) -> list[tuple[str, ...]]:
        return list(itertools.product(
            *([operators] * (len(self.operands) - 1))
        ))

    def solve(self, operations: tuple[str, ...]) -> int:
        result = self.operands[0]
        for operator, operand in zip(operations, self.operands[1:]):
            match operator:
                case '+':
                    result += operand
                case '*':
                    result *= operand
                case '||':
                    result = (
                        10 ** (floor(log10(operand)) + 1)
                        * result + operand
                    )
        return result

    def is_solvable(self, operators: list[str] = OPERATORS) -> bool:
        return any(
            self.solve(operations) == self.result
            for operations in self.operations(operators)
        )


def sum_solvable(
    equations: list[Equation], operators: list[str] = Equation.OPERATORS
) -> int:
    return sum(
        eq.result for eq in equations if eq.is_solvable(operators)
    )


def test_get_possible_operations() -> None:
    eq = Equation.of('190: 5 5 19')
    assert len(eq.operations(['+', '*'])) == 4
    assert eq.solve(('+', '*',)) == 190


def test_concatenation_operator() -> None:
    assert Equation.of('156: 15 6').solve(('||',)) == 156
    assert Equation.of('7290: 6 8 6 15').is_solvable()


def test_is_solvable() -> None:
    assert Equation.of('292: 11 6 16 20').is_solvable()
    assert not Equation.of('21037: 9 7 18 13').is_solvable()


def test_sum_of_solvable(example_input: str) -> None:
    equations = load_equations(StringIO(example_input))
    assert sum_solvable(equations, ['+', '*']) == 3749
    assert sum_solvable(equations, ['+', '*', '||']) == 11387


if __name__ == '__main__':
    with open('input.txt') as f:
        equations = load_equations(f)
    result = sum_solvable(equations, ['*', '+'])
    print(f'sum of equations solvable with only + and *: {result}')
    result = sum_solvable(equations)
    print(
        f'sum of equations solvable with concatenation operator: {result}'
    )
