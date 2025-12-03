from functools import cache, reduce
import itertools
from typing import Iterable

import pytest


type P = tuple[int, int]


def diff(a: P, b: P) -> P:
    return b[0] - a[0], b[1] - a[1]


def steps(a: P, b: P) -> list[P]:
    '''
    >>> steps((3, 3), (5, 1))
    [(1, 0), (1, 0), (0, -1), (0, -1)]
    '''
    dx, dy = diff(a, b)
    result = []
    if dx != 0:
        result += [(dx // abs(dx), 0)] * abs(dx)
    if dy != 0:
        result += [(0, dy // abs(dy))] * abs(dy)
    return result


def step(pos: P, direction: P) -> P:
    x, y = map(sum, zip(pos, direction))
    return x, y


NUMPAD = '789456123 0a'
DIRPAD = ' ^a<v>'


class Pad:
    '''
    >>> Pad(NUMPAD).pos('A')
    (2, 3)

    >>> Pad(' ^a<v>').height
    2

    Empty grid positions are not considered part of the
    pad:

    >>> (0, 0) in Pad(' ^a<v>')
    False

    >>> Pad(' ^a<v>').moves('a', '<')
    ['<v<', 'v<<']

    >>> Pad('123456').moves('1', '6')
    ['v>>', '>v>', '>>v']

    Pad instances are re-used based on their button
    sets.

    >>> Pad(NUMPAD) is Pad(NUMPAD)
    True

    Robots can't move over a position where there is
    not button or it will panic.
    Panic moves are being avoided:

    >>> Pad(NUMPAD)
    7|8|9
    4|5|6
    1|2|3
     |0|a

    note that there is not button next to the `0` button,
    so there is only two possible ways of getting from
    the 'a' to the '1' button as opposed to getting from
    `7` to `6`:

    >>> Pad(NUMPAD).moves('6', '7')
    ['<^<', '<<^', '^<<']

    >>> Pad(NUMPAD).moves('a', '1')
    ['<^<', '^<<']

    '''
    _pads: dict[str, 'Pad'] = {}

    def __init__(self, buttons: str) -> None:
        self.buttons = buttons
        self.width = 3
        self.height = len(buttons) // self.width

    def __new__(cls, buttons: str) -> 'Pad':
        if buttons not in cls._pads:
            cls._pads[buttons] = super().__new__(cls)
        return cls._pads[buttons]

    @cache
    def moves(self, a: str, b: str) -> list[str]:
        results = []
        for directions in set(
            itertools.permutations(
                steps(self.pos(a), self.pos(b))
            )
        ):
            path = reduce(
                lambda p, d: p + [step(p[-1], d)],
                directions, [self.pos(a)]
            )
            if any(pos not in self for pos in path):
                continue
            results.append(
                ''.join(
                    ARROWS[DIRS.index(d)]
                    for d in directions
                )
            )
        return results

    def pos(self, button: str) -> P:
        y, x = divmod(
            self.buttons.index(button.lower()),
            self.width
        )
        return x, y

    def btn(self, pos: P) -> str:
        x, y = pos
        return self.buttons[x + y * self.width]

    def __contains__(self, pos: P) -> bool:
        return self.btn(pos) != ' '

    def __repr__(self) -> str:
        return '\n'.join(
            '|'.join(self.buttons[
                i*self.width:(i+1)*self.width
            ])
            for i in range(self.height)
        )


DIRS = [(0, -1), (1, 0), (0, 1), (-1, 0)]
ARROWS = '^>v<'


def find_inputs(pad: Pad, code: str) -> list[str]:
    moves: list[str] = [
        f'{m}A' for m in pad.moves(
            'A', code[0]
        )
    ]
    for button1, button2 in zip(
        code[:-1], code[1::]
    ):
        moves = [
            prev + cur + 'A'
            for prev, cur in itertools.product(
                moves, pad.moves(
                    button1, button2
                )
            )
        ]
    return moves


def find_chain_inputs(
    pads: list[Pad], code: str
) -> list[str]:
    inputs: list[str] = [code]
    for pad in pads[::-1]:
        candidates = [
            moves for current in inputs
            for moves in find_inputs(pad, current)
        ]
        shortest = min(map(len, candidates))
        inputs = [
            moves for moves in candidates
            if len(moves) == shortest
        ]
    return inputs


def complexity(pads: list[Pad], code: str) -> int:
    inputs = find_chain_inputs(pads, code)
    return int(code[:-1]) * len(inputs[0])


def sum_complexity(
    pads: list[Pad], codes: list[str]
) -> int:
    return sum(
        complexity(pads, code) for code in codes
    )


def test_inputs() -> None:
    pad = Pad(NUMPAD)
    inputs = find_inputs(pad, '029A')
    assert set(inputs) == {
        '<A^A>^^AvvvA',
        '<A^A^>^AvvvA',
        '<A^A^^>AvvvA',
    }


@pytest.mark.parametrize(
    'buttons, moves',
    [
        (
            (DIRPAD, NUMPAD),
            'v<<A>>^A<A>AvA<^AA>A<vAAA>^A'
        ),
        (
            (DIRPAD, DIRPAD, NUMPAD),
            '<vA<AA>>^AvAA<^A>A<v<A>>^AvA^A<vA>^A'
            '<v<A>^A>AAvA^A<v<A>A>^AAAvA<^A>A'
        )
    ]
)
def test_chain_inputs(
    buttons: Iterable[str], moves: str
) -> None:
    pads = [Pad(pad) for pad in buttons]
    inputs = find_chain_inputs(pads, '029A')
    assert moves in inputs


@pytest.mark.parametrize(
    'code, moves',
    [
        (
            '029A', '<vA<AA>>^AvAA<^A>A<v<A>>^AvA^A<v'
            'A>^A<v<A>^A>AAvA^A<v<A>A>^AAAvA<^A>A'
        ),
        (
            '980A', '<v<A>>^AAAvA^A<vA<AA>>^AvAA<^A>'
            'A<v<A>A>^AAAvA<^A>A<vA>^A<A>A'
        ),
        (
            '179A', '<v<A>>^A<vA<A>>^AAvAA<^A>A<v<A>>'
            '^AAvA^A<vA>^AA<A>A<v<A>A>^AAAvA<^A>A'
        ),
        (
            '456A', '<v<A>>^AA<vA<A>>^AAvAA<^A>A<vA>^'
            'A<A>A<vA>^A<A>A<v<A>A>^AAvA<^A>A'
        ),
        (
            '379A', '<v<A>>^AvA^A<vA<AA>>^AAvA<^A>AAv'
            'A^A<vA>^AA<A>A<v<A>A>^AAAvA<^A>A'
        )
    ]
)
def test_shortest_input(code: str, moves: str) -> None:
    pads = PUZZLE_PADS
    assert moves in find_chain_inputs(pads, code)


def test_complexity() -> None:
    codes = [
        '029A',
        '980A',
        '179A',
        '456A',
        '379A',
    ]
    assert sum_complexity(PUZZLE_PADS, codes) == 126384


PUZZLE_PADS = [Pad(DIRPAD), Pad(DIRPAD), Pad(NUMPAD)]


if __name__ == '__main__':
    codes = [
        '935A',
        '319A',
        '480A',
        '789A',
        '176A',
    ]
    pads = [Pad(DIRPAD)] * 25 + [Pad(NUMPAD)]
    print(sum_complexity(pads, codes))
