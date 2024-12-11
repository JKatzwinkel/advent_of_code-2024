from __future__ import annotations

from math import floor, log10
from typing import Self

import pytest


def read(line: str) -> list[int]:
    '''
    >>> read('0 1 10 99 999 ')
    [0, 1, 10, 99, 999]
    '''
    return list(map(int, line.strip().split()))


def sstr(stones: list[int]) -> str:
    return ' '.join(map(str, stones))


def digits(number: int) -> int:
    '''
    >>> digits(0)
    1

    >>> digits(10)
    2
    '''
    if number < 1:
        return 1
    return floor(log10(number)) + 1


def change(stone: int) -> list[int]:
    if stone == 0:
        return [1]
    if not (dig := digits(stone)) % 2:
        ss = str(stone)
        return [int(ss[:dig//2]), int(ss[dig//2:])]
    return [stone * 2024]


def test_change_rules() -> None:
    assert change(99) == [9, 9]
    assert change(2024) == [20, 24]
    assert change(1) == [2024]
    # assert change(0, 2) == [2024]
    # assert change(0, 3) == [20, 24]


class Node:
    def __init__(self, stone: int) -> None:
        self.value = stone
        self.children: list[Node] = []
        self.populated = False

    def add(self, child: Node) -> Self:
        self.children.append(child)
        return self

    def traverse(self, length: int) -> list[Node]:
        if length == 0:
            return [self]
        return [
            node
            for child in self.children
            for node in child.traverse(length - 1)
        ]


class Graph:
    def __init__(self) -> None:
        self.nodes: dict[int, Node] = {}

    def __getitem__(self, stone: int) -> Node:
        result = self.nodes.get(stone, Node(stone))
        if stone not in self.nodes:
            self.nodes[stone] = result
        return result

    def __len__(self) -> int:
        return len(self.nodes)

    def link(self, stone: int, changes_into: int) -> Self:
        self[stone].add(self[changes_into])
        return self

    def traverse(self, start: int, length: int) -> list[int]:
        return [
            node.value for node in self[start].traverse(length)
        ]

    def keys(self) -> set[int]:
        return set(self.nodes.keys())

    def __contains__(self, stone: int) -> bool:
        return stone in self.nodes

    @classmethod
    def spawn(cls) -> Graph:
        g = Graph()
        frontier: set[int] = {0}
        while frontier:
            new_frontier = set()
            for stone in frontier:
                for successor in change(stone):
                    g.link(stone, successor)
                    if g[successor].populated:
                        continue
                    new_frontier.add(successor)
                g[stone].populated = True
            frontier = new_frontier
        return g


@pytest.fixture
def smol_graph() -> Graph:
    g = Graph().link(0, 1).link(1, 2024).link(2024, 20).link(2024, 24)
    return g.link(20, 2).link(20, 0).link(24, 2).link(24, 4)


def test_graph(smol_graph: Graph) -> None:
    assert len(smol_graph) == 7
    assert smol_graph[20].value == 20


def test_traverse_graph(smol_graph: Graph) -> None:
    assert smol_graph.traverse(1, 2) == [20, 24]
    assert smol_graph.traverse(1, 3) == [2, 0, 2, 4]


def test_spawn_graph() -> None:
    g = Graph.spawn()
    assert g[20].children == [g[2], g[0]]
    assert g.traverse(0, 6) == [
        40, 48, 2024, 40, 48, 80, 96
    ]


def blink(stones: list[int], times: int = 1) -> list[int]:
    result = [
        new_stone
        for stone in stones
        for new_stone in change(stone)
    ]
    if times == 1:
        return result
    return blink(result, times - 1)


@pytest.mark.parametrize(
    'stones,results',
    [
        (
            '0 1 10 99 999',
            ['1 2024 1 0 9 9 2021976']
        ),
        (
            '125 17',
            [
                '253000 1 7',
                '253 0 2024 14168',
                '512072 1 20 24 28676032',
                '512 72 2024 2 0 2 4 2867 6032',
                '1036288 7 2 20 24 4048 1 4048 8096 28 67 60 32',
                '2097446912 14168 4048 2 0 2 4 40 48 2024 40 48 '
                '80 96 2 8 6 7 6 0 3 2'
            ]
        ),
    ]
)
def test_blink(stones: str, results: list[str]) -> None:
    for result in results:
        iteration = sstr(blink(read(stones)))
        assert iteration == result, (
            f'{stones} should have blinked into {result} but became '
            f'{iteration}'
        )
        stones = iteration


def test_blink_n_times() -> None:
    assert len(blink(read('125 17'), 6)) == 22
    assert len(blink(read('125 17'), 25)) == 55312


def test_input() -> None:
    stones = read('4022724 951333 0 21633 5857 97 702 6')
    assert len(blink(stones, 25)) == 211306


if __name__ == '__main__':
    stones = read('4022724 951333 0 21633 5857 97 702 6')
    print(len(blink(stones, 25)))
    # print(len(blink(stones, 75)))
