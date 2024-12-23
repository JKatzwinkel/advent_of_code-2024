from __future__ import annotations

from collections import defaultdict
from io import StringIO, TextIOBase
from typing import Iterable, Iterator, Self


def load(src: TextIOBase) -> Updates:
    result = Updates()
    for line in src:
        if not (specs := line.strip()):
            continue
        if '|' in specs:
            a, b = specs.split('|')
            result.add_order(int(a), int(b))
        else:
            result.updates.append(
                list(eval(specs))
            )
    return result


class Updates(Iterable[list[int]]):
    def __init__(self) -> None:
        self.order: dict[int, Order] = defaultdict(Order)
        self.updates: list[list[int]] = []

    def add_order(self, left: int, right: int) -> Self:
        self.order[left].page = left
        self.order[left].comes_before.add(right)
        self.order[right].page = right
        self.order[right].comes_after.add(left)
        return self

    def in_order(self, left: int, right: int) -> bool:
        return (
            right in self.order[left].comes_before or
            left in self.order[right].comes_after
        ) and not (
            right in self.order[left].comes_after or
            left in self.order[right].comes_before
        )

    def validate(self, pages: Iterable[int]) -> bool:
        return all(
            self.in_order(a, b)
            for a, b in zip(
                list(pages)[:-1], list(pages)[1:]
            )
        )

    def valid(self) -> list[list[int]]:
        return list(filter(self.validate, self))

    def invalid(self) -> list[list[int]]:
        return [
            pages for pages in self
            if not self.validate(pages)
        ]

    def fix(self, pages: Iterable[int]) -> list[int]:
        pages = list(pages)
        if len(pages) == 1:
            return pages
        left = self.fix(pages[:len(pages) // 2])
        right = self.fix(pages[len(pages) // 2:])
        merged = []
        while left and right:
            merged.append(
                left.pop(0)
                if self.in_order(left[0], right[0])
                else right.pop(0)
            )
        merged.extend(left)
        merged.extend(right)
        return merged

    def __contains__(self, pages: list[int]) -> bool:
        return pages in self.updates

    def __iter__(self) -> Iterator[list[int]]:
        self._iter = iter(self.updates)
        return self._iter

    def __next__(self) -> list[int]:
        return next(self._iter)


class Order:
    def __init__(self) -> None:
        self.page = 0
        self.comes_after: set[int] = set()
        self.comes_before: set[int] = set()

    def __repr__(self) -> str:
        return (
            f'page {self.page} comes after {self.comes_after}'
            f' and before {self.comes_before}'
        )


def middle_page(pages: list[int]) -> int:
    '''
    >>> middle_page((75, 47, 61, 53, 29))
    61

    >>> middle_page([75, 29, 13])
    29
    '''
    return pages[len(pages) // 2]


SAMPLE = '''
47|53
97|13
97|61
97|47
75|29
61|13
75|53
29|13
97|29
53|29
61|53
97|53
61|29
47|13
75|47
97|75
47|61
75|61
47|29
75|13
53|13

75,47,61,53,29
97,61,53,29,13
75,29,13
75,97,47,61,53
61,13,29
97,13,75,29,47'''


def test_load() -> None:
    updates = load(StringIO(SAMPLE))
    assert [75, 47, 61, 53, 29] in updates
    assert 47 in updates.order[53].comes_after


def test_validate_order() -> None:
    updates = load(StringIO(SAMPLE))
    assert updates.validate((75, 47, 61, 53, 29))
    assert [
        updates.validate(update) for update in updates
    ] == [
        True, True, True,
        False, False, False
    ]


def test_middle_pages_of_valid() -> None:
    updates = load(StringIO(SAMPLE))
    assert sum(map(middle_page, updates.valid())) == 143


def test_fix_order() -> None:
    updates = load(StringIO(SAMPLE))
    fixed = [
        updates.fix(pages) for pages in updates.invalid()
    ]
    print(updates.order[13])
    print(updates.order[97])
    assert fixed == [
        [97, 75, 47, 61, 53],
        [61, 29, 13],
        [97, 75, 47, 29, 13],
    ]


def test_fix_single_order() -> None:
    updates = load(StringIO(SAMPLE))
    fixed = updates.fix([97, 13, 75, 29, 47])
    assert fixed == [97, 75, 47, 29, 13]


if __name__ == '__main__':
    with open('input.txt') as f:
        updates = load(f)
    print('part 1:', sum(map(middle_page, updates.valid())))
    print(
        'part 2:', sum(
            map(
                middle_page,
                map(updates.fix, updates.invalid())
            )
        )
    )
