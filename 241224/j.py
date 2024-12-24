'''
--- Part Two ---

After inspecting the monitoring device more
closely, you determine that the system you're
simulating is trying to add two binary
numbers.

Specifically, it is treating the bits on wires
starting with x as one binary number, treating
the bits on wires starting with y as a second
binary number, and then attempting to add
those two numbers together. The output of this
operation is produced as a binary number on
the wires starting with z. (In all three
cases, wire 00 is the least significant bit,
then 01, then 02, and so on.)

The initial values for the wires in your
puzzle input represent just one instance of a
pair of numbers that sum to the wrong value.
Ultimately, any two binary numbers provided as
input should be handled correctly. That is,
for any combination of bits on wires starting
with x and wires starting with y, the sum of
the two numbers those bits represent should be
produced as a binary number on the wires
starting with z.

For example, if you have an addition system
with four x wires, four y wires, and five z
wires, you should be able to supply any
four-bit number on the x wires, any four-bit
number on the y numbers, and eventually find
the sum of those two numbers as a five-bit
number on the z wires. One of the many ways
you could provide numbers to such a system
would be to pass 11 on the x wires (1011 in
binary) and 13 on the y wires (1101 in
binary):

x00: 1
x01: 1
x02: 0
x03: 1
y00: 1
y01: 0
y02: 1
y03: 1

If the system were working correctly, then
after all gates are finished processing, you
should find 24 (11+13) on the z wires as the
five-bit binary number 11000:

z00: 0
z01: 0
z02: 0
z03: 1
z04: 1

Unfortunately, your actual system needs to add
numbers with many more bits and therefore has
many more wires.

Based on forensic analysis of scuff marks and
scratches on the device, you can tell that
there are exactly four pairs of gates whose
output wires have been swapped. (A gate can
only be in at most one such pair; no gate's
output was swapped multiple times.)

For example, the system below is supposed to
find the bitwise AND of the six-bit number on
x00 through x05 and the six-bit number on y00
through y05 and then write the result as a
six-bit number on z00 through z05:

x00: 0
x01: 1
x02: 0
x03: 1
x04: 0
x05: 1
y00: 0
y01: 0
y02: 1
y03: 1
y04: 0
y05: 1

x00 AND y00 -> z05
x01 AND y01 -> z02
x02 AND y02 -> z01
x03 AND y03 -> z03
x04 AND y04 -> z04
x05 AND y05 -> z00

However, in this example, two pairs of gates
have had their output wires swapped, causing
the system to produce wrong answers. The first
pair of gates with swapped outputs is x00 AND
y00 -> z05 and x05 AND y05 -> z00; the second
pair of gates is x01 AND y01 -> z02 and x02
AND y02 -> z01. Correcting these two swaps
results in this system that works as intended
for any set of initial values on wires that
start with x or y:

x00 AND y00 -> z00
x01 AND y01 -> z01
x02 AND y02 -> z02
x03 AND y03 -> z03
x04 AND y04 -> z04
x05 AND y05 -> z05

In this example, two pairs of gates have
outputs that are involved in a swap. By
sorting their output wires' names and joining
them with commas, the list of wires involved
in swaps is z00,z01,z02,z05.

Of course, your actual system is much more
complex than this, and the gates that need
their outputs swapped could be anywhere, not
just attached to a wire starting with z. If
you were to determine that you need to swap
output wires aaa with eee, ooo with z99, bbb
with ccc, and aoc with z24, your answer would
be aaa,aoc,bbb,ccc,eee,ooo,z24,z99.

Your system of gates and wires has four pairs
of gates which need their output wires swapped
- eight wires in total. Determine which four
pairs of gates need their outputs swapped so
that your system correctly performs addition;
what do you get if you sort the names of the
eight wires involved in a swap and then join
those names with commas?
'''
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

    def output(self) -> str:
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

    def decimal_input(
        self, prefix: str
    ) -> int:
        return dec(
            ''.join(
                str(int(v))
                for w, v in sorted(
                    self.inputs.items(),
                    reverse=True
                )
                if w.startswith(prefix)
            )
        )

    def computes(self, op: str) -> bool:
        x, y = tuple(map(
            self.decimal_input, 'xy'
        ))
        assert type(result := eval(
            f'{x} {op} {y}'
        )) is int
        return result == dec(self.output())

    def swap(
        self, wire1: str, wire2: str
    ) -> Circuit:
        result = Circuit()
        result.inputs = {
            w: c
            for w, c in self.inputs.items()
        }
        result.wires = {
            w: g
            for w, g in self.wires.items()
        }
        (
            result.wires[wire1],
            result.wires[wire2]
        ) = (
            result.wires[wire2],
            result.wires[wire1]
        )
        return result


def gate(op: Op, a: bool, b: bool) -> bool:
    '''
    >>> gate(Op['OR'], True, False)
    True
    '''
    assert type(
        result := eval(f'{a} {op.value} {b}')
    ) is bool
    return result


def dec(binary: str) -> int:
    return int(binary, base=2)


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
    assert c.output() == '100'


def test_large_circuit() -> None:
    c = load(StringIO(t.LARGE))
    print(c.wires)
    assert c.output() == '0011111101000'
    assert int(c.output(), base=2) == 2024


def test_circuit_input() -> None:
    c = load(StringIO(t.FU))
    assert not c.computes('&')
    c = load(StringIO(t.FU_FIXED))
    assert c.computes('&')


def test_circuit_swap() -> None:
    c = load(StringIO(t.FU))
    assert not c.computes('&')
    c = c.swap('z05', 'z00').swap(
        'z02', 'z01'
    )
    assert c.computes('&')


if __name__ == '__main__':
    with open('input.txt') as f:
        c = load(f)
    print(int(c.output(), base=2))
