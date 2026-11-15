"""Prometheus and fallback in-memory metrics definitions for DevOpsML."""

from __future__ import annotations

try:
    from prometheus_client import Counter, Gauge, Histogram, start_http_server
except ImportError:  # pragma: no cover - local stdlib fallback when prometheus_client is absent

    class _LabeledMetric:
        def __init__(self, initial: float = 0.0) -> None:
            self.value = initial
            self.observations: list[float] = []

        def inc(self, amount: float = 1.0) -> None:
            self.value += amount

        def observe(self, value: float) -> None:
            self.observations.append(float(value))

        def set(self, value: float) -> None:
            self.value = float(value)

    class _FallbackMetric:
        def __init__(self, _name: str, _doc: str, labelnames: list[str] | None = None) -> None:
            self.labelnames = labelnames or []
            self._series: dict[tuple[tuple[str, str], ...], _LabeledMetric] = {}
            self._root = _LabeledMetric()

        def labels(self, **kwargs: str) -> _LabeledMetric:
            key = tuple(sorted((k, str(v)) for k, v in kwargs.items()))
            return self._series.setdefault(key, _LabeledMetric())

        def set(self, value: float) -> None:
            self._root.set(value)

    Counter = _FallbackMetric
    Gauge = _FallbackMetric
    Histogram = _FallbackMetric

    def start_http_server(port: int = 8000) -> None:
        print(f"Fallback metrics exporter initialized for port {port}")


# Metric Definitions for DevOpsML
REQUEST_COUNT = Counter(
    "app_requests_total", "Total HTTP/API Requests", ["method", "endpoint", "status"]
)
REQUEST_LATENCY = Histogram(
    "app_request_duration_seconds", "Request duration in seconds", ["endpoint"]
)
EVALUATION_SCORE = Gauge(
    "model_evaluation_score", "Latest evaluation score", ["metric_name"]
)
APP_HEALTH_STATUS = Gauge(
    "app_health_status", "Application health status (1=healthy, 0=unhealthy)"
)


def record_request(method, endpoint, status, duration):
    REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=status).inc()
    REQUEST_LATENCY.labels(endpoint=endpoint).observe(duration)


def update_eval_metric(name, value):
    EVALUATION_SCORE.labels(metric_name=name).set(value)


def set_health_status(is_healthy):
    APP_HEALTH_STATUS.set(1 if is_healthy else 0)


def start_metrics_exporter(port=8000):
    start_http_server(port)
    print(f"Metrics exporter running on port {port}")
