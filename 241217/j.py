from __future__ import annotations

from io import StringIO, TextIOBase
from typing import Callable
from types import FunctionType, Self


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
    OPS = ['adv', 'bxl', 'bst', 'bst', 'jnz', 'bxc', 'out', 'bdv']

    def __init__(self) -> None:
        self.reg = {name: 0 for name in 'abc'}
        self.head = 0
        self.tape: list[int] = []
        self.output: list[int] = []

    def exe(self, opcode: int, o: int) -> Self:
        self.operation(opcode)(o)
        return self

    def operand(self, co: int) -> int:
        if co < 4:
            return co
        return self.reg['abc'[co-4]]

    def adv(self, co: int) -> None:
        num = self.reg['a']
        den = 2 ** self.operand(co)
        self.reg['a'] == num // den

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
        self.reg['b'] == num // den

    def operation(self, opcode: int) -> Callable[[int], None]:
        name = self.__class__.OPS[opcode]
        assert isinstance(
            meth := self.__dict__[name],
            FunctionType
        )
        return meth


def test_load() -> None:
    machine = load(StringIO(EXAMPLE))
    assert machine.registers == {
        'a': 729, 'b': 0, 'c': 0
    }
    assert machine.tape == [
        0, 1, 5, 4, 3, 0
    ]


def 
