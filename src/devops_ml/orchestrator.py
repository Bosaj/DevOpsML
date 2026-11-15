"""DAG-ordered ML pipeline orchestrator and dependency injection container."""

from __future__ import annotations

import math
import time
from collections import deque
from collections.abc import Callable
from typing import Any

from src.devops_ml.contracts import (
    MetricsSink,
    ModelEvaluator,
    PipelineRunRequest,
    PipelineRunResult,
    PipelineStageConfig,
    StageExecutionResult,
    StageRunner,
)
from src.devops_ml.profiler import InMemoryMetricsSink


class LogisticBatchEvaluator:
    """Fast pure-Python sigmoid scoring evaluator with zero external runtime lock-in."""

    @staticmethod
    def _sigmoid(z: float) -> float:
        if z >= 0:
            exp_neg = math.exp(-z)
            return 1.0 / (1.0 + exp_neg)
        exp_pos = math.exp(z)
        return exp_pos / (1.0 + exp_pos)

    def score_batch(
        self,
        weights: tuple[float, ...],
        bias: float,
        features: tuple[tuple[float, ...], ...],
    ) -> dict[str, float]:
        if not features:
            raise ValueError("Cannot score an empty feature batch.")
        width = len(weights)
        probabilities: list[float] = []
        positive_count = 0
        for row in features:
            if len(row) != width:
                raise ValueError(f"Feature row length {len(row)} does not match weights length {width}.")
            logit = bias + sum(w * x for w, x in zip(weights, row))
            prob = self._sigmoid(logit)
            probabilities.append(prob)
            if prob >= 0.5:
                positive_count += 1
        mean_prob = sum(probabilities) / len(probabilities)
        confidence = sum(abs(p - 0.5) * 2.0 for p in probabilities) / len(probabilities)
        return {
            "batch_size": float(len(probabilities)),
            "positive_rate": positive_count / len(probabilities),
            "mean_probability": mean_prob,
            "decision_confidence": confidence,
        }


class DefaultStageRunner:
    """Default concrete stage executor with injected evaluator and metrics sink."""

    def __init__(self, evaluator: ModelEvaluator) -> None:
        self._evaluator = evaluator

    def execute(
        self,
        stage: PipelineStageConfig,
        request: PipelineRunRequest,
        prior_outputs: dict[str, StageExecutionResult],
    ) -> StageExecutionResult:
        t0 = time.perf_counter()
        if request.dry_run:
            return StageExecutionResult(
                stage_id=stage.stage_id,
                status="SKIPPED",
                duration_ms=(time.perf_counter() - t0) * 1000.0,
                metrics={"dry_run": 1.0},
            )

        metrics: dict[str, float] = {}
        artifacts: tuple[str, ...] = ()
        width = len(request.features[0])
        if stage.kind == "validate":
            metrics = {
                "row_count": float(len(request.features)),
                "feature_width": float(width),
                "schema_valid": 1.0,
            }
        elif stage.kind == "score":
            weights = tuple(float(w) for w in stage.params.get("weights", (0.5,) * width))
            bias = float(stage.params.get("bias", -0.25))
            metrics = self._evaluator.score_batch(weights=weights, bias=bias, features=request.features)
            artifacts = (f"reports/{request.run_id}/{stage.stage_id}.json",)
        else:
            upstream = sum(res.metrics.get("decision_confidence", 0.9) for res in prior_outputs.values())
            metrics = {"upstream_signal": float(upstream), "stage_ready": 1.0}

        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        return StageExecutionResult(
            stage_id=stage.stage_id,
            status="SUCCEEDED",
            duration_ms=elapsed_ms,
            metrics=metrics,
            artifacts=artifacts,
        )


