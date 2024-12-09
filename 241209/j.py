from __future__ import annotations

from typing import Self

import pytest


@pytest.mark.parametrize(
    'dense,blocks',
    [
        ('12345', '0..111....22222'),
        (
            '2333133121414131402',
            '00...111...2...333.44.5555.6666.777.888899'
        ),
    ]
)
def test_decode_dense_format(dense: str, blocks: str) -> None:
    assert f'{FS.decode(dense)}' == blocks


@pytest.mark.parametrize(
    'blocks,defrag',
    [
        ('11.2.33', '11323..'),
        ('0..111....22222', '022111222......'),
        (
            '00...111...2...333.44.5555.6666.777.888899',
            '0099811188827773336446555566..............'
        )
    ]
)
def test_defrag(blocks: str, defrag: str) -> None:
    assert str(FS.of(blocks).defrag()) == defrag


class FS:
    def __init__(self, blocks: list[str]):
        self.blocks = blocks

    def __str__(self) -> str:
        return ''.join(self.blocks)

    @classmethod
    def of(cls, decoded: str) -> Self:
        return cls([c for c in decoded])

    @classmethod
    def decode(cls, encoded: str) -> Self:
        blocks: list[str] = []
        file_id = 0
        gap_mode = False
        for char in encoded:
            for _ in range(int(char)):
                blocks.append(f'{file_id}' if not gap_mode else '.')
            if not gap_mode:
                file_id += 1
            gap_mode = not gap_mode
        return cls(blocks)

    def defrag(self) -> Self:
        left = 0
        right = len(self.blocks) - 1
        while left < right:
            while self.blocks[right] == '.':
                right -= 1
            while self.blocks[left] != '.':
                left += 1
            if left > right:
                break
            self.blocks[left], self.blocks[right] = (
                self.blocks[right], self.blocks[left]
            )
        return self

    def checksum(self) -> int:
        result = 0
        for i, char in enumerate(self.blocks):
            if char == '.':
                continue
            result += i * int(char)
        return result


def test_example() -> None:
    dense = '2333133121414131402'
    fs = FS.decode(dense)
    assert f'{fs.defrag()}' == (
        '0099811188827773336446555566..............'
    )
    assert fs.defrag().checksum() == 1928
