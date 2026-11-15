"""Modular clean-architecture core for DevOpsML pipelines and observability."""

from src.devops_ml.contracts import (
    HealthSnapshot,
    LatencyProfile,
    MetricsSink,
    ModelArtifactRecord,
    ModelEvaluator,
    PipelineRunRequest,
    PipelineRunResult,
    PipelineStageConfig,
    StageExecutionResult,
    StageRunner,
)
from src.devops_ml.orchestrator import PipelineOrchestrator, ServiceContainer
from src.devops_ml.profiler import (
    InMemoryMetricsSink,
    LatencyProfiler,
    run_synthetic_load,
)
from src.devops_ml.registry import ModelArtifactRegistry

__all__ = [
    "HealthSnapshot",
    "InMemoryMetricsSink",
    "LatencyProfile",
    "LatencyProfiler",
    "MetricsSink",
    "ModelArtifactRecord",
    "ModelArtifactRegistry",
    "ModelEvaluator",
    "PipelineOrchestrator",
    "PipelineRunRequest",
    "PipelineRunResult",
    "PipelineStageConfig",
    "ServiceContainer",
    "StageExecutionResult",
    "StageRunner",
    "run_synthetic_load",
]
