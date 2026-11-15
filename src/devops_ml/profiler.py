"""Latency profiling, in-memory metrics sink, and synthetic load runner."""

from __future__ import annotations

import math
import threading
import time
from collections import defaultdict
from collections.abc import Callable, Iterator
from contextlib import contextmanager

from src.devops_ml.contracts import LatencyProfile


def _percentile(sorted_values: list[float], pct: float) -> float:
    if not sorted_values:
        return 0.0
    if len(sorted_values) == 1:
        return sorted_values[0]
    rank = (pct / 100.0) * (len(sorted_values) - 1)
    low = math.floor(rank)
    high = math.ceil(rank)
    if low == high:
        return sorted_values[low]
    fraction = rank - low
    return sorted_values[low] + (sorted_values[high] - sorted_values[low]) * fraction


class InMemoryMetricsSink:
    """Thread-safe metrics sink suitable for hermetic tests and local instrumentation."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.counters: dict[tuple[str, tuple[tuple[str, str], ...]], float] = defaultdict(float)
        self.histograms: dict[tuple[str, tuple[tuple[str, str], ...]], list[float]] = defaultdict(list)
        self.gauges: dict[tuple[str, tuple[tuple[str, str], ...]], float] = {}

    @staticmethod
    def _key(name: str, labels: dict[str, str] | None) -> tuple[str, tuple[tuple[str, str], ...]]:
        label_tuple = tuple(sorted((k, str(v)) for k, v in (labels or {}).items()))
        return (name, label_tuple)

    def increment_counter(self, name: str, value: float = 1.0, labels: dict[str, str] | None = None) -> None:
        if value < 0:
            raise ValueError("Counter increment must be non-negative.")
        with self._lock:
            self.counters[self._key(name, labels)] += float(value)

    def observe_latency(self, metric_name: str, duration_ms: float, labels: dict[str, str] | None = None) -> None:
        if duration_ms < 0:
            raise ValueError("Observed duration_ms must be non-negative.")
        with self._lock:
            self.histograms[self._key(metric_name, labels)].append(float(duration_ms))

    def set_gauge(self, name: str, value: float, labels: dict[str, str] | None = None) -> None:
        with self._lock:
            self.gauges[self._key(name, labels)] = float(value)


class LatencyProfiler:
    """High-resolution wall-clock profiler for pipeline compute paths."""

    def __init__(self) -> None:
        self._samples_ms: list[float] = []
        self._lock = threading.Lock()

    def record(self, duration_ms: float) -> None:
        if duration_ms < 0 or not math.isfinite(duration_ms):
            raise ValueError("duration_ms must be finite and >= 0.")
        with self._lock:
            self._samples_ms.append(float(duration_ms))

    @contextmanager
    def measure(self) -> Iterator[None]:
        start = time.perf_counter()
        try:
            yield
        finally:
            elapsed_ms = (time.perf_counter() - start) * 1000.0
            self.record(elapsed_ms)

    def summarize(self, elapsed_total_ms: float | None = None) -> LatencyProfile:
        with self._lock:
            ordered = sorted(self._samples_ms)
        count = len(ordered)
        if count == 0:
            return LatencyProfile(
                sample_count=0,
                min_ms=0.0,
                max_ms=0.0,
                mean_ms=0.0,
                p50_ms=0.0,
                p95_ms=0.0,
                p99_ms=0.0,
                throughput_ops_sec=0.0,
            )
        total_ms = sum(ordered)
        wall_ms = elapsed_total_ms if (elapsed_total_ms is not None and elapsed_total_ms > 0) else max(total_ms, 1e-6)
        throughput = (count * 1000.0) / wall_ms
        return LatencyProfile(
            sample_count=count,
            min_ms=ordered[0],
            max_ms=ordered[-1],
            mean_ms=total_ms / count,
            p50_ms=_percentile(ordered, 50.0),
            p95_ms=_percentile(ordered, 95.0),
            p99_ms=_percentile(ordered, 99.0),
            throughput_ops_sec=throughput,
        )


def run_synthetic_load(
    operation: Callable[[int], object],
    iterations: int = 200,
    max_p95_ms: float = 50.0,
) -> LatencyProfile:
    """Execute deterministic synthetic iterations and validate latency SLA."""
    if iterations < 1:
        raise ValueError("iterations must be >= 1.")
    if max_p95_ms <= 0:
        raise ValueError("max_p95_ms must be > 0.")

    profiler = LatencyProfiler()
    suite_start = time.perf_counter()
    for idx in range(iterations):
        with profiler.measure():
            operation(idx)
    total_ms = (time.perf_counter() - suite_start) * 1000.0
    profile = profiler.summarize(elapsed_total_ms=total_ms)
    if profile.p95_ms > max_p95_ms:
        raise TimeoutError(
            f"Synthetic load p95 latency {profile.p95_ms:.3f}ms exceeded SLA budget {max_p95_ms:.3f}ms."
        )
    return profile
