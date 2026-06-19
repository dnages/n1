"""Unit tests for prime counter implementations."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from prime_counter import (  # noqa: E402
    count_primes,
    count_primes_naive,
    count_primes_optimized,
    count_primes_sieve,
)

IMPLEMENTATIONS = [
    count_primes_naive,
    count_primes_optimized,
    count_primes_sieve,
    count_primes,
]

# Known counts: pi(n) = number of primes strictly less than n.
KNOWN_COUNTS = {
    0: 0,
    1: 0,
    2: 0,
    3: 1,
    10: 4,
    100: 25,
    1000: 168,
    10000: 1229,
}


@pytest.mark.parametrize("func", IMPLEMENTATIONS, ids=lambda f: f.__name__)
@pytest.mark.parametrize("n,expected", list(KNOWN_COUNTS.items()))
def test_known_prime_counts(func, n, expected):
    assert func(n) == expected


@pytest.mark.parametrize("func", IMPLEMENTATIONS, ids=lambda f: f.__name__)
def test_all_implementations_agree(func):
    for n in range(0, 500):
        assert func(n) == count_primes_sieve(n)


def test_default_alias_uses_sieve():
    assert count_primes(1000) == count_primes_sieve(1000)
