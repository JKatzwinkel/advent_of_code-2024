from __future__ import annotations

import functools
from io import TextIOBase, StringIO

import pytest

EXAMPLE = '''
r, wr, b, g, bwu, rb, gb, br

brwrr
bggr
gbbr
rrbgbr
ubwu
bwurrg
brgr
bbrgwb'''


def load(src: TextIOBase) -> Solver:
    towels = set()
    designs = []
    for line in src:
        if ',' in line:
            towels.update(
                set(line.strip().split(', '))
            )
        elif line.strip():
            designs.append(line.strip())
    return Solver(towels, designs)


def widest_first(
    towels: set[str], design: str
) -> list[tuple[str, int]]:
    result: list[tuple[str, int]] = []
    for towel in sorted(towels, key=len, reverse=True):
        if towel not in design:
            continue
        result.append(
            (towel, design.index(towel))
        )
    return result


class Solver:
    def __init__(
        self, towels: set[str], designs: list[str]
    ) -> None:
        self.towels = towels
        self.designs = designs

    @functools.cache
    def solvable(self, design: str) -> bool:
        towel_positions = widest_first(
            self.towels, design
        )
        for t, i in towel_positions:
            p = True
            for segm in (design[:i], design[i+len(t):]):
                if (
                    len(segm) == 1 and
                    segm not in self.towels
                ):
                    p = False
                    break
                if not segm or segm in self.towels:
                    continue
                if not (
                    p := p and self.solvable(segm)
                ):
                    break
                self.towels.add(segm)
            if p:
                self.towels.add(design)
                return True
        return False

    def count_solvable(self) -> int:
        return sum(
            1 for design in self.designs
            if self.solvable(design)
        )


def test_load() -> None:
    s = load(StringIO(EXAMPLE))
    assert s.towels == {
        'r', 'wr', 'b', 'g', 'bwu', 'rb', 'gb', 'br'
    }
    assert s.designs[0] == 'brwrr'
    assert s.designs[-1] == 'bbrgwb'


def test_example() -> None:
    s = load(StringIO(EXAMPLE))
    assert s.solvable('brwrr')
    assert s.solvable('bwurrg')
    assert not s.solvable('ubwu')
    assert len(s.designs) == 8
    assert s.count_solvable() == 6


def test_input() -> None:
    with open('input.txt') as f:
        s = load(f)
    assert not s.solvable(
        'brubwwwwubggbgubrbbwrgurgbbrubuwrggwguguw'
    )
    assert s.solvable(
        'ugrwbburbbgrgruwrgrwgwbgrgugubbwwurrgruww'
        'burgggrrgrgwggwbg'
    )


@pytest.mark.parametrize(
    'design, expected',
    [
        ('brwrr', 2), ('bggr', 1), ('gbbr', 4),
        ('rrbgbr', 6), ('bwurrg', 1), ('brgr', 2),
        ('ubwu', 0), ('bbrgwb', 0)
    ]
)
def test_possible_solutions(
    design: str, expected: int
) -> None:
    s = load(StringIO(EXAMPLE))
    assert s.solutions(design) == expected


if __name__ == '__main__':
    with open('input.txt') as f:
        s = load(f)
    print(sorted(s.towels, key=len, reverse=True))
    print(
        f'solvable: {s.count_solvable()}'
        f'/{len(s.designs)}'
    )
