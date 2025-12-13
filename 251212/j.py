from __future__ import annotations
import re
from typing import Iterable


X = '''
0:
###
##.
##.

1:
###
##.
.##

2:
.##
###
##.

3:
##.
###
##.

4:
###
#..
###

5:
###
.#.
###

4x4: 0 0 0 0 2 0
12x5: 1 0 1 0 2 2
12x5: 1 0 1 0 3 2
'''


def load(src: str) -> dict[int, Shape]:
    '''
    >>> ss = load(X)
    >>> len(ss)
    6

    >>> ss[5]
    ###
    .#.
    ###
    '''
    shapes: dict[int, Shape] = {}
    shid = 0
    buffer: list[str] = []
    for line in src.split('\n'):
        if not line:
            if buffer:
                shapes[shid] = Shape(buffer)
                buffer = []
            continue
        if (numerals := re.findall(r'^(\d):', line)):
            shid = int(numerals[0])
        elif re.match(r'^[#.]+', line):
            buffer.append(line)
    return shapes


class Shape:
    def __init__(self, grid: Iterable[str]):
        self.data = ''.join(grid)

    def hflip(self) -> Shape:
        '''
        >>> Shape(['###', '#..', '##.']).hflip()
        ##.
        #..
        ###
        '''
        return Shape(
            self.data[i-3:i] for i in range(9, 0, -3)
        )

    def vflip(self) -> Shape:
        '''
        >>> Shape(['###', '#..', '##.']).vflip()
        ###
        ..#
        .##
        '''
        return Shape(
            self.data[i:i+3][::-1] for i in range(0, 9, 3)
        )

    def turn(self, turns: int = 1) -> Shape:
        '''
        >>> Shape(['###', '#..', '##.']).turn()
        ###
        #.#
        ..#

        >>> Shape(['###', '#..', '##.']).turn(3)
        #..
        #.#
        ###
        '''
        if turns == 0:
            return self
        return Shape(
            ''.join(
                self.data[o+i] for o in range(6, -3, -3)
            )
            for i in range(3)
        ).turn(turns - 1)

    def __repr__(self) -> str:
        '''
        >>> Shape(['###', '#..', '###'])
        ###
        #..
        ###
        '''
        return '\n'.join(
            self.data[i:i+3] for i in range(0, 9, 3)
        )
