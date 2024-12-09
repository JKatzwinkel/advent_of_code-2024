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
    assert FS.decode(dense).blocks == blocks


class FS:
    def __init__(self, blocks: str = ''):
        self.blocks = blocks

    @classmethod
    def decode(cls, encoded: str) -> Self:
        segm: list[str] = []
        file_id = 0
        gap_mode = False
        for char in encoded:
            segm.append(
                (f'{file_id}' if not gap_mode else '.') * int(char)
            )
            if not gap_mode:
                file_id += 1
            gap_mode = not gap_mode
        return cls(''.join(segm))
