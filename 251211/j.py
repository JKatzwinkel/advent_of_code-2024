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
        return [
            [node] + tail
            for adj in edges[node]
            for tail in recurse(adj)
        ]
    return [
        tail for tail in recurse(start)
        if all(checkpoint in tail for checkpoint in checkpoints)
    ]


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


if __name__ == '__main__':
    edges = load(Path('input.txt').read_text())
    print(todot(edges))
    # paths = find(edges, 'dac', 'fft', start='svr')
    # print(len(paths))
