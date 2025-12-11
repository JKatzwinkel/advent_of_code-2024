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
iii: out'''


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
        node, outputs = line.split(':')
        edges[node] = list(
            map(str.strip, outputs.split())
        )
    return edges
