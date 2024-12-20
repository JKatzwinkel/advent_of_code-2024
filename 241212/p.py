import itertools
import math
import random
import os

from j import (
    DIRS,
    Direction, Garden, Point, Region, Side,
    rotate, step_into,
)


type Color = tuple[int, int, int]


def colors(
    limit: int, /,
    brightness: int = 200, *,
    distance: int = 30
) -> list[Color]:
    '''
    >>> len(colors(5))
    5

    >>> max(map(_brightness, colors(10, 160)))
    160

    '''
    results: list[Color] = []
    misses = 0
    jitter = 0
    while len(results) < limit:
        rgb = random_color(
            random.randint(
                max(
                    brightness // 2,
                    brightness - jitter // 2
                ),
                min(
                    brightness * 3 // 2,
                    brightness + jitter // 2
                )
            )
        )
        if all(
            _dist(rgb, col) > distance
            for col in results
        ):
            results.append(rgb)
        else:
            misses += 1
        if misses > 20:
            misses = 0
            jitter += 1
    return results


def random_color(brightness: int = 255) -> Color:
    '''
    >>> rgb = random_color(brightness=100)
    >>> _brightness(rgb) in [99, 100]
    True

    >>> _brightness(random_color(brightness=360)) > 350
    True

    '''
    alpha = random.randint(0, 90) * math.pi / 180
    r = brightness * math.sin(alpha)
    radius = brightness * math.cos(alpha)
    beta = random.randint(0, 90) * math.pi / 180
    g = radius * math.sin(beta)
    b = radius * math.cos(beta)
    r, g, b = (
        min(int(c), 255) for c in (r, g, b)
    )
    while _brightness((r, g, b)) < brightness * .99:
        r, g, b = (
            min(c + 1, 255) for c in (r, g, b)
        )
    return int(r), int(g), int(b)


def _brightness(rgb: Color) -> int:
    '''
    >>> _brightness((100, 40, 40))
    115

    >>> _brightness((255, 255, 255))
    442

    '''
    return round(_dist(rgb, (0, 0, 0)))


def _dist(a: Color, b: Color) -> float:
    '''
    >>> _dist((255, 0, 0), (0, 0, 0))
    255.0

    >>> _dist((100, 100, 0), (0, 0, 0))
    141.4213562373095

    '''
    return float(sum(
        (b[i] - a[i]) ** 2 for i in range(3)
    ) ** .5)


class Plotter:
    SIDES = '-|-|'
    ANSI_FG = [
        f'\033[38;2;{r};{g};{b}m'
        for r, g, b in colors(
            20, brightness=360, distance=40
        )
    ]
    ANSI_BG = [
        f'\033[48;2;{r};{g};{b}m'
        for r, g, b in colors(20, brightness=80)
    ]

    def __init__(
        self, garden: Garden, ansi: bool = True
    ) -> None:
        self.garden = garden
        self.grid: list[list[str]] = [
            [' '] * (garden.width * 2 + 1)
            for z in range(garden.height * 2 + 1)
        ]
        self._ansi = ansi
        self._plot_regions()

    def plot(self, region: Region | None = None) -> str:
        regions = [region] if region else self.garden.regions
        for region in regions:
            self._plot_sides(region)
        try:
            vw, vh = os.get_terminal_size()
        except OSError:
            vw, vh = 100, 100
        return '\n'.join(
            ''.join(
                row[:min(len(row), vw)]
            ) for row in self.grid[
                :min(len(self.grid), vh-1)
            ]
        )

    def _plot_sides(self, region: Region) -> None:
        for i, side in enumerate(region.sides):
            self._plot_side(side, i)

    def _plot_side(self, side: Side, i: int) -> None:
        x, y = step_into(
            rotate(side.facing),
            step_into(
                (1, 1), step_into(
                    side.facing, scale(side.start, 2)
                )
            )
        )
        target = step_into(
            (1, 1), step_into(
                side.facing, scale(side.end, 2)
            )
        )
        self._plot_border(x, y, side.facing, i)
        v = unit((x, y), target)
        while (x, y) != target:
            x, y = step_into(v, (x, y))
            self._plot_border(x, y, side.facing, i)

    def _plot_border(
        self, x: int, y: int,
        direction: Direction, i: int
    ) -> None:
        self._draw(
            x, y, self.__class__.SIDES[
                DIRS.index(direction)
            ] if x % 2 or y % 2 else '+',
            color=i, fg=True
        )

    def _draw(
        self, x: int, y: int, char: str,
        color: int | None = None,
        fg: bool = False
    ) -> None:
        if self._ansi and color:
            choices = self.__class__.ANSI_FG if fg else (
                self.__class__.ANSI_BG
            )
            ansicode = choices[color % len(choices)]
            out = f'{ansicode}{char}\033[00m'
            if not fg:
                out = f'\033[1;37m{out}'
                for i, j in itertools.product(
                    *([[-1, 0, 1]] * 2)
                ):
                    self.grid[y+j][x+i] = (
                        f'{ansicode}'
                        f'{self.grid[y+j][x+i]}\033[00m'
                    )
        else:
            out = f'{char}'
        self.grid[y][x] = out

    def _plot_regions(self) -> None:
        for region in self.garden.regions:
            for plot in region.plots:
                self._draw(
                    *step_into((1, 1), scale(plot, 2)),
                    region.plant,
                    color=ord(region.plant), fg=False
                )


def scale(pos: Point, factor: float) -> Point:
    return int(pos[0] * factor), int(pos[1] * factor)


def unit(a: Point, b: Point) -> Direction:
    '''
    >>> unit((0, 0), (0, 5))
    (0, 1)

    >>> unit((5, 0), (0, 0))
    (-1, 0)

    >>> unit((5, 5), (5, 5))
    (0, 0)
    '''
    x, y = map(
        lambda c: 0 if not c else c // abs(c),
        (b[0] - a[0], b[1] - a[1])
    )
    return x, y
