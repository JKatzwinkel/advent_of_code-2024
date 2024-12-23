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
        )

    def validate(self, pages: Iterable[int]) -> bool:
        return all(
            self.in_order(a, b)
            for a, b in zip(
                list(pages)[:-1], list(pages)[1:]
            )
        )

    def valid(self) -> list[list[int]]:
        return list(
            filter(self.validate, self.updates)
        )

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


if __name__ == '__main__':
    with open('input.txt') as f:
        updates = load(f)
    print(sum(map(middle_page, updates.valid())))
