from functools import reduce
import itertools

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
    result += [
        (0, 0) if dx == 0 else (dx // abs(dx), 0)
    ] * abs(dx)
    result += [
            (0, 0) if dy == 0 else (0, dy // abs(dy))
    ] * abs(dy)
    return result


def step(pos: P, direction: P) -> P:
    x, y = map(sum, zip(pos, direction))
    return x, y


NUMPAD = '789456123 0a'


class Pad:
    '''
    >>> Pad(NUMPAD).pos('A')
    (2, 3)

    >>> Pad(' ^a<v>').height
    2

    >>> (0, 0) in Pad(' ^a<v>')
    False

    >>> Pad(' ^a<v>').moves('a', '<')
    ['<v<', 'v<<']

    >>> Pad('123456').moves('1', '6')
    ['v>>', '>v>', '>>v']
    '''

    def __init__(self, buttons: str) -> None:
        self.buttons = buttons
        self.width = 3
        self.height = len(buttons) // self.width

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
            if all(pos in self for pos in path):
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
        x, y = pos
        if not (
            0 <= x < self.width and
            0 <= y < self.height
        ):
            return False
        return self.btn((x, y)) != ' '


DIRS = [(0, -1), (1, 0), (0, 1), (-1, 0)]
ARROWS = '^>v<'


class Robot:
    def __init__(self, pad: Pad) -> None:
        self.arm = pad.pos('A')
        self.pad = pad

    def punch_in(self, code: str) -> list[str]:
        moves: list[str] = [
            f'{m}A' for m in self.pad.moves(
                'A', code[0]
            )
        ]
        for button1, button2 in zip(
            code[:-1], code[1::]
        ):
            moves = [
                prev + cur + 'A'
                for prev, cur in itertools.product(
                    moves, self.pad.moves(
                        button1, button2
                    )
                )
            ]
        return moves


def find_inputs(pad: Pad, code: str) -> list[str]:
    bot = Robot(pad)
    return bot.punch_in(code)


def test_inputs() -> None:
    pad = Pad(NUMPAD)
    inputs = find_inputs(pad, '029A')
    assert set(inputs) == {
        '<A^A>^^AvvvA',
        '<A^A^>^AvvvA',
        '<A^A^^>AvvvA',
    }
