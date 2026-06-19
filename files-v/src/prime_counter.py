"""
Prime number counting implementations.

The naive version mirrors the original specification (with the Python keyword
fixed: ``Break`` -> ``break``). Optimized versions reduce redundant work.
"""


def count_primes_naive(n: int) -> int:
    """Count primes strictly less than *n* using trial division up to *i - 1*.

    Time complexity: O(n^2) in the worst case.
    """
    if n <= 2:
        return 0

    count = 0
    for i in range(2, n):
        for j in range(2, i):
            if i % j == 0:
                break
        else:
            count += 1
    return count


def count_primes_optimized(n: int) -> int:
    """Count primes below *n* using trial division only up to sqrt(i).

    A composite number always has a factor <= sqrt(i), so inner loops stop
    much earlier. Time complexity: O(n * sqrt(n)).
    """
    if n <= 2:
        return 0

    count = 0
    for i in range(2, n):
        if _is_prime_sqrt(i):
            count += 1
    return count


def count_primes_sieve(n: int) -> int:
    """Count primes below *n* with the Sieve of Eratosthenes.

    Marks multiples of each prime instead of re-testing every candidate.
    Time complexity: O(n log log n); space: O(n).
    """
    if n <= 2:
        return 0

    is_composite = [False] * n
    limit = int(n ** 0.5) + 1

    for i in range(2, limit):
        if not is_composite[i]:
            for multiple in range(i * i, n, i):
                is_composite[multiple] = True

    return sum(1 for i in range(2, n) if not is_composite[i])


def count_primes(n: int) -> int:
    """Default entry point: fastest general-purpose implementation."""
    return count_primes_sieve(n)


def _is_prime_sqrt(value: int) -> bool:
    if value < 2:
        return False
    if value == 2:
        return True
    if value % 2 == 0:
        return False

    limit = int(value ** 0.5) + 1
    for divisor in range(3, limit, 2):
        if value % divisor == 0:
            return False
    return True
