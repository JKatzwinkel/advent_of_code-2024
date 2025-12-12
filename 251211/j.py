from pathlib import Path


X = '''\
aaa: you hhh
you: bbb ccc
bbb: ddd eee
ccc: ddd eee fff
ddd: ggg
eee: out
fff: out
ggg: out
hhh: ccc fff iii
iii: out
'''


def load(src: str) -> dict[str, list[str]]:
    '''
    >>> g = load(X)
    >>> len(g)
    10

    >>> g['you']
    ['bbb', 'ccc']
    '''
    edges = {}
    for line in src.split('\n'):
        if not line.strip():
            continue
        node, outputs = line.split(':')
        edges[node] = list(
            map(str.strip, outputs.split())
        )
    return edges


def find(
    edges: dict[str, list[str]],
    start: str = 'you', end: str = 'out',
) -> list[list[str]]:
    '''
    >>> pp = find(load(X))
    >>> len(pp)
    5
    >>> pp[0]
    ['you', 'bbb', 'ddd', 'ggg', 'out']
    '''
    def recurse(node: str) -> list[list[str]]:
        if node == 'out':
            return [[node]]
        result = []
        for adj in edges[node]:
            if not (rr := recurse(adj)):
                continue
            for tail in rr:
                result.append([node] + tail)
        return result
    return recurse(start)


def test_pathfinding() -> None:
    gg = load(X)
    pp = find(gg)
    assert pp == [
        ['you', 'bbb', 'ddd', 'ggg', 'out'],
        ['you', 'bbb', 'eee', 'out'],
        ['you', 'ccc', 'ddd', 'ggg', 'out'],
        ['you', 'ccc', 'eee', 'out'],
        ['you', 'ccc', 'fff', 'out'],
    ]


if __name__ == '__main__':
    edges = load(Path('input.txt').read_text())
    paths = find(edges)
    print(len(paths))
