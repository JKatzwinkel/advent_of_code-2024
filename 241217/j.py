from __future__ import annotations

from io import StringIO, TextIOBase
from typing import Callable, Self
from types import FunctionType

import pytest


EXAMPLE = '''
Register A: 729
Register B: 0
Register C: 0

Program: 0,1,5,4,3,0
'''


def load(src: TextIOBase) -> Machine:
    machine = Machine()
    for line in src:
        if 'Register' in line:
            register, value = line.split(
                'Register'
            )[-1].split(':')
            machine.reg[
                register.strip().lower()
            ] = int(value)
        elif 'Program' in line:
            prog = eval(
                line.split('Program: ')[-1]
            )
            machine.tape = [t for t in prog]
    return machine


class Machine:
    OPS = [
        'adv', 'bxl', 'bst', 'jnz',
        'bxc', 'out', 'bdv', 'cdv',
    ]

    def __init__(
        self, a: int = 0,
        b: int = 0, c: int = 0
    ) -> None:
        self.reg = {}
        for i, v in enumerate((a, b, c)):
            self.reg['abc'[i]] = v
        self.head = 0
        self.tape: list[int] = []
        self.output: list[int] = []
        self.log: list[str] = []

    def run(
        self, program: list[int] | None = None
    ) -> Self:
        self.head = 0
        self.tape = program or self.tape
        while self.head < len(self.tape):
            self.exe(*self.tape[self.head:self.head+2])
            self.head += 2
            print(
                f'{self.log[-2]}  |  {self.log[-1]}'
            )
        return self

    def exe(self, opcode: int, o: int) -> Self:
        self.operation(opcode)(self, o)
        self.log.append(f'{o:<5} | {self}')
        return self

    def __str__(self) -> str:
        reg = '  '.join(
            f'{k}={v:<5}' for k, v in self.reg.items()
        )
        opc = self.tape[self.head:self.head+2]
        return f'{reg} | {self.head} -> {opc}'

    def operand(self, co: int) -> int:
        if co < 4:
            return co
        return self.reg['abc'[co-4]]

    def adv(self, co: int) -> None:
        num = self.reg['a']
        den = 2 ** self.operand(co)
        self.reg['a'] = num // den

    def bxl(self, lo: int) -> None:
        self.reg['b'] = self.reg['b'] ^ lo

    def bst(self, co: int) -> None:
        self.reg['b'] = self.operand(co) % 8

    def jnz(self, lo: int) -> None:
        if self.reg['a'] == 0:
            return
        self.head = lo - 2

    def bxc(self, *args: int) -> None:
        self.reg['b'] = self.reg['b'] ^ self.reg['c']

    def out(self, co: int) -> None:
        self.output.append(self.operand(co) % 8)

    def bdv(self, co: int) -> None:
        num = self.reg['a']
        den = 2 ** self.operand(co)
        self.reg['b'] = num // den

    def cdv(self, co: int) -> None:
        num = self.reg['a']
        den = 2 ** self.operand(co)
        self.reg['c'] = num // den

    def operation(self, opcode: int) -> Callable[
        [Self, int], None
    ]:
        name = self.__class__.OPS[opcode]
        self.log.append(f'{opcode}:{name}')
        meth = self.__class__.__dict__[name]
        assert isinstance(meth, FunctionType)
        return meth

    @property
    def stdout(self) -> str:
        return ','.join(map(str, self.output))


def test_load() -> None:
    machine = load(StringIO(EXAMPLE))
    assert machine.reg == {
        'a': 729, 'b': 0, 'c': 0
    }
    assert machine.tape == [
        0, 1, 5, 4, 3, 0
    ]


def _load_registers(s: str) -> dict[str, int]:
    '''
    >>> _load_registers('a=1')
    {'a': 1}

    >>> _load_registers('')
    {}
    '''
    return {
        k: int(v)
        for k, v in [
            a.split('=') for a in s.split()
        ]
    }


@pytest.mark.parametrize(
    'before, program, after, output',
    [
        ('c=9', '2,6', 'b=1', ''),
        ('a=10', '5,0,5,1,5,4', '', '0,1,2'),
        (
            'a=2024', '0,1,5,4,3,0',
            'a=0', '4,2,5,6,7,7,7,7,3,1,0'
        ),
        ('b=29', '1,7', 'b=26', ''),
        ('b=2024 c=43690', '4,0', 'b=44354', ''),
    ]
)
def test_instructions(
    before: str, program: str, after: str, output: str
) -> None:
    rb = _load_registers(before)
    instr = eval(f'[{program}]')
    ra = _load_registers(after)
    out = eval(f'[{output}]')
    m = Machine(**rb).run(instr)
    for cmd, state in zip(m.log[::2], m.log[1::2]):
        print(f'{cmd} | {state}')
    for r, v in ra.items():
        assert m.reg[r] == v
    if out:
        assert m.output == out


def test_run_example() -> None:
    m = load(StringIO(EXAMPLE))
    assert m.run().stdout == '4,6,3,5,6,3,5,2,1,0'


def test_input() -> None:
    with open('input.txt') as f:
        m = load(f)
    assert m.run().stdout == '2,1,4,0,7,4,0,2,3'


if __name__ == '__main__':
    m = Machine(a=2024).run([0, 1, 5, 4, 3, 0])
