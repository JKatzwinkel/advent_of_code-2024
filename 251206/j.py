from collections import defaultdict
import pathlib
import re


X = '''\
123 328  51 64
 45 64  387 23
  6 98  215 314
*   +   *   +
'''


type Problem = tuple[str, *tuple[int, ...]]


def load(src: str, cephmode: bool = False) -> list[Problem]:
    '''
    >>> load(X)[0]
    ('*', 123, 45, 6)

    >>> load(X, cephmode=True)[:2]
    [('*', 356, 24, 1), ('+', 8, 248, 369)]
    '''
    rows = [re.split(r'(?<=[0-9+*]) ', row) for row in src.split('\n') if row]
    result = []
    for i, op in enumerate(rows[-1]):
        cells = [row[i] for row in rows[:-1]]
        if cephmode:
            operands = cephalofy(*cells)
        else:
            operands = [int(s) for s in cells]
        prob: Problem = (op.strip(), *operands)
        result.append(prob)
    return result


def cephalofy(*numbers: str) -> list[int]:
    '''
    >>> cephalofy('64', '23', '314')
    [4, 431, 623]

    >>> cephalofy(' 51', '387', '215')
    [175, 581, 32]
    '''
    signdig: dict[int, list[str]] = defaultdict(list)
    for n in numbers:
        for i, c in enumerate(f'{n}'):
            signdig[i].append(c)
    vertical = [
        ''.join(v) for v in reversed(signdig.values())
    ]
    return [int(s) for s in vertical if s.strip()]


def solve(prob: Problem) -> int:
    '''
    >>> [solve(p) for p in load(X)]
    [33210, 490, 4243455, 401]

    >>> [solve(p) for p in load(X, cephmode=True)]
    [8544, 625, 3253600, 1058]
    '''
    op, *rands = prob
    assert isinstance(
        result := eval(op.join(map(str, rands))), int
    )
    return result


def solve_all(probs: list[Problem]) -> int:
    '''
    >>> solve_all(load(X))
    4277556

    >>> solve_all(load(X, cephmode=True))
    3263827
    '''
    return sum(map(solve, probs))


if __name__ == '__main__':
    probs = load(pathlib.Path('input.txt').read_text())
    print(solve_all(probs))
