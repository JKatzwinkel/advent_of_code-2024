from __future__ import annotations

from enum import Enum
from io import StringIO, TextIOBase

import t

OPS = {'XOR': '^', 'OR': '|', 'AND': '&'}


def load(src: TextIOBase) -> Circuit:
    c = Circuit()
    for line in map(str.strip, src):
        if ':' in line:
            wire, v = line.split(':')
            c.inputs[wire] = bool(int(v))
        elif '->' in line:
            i, op, j, _, w = line.split()
            c.wires[w] = (i, j, Op[op])
    return c


class Circuit:
    def __init__(self) -> None:
        self.wires: dict[
            str, tuple[str, str, Op]
        ] = {}
        self.inputs: dict[str, bool] = {}

    def roots(self) -> list[str]:
        return [
            wire
            for wire, gate in self.wires.items()
            if gate[0] in self.inputs
            and gate[1] in self.inputs
        ]

    def clock(self) -> str:
        return ''.join(
            [
                str(int(v))
                for w, v in sorted(
                    self.result().items(),
                    reverse=True
                )
            ]
        )

    def result(self) -> dict[str, bool]:
        return {
            wire: self._recurse(wire)
            for wire in self.wires
            if wire.startswith('z')
        }

    def _recurse(self, wire: str) -> bool:
        u, v, op = self.wires[wire]
        voltages = [
            self.inputs[w] if w in self.inputs
            else self._recurse(w)
            for w in (u, v)
        ]
        return gate(op, *voltages)


def gate(op: Op, a: bool, b: bool) -> bool:
    '''
    >>> gate(Op['OR'], True, False)
    True
    '''
    assert type(
        result := eval(f'{a} {op.value} {b}')
    ) is bool
    return result


class Op(Enum):
    AND = '&'
    XOR = '^'
    OR = '|'


def test_load_small() -> None:
    c = load(StringIO(t.SMALL))
    assert c.inputs['y02'] == 0
    assert c.wires['z01'] == (
        'x01', 'y01', Op.XOR
    )


def test_circuit_roots() -> None:
    c = load(StringIO(t.SMALL))
    roots = c.roots()
    assert roots == [
        'z00', 'z01', 'z02'
    ]


def test_small_circuit() -> None:
    c = load(StringIO(t.SMALL))
    output = c.result()
    assert output == {
        'z02': True,
        'z01': False,
        'z00': False,
    }
    assert c.clock() == '100'


def test_large_circuit() -> None:
    c = load(StringIO(t.LARGE))
    print(c.wires)
    assert c.clock() == '0011111101000'
    assert int(c.clock(), base=2) == 2024


if __name__ == '__main__':
    with open('input.txt') as f:
        c = load(f)
    print(int(c.clock(), base=2))
