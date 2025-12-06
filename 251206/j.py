X = '''\
123 328  51 64
 45 64  387 23
  6 98  215 314
*   +   *   +  '''


def load(src: str) -> list[tuple[str, *tuple[int, ...]]]:
    '''
    >>> load(X)[0]
    ('*', 123, 45, 6)
    '''
    rows = [row.split() for row in src.split('\n')]
    result = []
    for i, op in enumerate(rows[-1]):
        prob: tuple[str, *tuple[int, ...]] = (
            op, *[int(row[i]) for row in rows[:-1]]
        )
        result.append(prob)
    return result
