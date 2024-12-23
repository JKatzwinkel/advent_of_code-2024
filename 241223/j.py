from collections import defaultdict
from io import StringIO, TextIOBase
import itertools


def load(src: TextIOBase) -> dict[str, set[str]]:
    graph = defaultdict(set)
    for line in src:
        if '-' not in line:
            continue
        a, b = line.strip().split('-')
        graph[a].add(b)
        graph[b].add(a)
    return graph


def find_cliques(
    graph: dict[str, set[str]],
    max_size: int = 0,
) -> list[set[str]]:
    cliques: set[frozenset[str]] = set()

    def bron_kerbosch(
        R: set[str], P: set[str], X: set[str]
    ) -> None:
        if not P and not X:
            if max_size:
                cliques.update(
                    frozenset(combi)
                    for combi in itertools.combinations(
                        R, max_size
                    )
                )
            else:
                cliques.add(frozenset(R))
        for v in {v for v in P}:
            bron_kerbosch(
                R | {v},
                P.intersection(graph[v]),
                X.intersection(graph[v])
            )
            P -= {v}
            X |= {v}

    bron_kerbosch(set(), set(graph.keys()), set())
    return list(cliques)


SAMPLE = '''
kh-tc
qp-kh
de-cg
ka-co
yn-aq
qp-ub
cg-tb
vc-aq
tb-ka
wh-tc
yn-cg
kh-ub
ta-co
de-co
tc-td
tb-wq
wh-td
ta-ka
td-qp
aq-cg
wq-ub
ub-vc
de-ta
wq-aq
wq-vc
wh-yn
ka-de
kh-ta
co-tc
wh-qp
tb-vc
td-yn'''


def test_load() -> None:
    graph = load(StringIO(SAMPLE))
    assert graph['kh'] == {'tc', 'qp', 'ub', 'ta'}


def test_cliques() -> None:
    graph = load(StringIO(SAMPLE))
    cliques = find_cliques(graph, 3)
    assert len(cliques) == 12
    assert len([
        clique for clique in cliques
        if any(c[0] == 't' for c in clique)
    ]) == 7


def test_input() -> None:
    with open('input.txt') as f:
        graph = load(f)
    cliques = find_cliques(graph, 3)
    with_t = [
        clique for clique in cliques
        if any(c[0] == 't' for c in clique)
    ]
    assert len(with_t) == 1368


if __name__ == '__main__':
    with open('input.txt') as f:
        graph = load(f)
    cliques = find_cliques(graph, 3)
    with_t = [
        clique for clique in cliques
        if any(c[0] == 't' for c in clique)
    ]
    print(len(with_t))
