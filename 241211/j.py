from __future__ import annotations

from math import floor, log10

import pytest


def read(line: str) -> list[int]:
    '''
    >>> read('0 1 10 99 999 ')
    [0, 1, 10, 99, 999]
    '''
    return list(map(int, line.strip().split()))


def sstr(stones: list[int]) -> str:
    return ' '.join(map(str, stones))


def digits(number: int) -> int:
    '''
    >>> digits(0)
    1

    >>> digits(10)
    2
    '''
    if number < 1:
        return 1
    return floor(log10(number)) + 1


def change(stone: int) -> list[int]:
    if stone == 0:
        return [1]
    if not (dig := digits(stone)) % 2:
        ss = str(stone)
        return [int(ss[:dig//2]), int(ss[dig//2:])]
    return [stone * 2024]


def test_change_rules() -> None:
    assert change(99) == [9, 9]


def blink(stones: list[int], times: int = 1) -> list[int]:
    result = [
        new_stone
        for stone in stones
        for new_stone in change(stone)
    ]
    if times == 1:
        return result
    return blink(result, times - 1)


@pytest.mark.parametrize(
    'stones,results',
    [
        (
            '0 1 10 99 999',
            ['1 2024 1 0 9 9 2021976']
        ),
        (
            '125 17',
            [
                '253000 1 7',
                '253 0 2024 14168',
                '512072 1 20 24 28676032',
                '512 72 2024 2 0 2 4 2867 6032',
                '1036288 7 2 20 24 4048 1 4048 8096 28 67 60 32',
                '2097446912 14168 4048 2 0 2 4 40 48 2024 40 48 '
                '80 96 2 8 6 7 6 0 3 2'
            ]
        ),
    ]
)
def test_blink(stones: str, results: list[str]) -> None:
    for result in results:
        iteration = sstr(blink(read(stones)))
        assert iteration == result, (
            f'{stones} should have blinked into {result} but became '
            f'{iteration}'
        )
        stones = iteration


def test_blink_n_times() -> None:
    assert len(blink(read('125 17'), 6)) == 22
    assert len(blink(read('125 17'), 25)) == 55312


def test_input() -> None:
    stones = read('4022724 951333 0 21633 5857 97 702 6')
    assert len(blink(stones, 25)) == 211306


if __name__ == '__main__':
    stones = read('4022724 951333 0 21633 5857 97 702 6')
    for _ in range(25):
        stones = blink(stones)
    print(len(stones))
