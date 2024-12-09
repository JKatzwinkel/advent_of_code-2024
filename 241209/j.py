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


def test_update_block_size() -> None:
    fs = FS.decode('12345')
    assert str(fs) == str(fs.with_block_size_1())


def test_mv_file() -> None:
    fs = FS.of('0..111').with_block_size_1()
    assert f'{fs.mv_file(5, 1)}' == '01.11.'
    fs = FS.decode('13202')
    assert str(fs) == '0...1122'
    assert fs.segms == [('0', 1), ('.', 3), ('1', 2), ('2', 2)]
    assert str(fs.mv_file(3, 1)) == '022.11..'


@pytest.mark.parametrize(
    'blocks,frag',
    [
        ('11.2.33', '11323..'),
        ('0..111....22222', '022111222......'),
        (
            '00...111...2...333.44.5555.6666.777.888899',
            '0099811188827773336446555566..............'
        )
    ]
)
def test_fragmentation(blocks: str, frag: str) -> None:
    assert str(
        FS.of(blocks).with_block_size_1().compact()
    ) == frag


def test_compaction() -> None:
    dense = '2333133121414131402'
    assert str(FS.decode(dense).compact()) == (
        '00992111777.44.333....5555.6666.....8888..'
    )


class FS:
    def __init__(self, segms: list[tuple[str, int]]):
        self.segms = segms

    def __str__(self) -> str:
        return ''.join(
            segm[0] * segm[1] for segm in self.segms
        )

    @classmethod
    def of(cls, decoded: str) -> Self:
        return cls([(c, 1) for c in decoded])

    @classmethod
    def decode(cls, encoded: str) -> Self:
        segms: list[tuple[str, int]] = []
        file_id = 0
        gap_mode = False
        for char in encoded:
            segms.append(
                (f'{file_id}' if not gap_mode else '.', int(char))
            )
            if not gap_mode:
                file_id += 1
            gap_mode = not gap_mode
        return cls([segm for segm in segms if segm[1]])

    def to_list(self) -> list:
        list_repr = []
        list_repr.extend(
            [segm[0]] * segm[1] for segm in self.segms
        )
        return list_repr

    def with_block_size_1(self) -> Self:
        blocks = []
        for segm in self.segms:
            blocks += [(segm[0], 1)] * segm[1]
        return self.__class__(blocks)

    def _find_first_gap_of_size(
        self, size: int, before_index: int
    ) -> int:
        for i, segm in enumerate(self.segms):
            if i >= before_index:
                break
            if segm[0] != '.':
                continue
            if segm[1] >= size:
                return i
        return -1

    def mv_file(self, right: int, left: int) -> Self:
        file = self.segms[right]
        gap = self.segms[left]
        self.segms[left] = ('.', gap[1] - file[1])
        self.segms[right] = ('.', file[1])
        self.segms.insert(left, (file[0], file[1]))
        return self

    def compact(self) -> Self:
        right = len(self.segms) - 1
        while right > 0:
            while (
                (segm := self.segms[right])[0] == '.' and segm[1]
                or not segm[1]
            ):
                right -= 1
            if (
                left := self._find_first_gap_of_size(segm[1], right)
            ) > -1:
                self.mv_file(right, left)
            else:
                right -= 1
        return self

    def checksum(self) -> int:
        result = 0
        for i, char in enumerate(self.to_list()):
            if char == '.':
                continue
            result += i * int(char)
        return result


def test_example_part1() -> None:
    dense = '2333133121414131402'
    fs = FS.decode(dense)
    assert f'{fs.with_block_size_1().compact()}' == (
        '0099811188827773336446555566..............'
    )
    assert fs.with_block_size_1().compact().checksum() == 1928


def test_example_part2() -> None:
    dense = '2333133121414131402'
    fs = FS.decode(dense)
    assert fs.compact().checksum() == 2858


if __name__ == '__main__':
    with open('input.txt') as f:
        dense = f.read().split('\n')[0]
    fs = FS.decode(dense)
    result_1 = fs.with_block_size_1().compact().checksum()
    print(f'checksum of fragmented fs: {result_1}')
    result_2 = FS.decode(dense).compact().checksum()
    print(f'checksum after non-fragmenting compaction: {result_2}')
