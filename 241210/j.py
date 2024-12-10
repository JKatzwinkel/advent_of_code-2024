from __future__ import annotations

from io import StringIO, TextIOBase


def load(src: TextIOBase) -> Topo:
    result = Topo()
    z = 0
    for line in src:
        if not (payload := line.split('\n')[0].strip()):
            continue
        _load_line(z, payload, result)
        z += 1
    result.height = z
    return result


def _load_line(z: int, line: str, topo: Topo) -> None:
    elevations = []
    for x, char in enumerate(line):
        if char == '.':
            elevations.append(-1)
            continue
        elevations.append(int(char))
    topo.elevation.extend(elevations)
    topo.width = x + 1


def test_load_topo() -> None:
    src = StringIO('''
        0123
        1234
        8765
        9876
    ''')
    topo = load(src)
    assert topo.height == 4
    assert topo.width == 4
    assert topo[1, 1] == 2


class Topo:
    def __init__(self) -> None:
        self.width = 0
        self.height = 0
        self.elevation: list[int] = []

    def __getitem__(self, pos: tuple[int, int]) -> int:
        x, z = pos
        return self.elevation[x + z * self.width]
