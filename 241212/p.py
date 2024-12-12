import itertools
import os

from j import (
    DIRS,
    Direction, Garden, Point, Region, Side,
    rotate, step_into,
)


class Plotter:
    SIDES = '-|-|'
    ANSI_FG = [
        f'\033[{color}m' for color in (
            30, 31, 32, 33, 34, 35, 36, 37, 91,
            92, 93, 94, 95, 96
        )
    ]
    ANSI_BG = [
        f'\033[48;2;{r};{g};{b}m'
        for r, g, b in itertools.product(
            range(40, 160, 40),
            range(40, 160, 40),
            range(40, 160, 40),
        )
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
                :min(len(self.grid), vh)
            ]
        )

    def _plot_sides(self, region: Region) -> None:
        for i, side in enumerate(region.sides):
            self._plot_side(side, i)

    def _plot_side(self, side: Side, i: int) -> None:
        x, z = step_into(
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
        self._plot_border(x, z, side.facing, i)
        while (x, z) != target:
            if x < target[0]:
                x += 1
            elif x > target[0]:
                x -= 1
            if z < target[1]:
                z += 1
            elif z > target[1]:
                z -= 1
            self._plot_border(x, z, side.facing, i)

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
                x, y = step_into((1, 1), scale(plot, 2))
                self._draw(
                    x, y, region.plant,
                    color=ord(region.plant), fg=False
                )


def scale(pos: Point, factor: float) -> Point:
    return int(pos[0] * factor), int(pos[1] * factor)