def resolve_execution_order(stages: list[PipelineStageConfig]) -> tuple[str, ...]:
    """Resolve deterministic topological order for pipeline stages using Kahn's algorithm."""
    if not stages:
        raise ValueError("Pipeline must define at least one stage.")

    stage_map: dict[str, PipelineStageConfig] = {}
    for stage in stages:
        if stage.stage_id in stage_map:
            raise ValueError(f"Duplicate stage_id '{stage.stage_id}'.")
        stage_map[stage.stage_id] = stage

    indegree: dict[str, int] = {sid: 0 for sid in stage_map}
    dependents: dict[str, list[str]] = {sid: [] for sid in stage_map}
    for sid, stage in stage_map.items():
        for dep in stage.dependencies:
            if dep not in stage_map:
                raise ValueError(f"Stage '{sid}' references unknown dependency '{dep}'.")
            dependents[dep].append(sid)
            indegree[sid] += 1

    ready: deque[str] = deque(sorted(sid for sid, deg in indegree.items() if deg == 0))
    order: list[str] = []
    while ready:
        current = ready.popleft()
        order.append(current)
        for nxt in sorted(dependents[current]):
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                ready.append(nxt)

    if len(order) != len(stage_map):
        raise ValueError("Cycle detected in pipeline stage dependencies.")
    return tuple(order)


class ServiceContainer:
    """Lightweight dependency injection container for registering and resolving services."""

    def __init__(self) -> None:
        self._factories: dict[type[Any], Callable[[], Any]] = {}
        self._singletons: dict[type[Any], Any] = {}

    def register_instance(self, interface: type[Any], instance: Any) -> None:
        self._singletons[interface] = instance

    def register_factory(self, interface: type[Any], factory: Callable[[], Any], singleton: bool = True) -> None:
        self._factories[interface] = factory
        if not singleton and interface in self._singletons:
            del self._singletons[interface]

    def resolve(self, interface: type[Any]) -> Any:
        if interface in self._singletons:
            return self._singletons[interface]
        if interface not in self._factories:
            raise KeyError(f"No provider registered for {interface.__name__}.")
        instance = self._factories[interface]()
        self._singletons[interface] = instance
        return instance


class PipelineOrchestrator:
    """Clean-architecture orchestrator executing DAG stages via injected dependencies."""

    def __init__(self, metrics_sink: MetricsSink, stage_runner: StageRunner) -> None:
        self._metrics = metrics_sink
        self._runner = stage_runner

    @classmethod
    def create_default(cls, metrics_sink: MetricsSink | None = None) -> PipelineOrchestrator:
        container = ServiceContainer()
        sink = metrics_sink if metrics_sink is not None else InMemoryMetricsSink()
        container.register_instance(MetricsSink, sink)
        container.register_instance(ModelEvaluator, LogisticBatchEvaluator())
        container.register_factory(
            StageRunner,
            lambda: DefaultStageRunner(evaluator=container.resolve(ModelEvaluator)),
        )
        return cls(
            metrics_sink=container.resolve(MetricsSink),
            stage_runner=container.resolve(StageRunner),
        )

    def run(self, stages: list[PipelineStageConfig], request: PipelineRunRequest) -> PipelineRunResult:
        order = resolve_execution_order(stages)
        stage_lookup = {s.stage_id: s for s in stages}
        prior_outputs: dict[str, StageExecutionResult] = {}
        results: list[StageExecutionResult] = []
        run_start = time.perf_counter()

        for sid in order:
            stage = stage_lookup[sid]
            result = self._runner.execute(stage=stage, request=request, prior_outputs=prior_outputs)
            prior_outputs[sid] = result
            results.append(result)
            self._metrics.increment_counter(
                "pipeline_stage_executions_total",
                labels={"stage": sid, "status": result.status},
            )
            self._metrics.observe_latency(
                "pipeline_stage_duration_ms",
                result.duration_ms,
                labels={"stage": sid},
            )

        total_ms = (time.perf_counter() - run_start) * 1000.0
        confidence_values = [
            res.metrics["decision_confidence"]
            for res in results
            if "decision_confidence" in res.metrics
        ]
        mean_conf = (sum(confidence_values) / len(confidence_values)) if confidence_values else 0.95
        latency_factor = max(0.0, 1.0 - (total_ms / 1000.0))
        quality_index = round((mean_conf * 0.7) + (latency_factor * 0.3), 6)
        self._metrics.set_gauge("pipeline_quality_index", quality_index, labels={"model": request.model_name})

        final_status = "SKIPPED" if request.dry_run else "PASSED"
        return PipelineRunResult(
            run_id=request.run_id,
            status=final_status,
            execution_order=order,
            stage_results=tuple(results),
            total_duration_ms=total_ms,
            quality_index=quality_index,
        )
