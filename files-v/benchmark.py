#!/usr/bin/env python3
"""
Compare runtime of naive vs optimized prime counters.

Uses ``timeit`` for repeatable measurements and ``cProfile`` to highlight
where the naive implementation spends its time.
"""

from __future__ import annotations

import argparse
import cProfile
import io
import json
import pstats
import sys
import time
import timeit
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from prime_counter import (  # noqa: E402
    count_primes_naive,
    count_primes_optimized,
    count_primes_sieve,
)

IMPLEMENTATIONS = {
    "naive": count_primes_naive,
    "optimized_sqrt": count_primes_optimized,
    "sieve": count_primes_sieve,
}


def run_timeit(name: str, func, n: int, repeats: int) -> dict:
    timer = timeit.Timer(stmt="func(n)", setup="pass", globals={"func": func, "n": n})
    samples = timer.repeat(repeat=repeats, number=1)
    best = min(samples)
    return {
        "name": name,
        "n": n,
        "result": func(n),
        "seconds_best": best,
        "seconds_mean": sum(samples) / len(samples),
        "seconds_worst": max(samples),
        "repeats": repeats,
    }


def profile_naive(n: int, top_n: int = 15) -> str:
    profiler = cProfile.Profile()
    profiler.enable()
    count_primes_naive(n)
    profiler.disable()

    stream = io.StringIO()
    stats = pstats.Stats(profiler, stream=stream).sort_stats("cumulative")
    stats.print_stats(top_n)
    return stream.getvalue()


def print_table(results: list[dict]) -> None:
    print("\nBenchmark results")
    print("-" * 72)
    print(f"{'Implementation':<18} {'n':>8} {'Result':>8} {'Best (s)':>12} {'Mean (s)':>12}")
    print("-" * 72)
    for row in results:
        print(
            f"{row['name']:<18} {row['n']:>8} {row['result']:>8} "
            f"{row['seconds_best']:>12.6f} {row['seconds_mean']:>12.6f}"
        )
    print("-" * 72)

    baseline = next((r for r in results if r["name"] == "naive"), None)
    if baseline and baseline["seconds_best"] > 0:
        print("\nSpeedup vs naive (best run):")
        for row in results:
            if row["name"] == "naive":
                continue
            speedup = baseline["seconds_best"] / row["seconds_best"]
            print(f"  {row['name']:<18} {speedup:>8.1f}x faster")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Benchmark prime counter implementations.")
    parser.add_argument(
        "--sizes",
        nargs="+",
        type=int,
        default=[1000, 5000, 10000],
        help="Values of n to benchmark (count primes below n).",
    )
    parser.add_argument(
        "--repeats",
        type=int,
        default=3,
        help="Number of timed repetitions per implementation.",
    )
    parser.add_argument(
        "--skip-naive-above",
        type=int,
        default=10000,
        help="Skip naive implementation when n exceeds this value.",
    )
    parser.add_argument(
        "--profile-n",
        type=int,
        default=5000,
        help="Run cProfile on the naive implementation for this n.",
    )
    parser.add_argument(
        "--json-out",
        type=Path,
        default=None,
        help="Optional path to write machine-readable benchmark output.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    all_results: list[dict] = []

    for n in args.sizes:
        for name, func in IMPLEMENTATIONS.items():
            if name == "naive" and n > args.skip_naive_above:
                print(f"Skipping naive for n={n} (above --skip-naive-above={args.skip_naive_above})")
                continue
            print(f"Timing {name} for n={n}...")
            all_results.append(run_timeit(name, func, n, args.repeats))

    print_table(all_results)

    print(f"\ncProfile (naive, n={args.profile_n}, top 15 by cumulative time):\n")
    print(profile_naive(args.profile_n))

    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "generated_at_unix": time.time(),
            "results": all_results,
        }
        args.json_out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(f"\nWrote JSON results to {args.json_out}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
