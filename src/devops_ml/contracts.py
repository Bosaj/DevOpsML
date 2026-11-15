"""Typed domain schemas, DTOs, and service interfaces for DevOpsML."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Protocol


def _require_non_empty(value: str, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string.")
    return value.strip()


def _require_finite(value: float, field_name: str, minimum: float | None = None) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field_name} must be numeric.")
    numeric = float(value)
    if not math.isfinite(numeric):
        raise ValueError(f"{field_name} must be finite.")
    if minimum is not None and numeric < minimum:
        raise ValueError(f"{field_name} must be >= {minimum}.")
    return numeric


@dataclass(frozen=True)
class PipelineStageConfig:
    """Typed declaration of an executable ML pipeline stage."""

    stage_id: str
    kind: str
    dependencies: tuple[str, ...] = ()
    timeout_seconds: float = 30.0
    params: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "stage_id", _require_non_empty(self.stage_id, "stage_id"))
        object.__setattr__(self, "kind", _require_non_empty(self.kind, "kind"))
        _require_finite(self.timeout_seconds, "timeout_seconds", minimum=0.001)
        if self.stage_id in self.dependencies:
            raise ValueError(f"Stage '{self.stage_id}' cannot depend on itself.")


@dataclass(frozen=True)
class PipelineRunRequest:
    """Validated request DTO for executing a pipeline DAG."""

    run_id: str
    model_name: str
    dataset_version: str
    features: tuple[tuple[float, ...], ...]
    dry_run: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "run_id", _require_non_empty(self.run_id, "run_id"))
        object.__setattr__(self, "model_name", _require_non_empty(self.model_name, "model_name"))
        object.__setattr__(self, "dataset_version", _require_non_empty(self.dataset_version, "dataset_version"))
        if not self.features:
            raise ValueError("features must contain at least one observation vector.")
        width = len(self.features[0])
        if width == 0:
            raise ValueError("Each feature vector must contain at least one numeric feature.")
        for idx, row in enumerate(self.features):
            if len(row) != width:
                raise ValueError(f"Feature row {idx} width {len(row)} != expected {width}.")
            for col, val in enumerate(row):
                _require_finite(val, f"features[{idx}][{col}]")


@dataclass(frozen=True)
class StageExecutionResult:
    """Result DTO produced by executing a single pipeline stage."""

    stage_id: str
    status: str
    duration_ms: float
    metrics: dict[str, float] = field(default_factory=dict)
    artifacts: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "stage_id", _require_non_empty(self.stage_id, "stage_id"))
        if self.status not in {"SUCCEEDED", "SKIPPED", "FAILED"}:
            raise ValueError(f"Unsupported stage status: {self.status}")
        _require_finite(self.duration_ms, "duration_ms", minimum=0.0)


@dataclass(frozen=True)
class LatencyProfile:
    """Aggregated percentile compute latency summary."""

    sample_count: int
    min_ms: float
    max_ms: float
    mean_ms: float
    p50_ms: float
    p95_ms: float
    p99_ms: float
    throughput_ops_sec: float


@dataclass(frozen=True)
class PipelineRunResult:
    """End-to-end execution outcome for a pipeline run."""

    run_id: str
    status: str
    execution_order: tuple[str, ...]
    stage_results: tuple[StageExecutionResult, ...]
    total_duration_ms: float
    quality_index: float


@dataclass(frozen=True)
class ModelArtifactRecord:
    """Versioned model artifact metadata tracked by the registry."""

    name: str
    version: str
    sha256_digest: str
    stage: str
    metrics: dict[str, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "name", _require_non_empty(self.name, "name"))
        object.__setattr__(self, "version", _require_non_empty(self.version, "version"))
        digest = _require_non_empty(self.sha256_digest, "sha256_digest")
        if len(digest) != 64 or any(c not in "0123456789abcdefABCDEF" for c in digest):
            raise ValueError("sha256_digest must be a valid 64-character hex SHA-256 string.")
        if self.stage not in {"development", "staging", "production", "archived"}:
            raise ValueError(f"Unsupported model stage: {self.stage}")


@dataclass(frozen=True)
class HealthSnapshot:
    """Structured liveness/readiness health probe DTO."""

    service: str
    status: str
    liveness: bool
    readiness: bool
    timestamp: float
    details: dict[str, Any] = field(default_factory=dict)


class MetricsSink(Protocol):
    """Decoupled observability sink protocol."""

    def increment_counter(self, name: str, value: float = 1.0, labels: dict[str, str] | None = None) -> None:
        ...

    def observe_latency(self, metric_name: str, duration_ms: float, labels: dict[str, str] | None = None) -> None:
        ...

    def set_gauge(self, name: str, value: float, labels: dict[str, str] | None = None) -> None:
        ...


class StageRunner(Protocol):
    """Strategy interface for executing individual pipeline stages."""

    def execute(
        self,
        stage: PipelineStageConfig,
        request: PipelineRunRequest,
        prior_outputs: dict[str, StageExecutionResult],
    ) -> StageExecutionResult:
        ...


class ModelEvaluator(Protocol):
    """Decoupled interface for computing deterministic model quality metrics."""

    def score_batch(self, weights: tuple[float, ...], bias: float, features: tuple[tuple[float, ...], ...]) -> dict[str, float]:
        ...
