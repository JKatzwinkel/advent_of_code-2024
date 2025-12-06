from collections import defaultdict
import pathlib
import re


X = '''\
123 328  51 64 \\n
 45 64  387 23 \\n
  6 98  215 314\\n
*   +   *   +  \\n
'''


type Problem = tuple[str, *tuple[int, ...]]


def load(src: str, cephmode: bool = False) -> list[Problem]:
    '''
    >>> len(load(X))
    4

    >>> len(load(X, cephmode=True))
    4

    >>> load(X)[0]
    ('*', 123, 45, 6)

    >>> load(X, cephmode=True)[:2]
    [('*', 356, 24, 1), ('+', 8, 248, 369)]

    >>> load(X, cephmode=True)[-2:]
    [('*', 175, 581, 32), ('+', 4, 431, 623)]
    '''
    rows = [row for row in src.split('\n') if row]
    result = []
    for match in re.finditer(r'[+*]\s*', rows[-1]):
        i, j = match.span()
        cells = [row[i:j] for row in rows[:-1]]
        if cephmode:
            operands = cephalofy(*cells)
        else:
            operands = [int(s) for s in cells]
        op = match.group()
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
    for s in numbers:
        for i, c in enumerate(s):
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
