X = '''\
123 328  51 64
 45 64  387 23
  6 98  215 314
*   +   *   +  '''


type PROBLEM = tuple[str, *tuple[int, ...]]


def load(src: str) -> list[PROBLEM]:
    '''
    >>> load(X)[0]
    ('*', 123, 45, 6)
    '''
    rows = [row.split() for row in src.split('\n')]
    result = []
    for i, op in enumerate(rows[-1]):
        prob: PROBLEM = (
            op, *[int(row[i]) for row in rows[:-1]]
        )
        result.append(prob)
    return result


def solve(prob: PROBLEM) -> int:
    '''
    >>> [solve(p) for p in load(X)]
    [33210, 490, 4243455, 401]
    '''
    op, *rands = prob
    assert isinstance(
        result := eval(op.join(map(str, rands))), int
    )
    return result
