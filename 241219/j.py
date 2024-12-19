from io import TextIOBase, StringIO

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


def load(src: TextIOBase) -> tuple[set[str], list[str]]:
    towels = set()
    designs = []
    for line in src:
        if ',' in line:
            towels.update(
                set(line.split(', '))
            )
        elif line.strip():
            designs.append(line.strip())
    return towels, designs


def solvable(towels: set[str], design: str) -> bool:
    if design in towels:
        return True
    ml = max(map(len, towels))
    for i in range(1, min(len(design), ml)):
        if (
            solvable(towels, design[:i]) and
            solvable(towels, design[i:])
        ):
            towels.add(design[:i])
            towels.add(design[i:])
            return True
    return False


def test_example() -> None:
    towels, designs = load(StringIO(EXAMPLE))
    assert solvable(towels, 'brwrr')
    assert solvable(towels, 'bwurrg')
    assert not solvable(towels, 'ubwu')
    assert len(designs) == 8
    assert sum(1 for design in designs if solvable(towels, design))
