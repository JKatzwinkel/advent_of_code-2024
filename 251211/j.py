from collections import defaultdict
import itertools
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
    *checkpoints: str,
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
        if node == end:
            return [[node]]
        result = [
            [node] + tail
            for adj in edges.get(node, [])
            for tail in recurse(adj)
        ]
        if not result:
            if node in edges:
                edges.pop(node, [])
        return result
    result = [
        path for path in recurse(start)
        if all(checkpoint in path for checkpoint in checkpoints)
    ]
    return result


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


Y = '''
svr: aaa bbb
aaa: fft
fft: ccc
bbb: tty
tty: ccc
ccc: ddd eee
ddd: hub
hub: fff
eee: dac
dac: fff
fff: ggg hhh
ggg: out
hhh: out
'''


E = '''\
svr,aaa,fft,ccc,ddd,hub,fff,ggg,out
svr,aaa,fft,ccc,ddd,hub,fff,hhh,out
svr,aaa,fft,ccc,eee,dac,fff,ggg,out
svr,aaa,fft,ccc,eee,dac,fff,hhh,out
svr,bbb,tty,ccc,ddd,hub,fff,ggg,out
svr,bbb,tty,ccc,ddd,hub,fff,hhh,out
svr,bbb,tty,ccc,eee,dac,fff,ggg,out
svr,bbb,tty,ccc,eee,dac,fff,hhh,out'''


def test_pathfinding_custom_start() -> None:
    gg = load(Y)
    pp = find(gg, start='svr')
    assert len(pp) == 8
    assert '\n'.join(','.join(path) for path in pp) == E


def test_pathfinding_with_checkpoints() -> None:
    gg = load(Y)
    pp = find(gg, 'fft', 'dac', start='svr')
    assert len(pp) == 2
    assert ','.join(pp[0]) == 'svr,aaa,fft,ccc,eee,dac,fff,ggg,out'
    assert ','.join(pp[1]) == 'svr,aaa,fft,ccc,eee,dac,fff,hhh,out'


def todot(edges: dict[str, list[str]]) -> str:
    '''
    >>> print(todot(load('svr: aaa bbb\\naaa: fft')))
    digraph G {
      svr -> aaa;
      svr -> bbb;
      aaa -> fft;
    }
    '''
    lines = [
        f'  {key} -> {adj};'
        for key, values in edges.items()
        for adj in values
    ]
    return '\n'.join(['digraph G {'] + lines + ['}'])


def reverse(edges: dict[str, list[str]]) -> dict[str, list[str]]:
    '''
    >>> gg = load('a: b c\\nb: d e\\nc: e')
    >>> reverse(gg)
    {'b': ['a'], 'c': ['a'], 'd': ['b'], 'e': ['b', 'c']}
    '''
    result = defaultdict(list)
    for node, adjs in edges.items():
        for adj in adjs:
            result[adj].append(node)
    return dict(result)


def part2(
    edges: dict[str, list[str]],
    *checkpoints: str,
    start: str = 'svr',
    end: str = 'out',
) -> list[list[str]]:
    '''
    >>> gg=load(Y)
    >>> pp=part2(gg, 'fft', 'dac')
    >>> len(pp)
    2
    >>> ','.join(pp[0])
    'svr,aaa,fft,ccc,eee,dac,fff,ggg,out'
    '''
    tails = find(
        edges, start=checkpoints[-1], end=end
    )
    heads = [
        reversed(path) for path in find(
            reverse(edges), start=checkpoints[0], end=start
        )
    ]
    middles = [
        path[1:-1] for path in find(
            edges, start=checkpoints[0], end=checkpoints[-1]
        )
    ]
    return [
        list(itertools.chain(*path))
        for path in itertools.product(heads, middles, tails)
    ]


if __name__ == '__main__':
    edges = load(Path('input.txt').read_text())
    # paths = find(edges, 'dac', 'fft', start='fft', end='dac')
    # paths = find(reverse(edges), start='fft', end='svr')  # viable
    # paths = find(edges, start='dac', end='out')  # viable
    # paths = find(edges, start='fft', end='dac')
    paths = part2(edges, 'fft', 'dac')
    print('\n'.join(' -> '.join(path) for path in paths))
    # print(len(paths))
    # print(todot(reverse(edges)))
