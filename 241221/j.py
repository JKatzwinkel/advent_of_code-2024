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


class Pad:
    '''
    >>> Pad('123456789 0a').pos('A')
    (2, 3)

    >>> Pad(' ^a<v>').height
    2

    >>> (0, 0) in Pad(' ^a<v>')
    False

    >>> Pad(' ^a<v>').moves('a', '<')
    ['<v<', 'v<<']

    >>> Pad('123456').moves('1', '6')
    ['
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
