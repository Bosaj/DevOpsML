"""Comprehensive architecture, validation, registry, and synthetic load tests for DevOpsML."""

from __future__ import annotations

import math
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.devops_ml.contracts import (
    MetricsSink,
    ModelArtifactRecord,
    PipelineRunRequest,
    PipelineStageConfig,
    StageExecutionResult,
)
from src.devops_ml.orchestrator import (
    PipelineOrchestrator,
    ServiceContainer,
    resolve_execution_order,
)
from src.devops_ml.profiler import InMemoryMetricsSink, LatencyProfiler, run_synthetic_load
from src.devops_ml.registry import ModelArtifactRegistry, compute_bytes_sha256


class _StubStageRunner:
    """Custom injected StageRunner verifying decoupled DI architecture."""

    def execute(
        self,
        stage: PipelineStageConfig,
        request: PipelineRunRequest,
        prior_outputs: dict[str, StageExecutionResult],
    ) -> StageExecutionResult:
        return StageExecutionResult(
            stage_id=stage.stage_id,
            status="SUCCEEDED",
            duration_ms=0.25,
            metrics={"decision_confidence": 0.91, "upstream_count": float(len(prior_outputs))},
        )


class TestDevOpsMLArchitecture(unittest.TestCase):
    def test_dto_input_validation_rejects_invalid_inputs(self) -> None:
        with self.assertRaises(ValueError):
            PipelineStageConfig(stage_id=" ", kind="validate")
        with self.assertRaises(ValueError):
            PipelineStageConfig(stage_id="a", kind="validate", dependencies=("a",))
        with self.assertRaises(ValueError):
            PipelineRunRequest(
                run_id="r1",
                model_name="m",
                dataset_version="1.0.0",
                features=(),
            )
        with self.assertRaises(ValueError):
            PipelineRunRequest(
                run_id="r1",
                model_name="m",
                dataset_version="1.0.0",
                features=((1.0, math.nan),),
            )
        with self.assertRaises(ValueError):
            PipelineRunRequest(
                run_id="r1",
                model_name="m",
                dataset_version="1.0.0",
                features=((1.0, 2.0), (1.0,)),
            )

    def test_dag_topological_resolution_and_cycle_rejection(self) -> None:
        stages = [
            PipelineStageConfig(stage_id="deploy", kind="publish", dependencies=("score",)),
            PipelineStageConfig(stage_id="validate", kind="validate"),
            PipelineStageConfig(stage_id="score", kind="score", dependencies=("validate",)),
        ]
        order = resolve_execution_order(stages)
        self.assertEqual(order, ("validate", "score", "deploy"))

        cyclic = [
            PipelineStageConfig(stage_id="a", kind="validate", dependencies=("b",)),
            PipelineStageConfig(stage_id="b", kind="score", dependencies=("a",)),
        ]
        with self.assertRaises(ValueError):
            resolve_execution_order(cyclic)

        with self.assertRaises(ValueError):
            resolve_execution_order(
                [PipelineStageConfig(stage_id="a", kind="validate", dependencies=("missing",))]
            )

    def test_dependency_injection_and_orchestrator_execution(self) -> None:
        container = ServiceContainer()
        sink = InMemoryMetricsSink()
        container.register_instance(MetricsSink, sink)
        resolved_sink = container.resolve(MetricsSink)
        self.assertIs(resolved_sink, sink)

        custom = PipelineOrchestrator(metrics_sink=sink, stage_runner=_StubStageRunner())
        stages = [
            PipelineStageConfig(stage_id="ingest", kind="validate"),
            PipelineStageConfig(stage_id="score", kind="score", dependencies=("ingest",)),
        ]
        request = PipelineRunRequest(
            run_id="run-105",
            model_name="income-lr",
            dataset_version="1.2.0",
            features=((1.0, 0.5, -0.2), (-0.4, 1.1, 0.3)),
        )
        result = custom.run(stages=stages, request=request)
        self.assertEqual(result.status, "PASSED")
        self.assertEqual(result.execution_order, ("ingest", "score"))
        self.assertAlmostEqual(
            sink.counters[("pipeline_stage_executions_total", (("stage", "score"), ("status", "SUCCEEDED")))],
            1.0,
        )

    def test_dry_run_skips_stages_cleanly(self) -> None:
        sink = InMemoryMetricsSink()
        orchestrator = PipelineOrchestrator.create_default(metrics_sink=sink)
        stages = [PipelineStageConfig(stage_id="validate", kind="validate")]
        req = PipelineRunRequest(
            run_id="dry-1",
            model_name="income-lr",
            dataset_version="1.0.0",
            features=((0.2, 0.8),),
            dry_run=True,
        )
        res = orchestrator.run(stages=stages, request=req)
        self.assertEqual(res.status, "SKIPPED")
        self.assertEqual(res.stage_results[0].status, "SKIPPED")

    def test_model_registry_lifecycle_and_checksum(self) -> None:
        registry = ModelArtifactRegistry()
        digest_v1 = compute_bytes_sha256(b"weights-v1")
        digest_v2 = compute_bytes_sha256(b"weights-v2")

        registry.register(
            ModelArtifactRecord(
                name="churn-net",
                version="1.0.0",
                sha256_digest=digest_v1,
                stage="development",
                metrics={"auc": 0.88},
            )
        )
        with self.assertRaises(ValueError):
            registry.promote("churn-net", "1.0.0", "production")

        registry.promote("churn-net", "1.0.0", "staging")
        registry.promote("churn-net", "1.0.0", "production")
        self.assertEqual(registry.get_production("churn-net").version, "1.0.0")

        registry.register(
            ModelArtifactRecord(
                name="churn-net",
                version="1.1.0",
                sha256_digest=digest_v2,
                stage="staging",
                metrics={"auc": 0.92},
            )
        )
        registry.promote("churn-net", "1.1.0", "production")
        self.assertEqual(registry.get_production("churn-net").version, "1.1.0")
        self.assertEqual(registry.latest_version("churn-net").version, "1.1.0")

    def test_latency_profiler_percentiles_and_synthetic_load(self) -> None:
        profiler = LatencyProfiler()
        for sample in [1.0, 2.0, 3.0, 4.0, 5.0]:
            profiler.record(sample)
        summary = profiler.summarize()
        self.assertEqual(summary.sample_count, 5)
        self.assertAlmostEqual(summary.p50_ms, 3.0)
        self.assertAlmostEqual(summary.min_ms, 1.0)
        self.assertAlmostEqual(summary.max_ms, 5.0)

        orchestrator = PipelineOrchestrator.create_default()
        stages = [
            PipelineStageConfig(stage_id="validate", kind="validate"),
            PipelineStageConfig(stage_id="score", kind="score", dependencies=("validate",)),
        ]
        batch = ((1.0, 0.2, -0.5), (-1.2, 0.9, 0.4), (0.3, -0.7, 1.1))
        profile = run_synthetic_load(
            lambda idx: orchestrator.run(
                stages=stages,
                request=PipelineRunRequest(
                    run_id=f"load-{idx}",
                    model_name="income-lr",
                    dataset_version="1.0.0",
                    features=batch,
                ),
            ),
            iterations=250,
            max_p95_ms=25.0,
        )
        self.assertEqual(profile.sample_count, 250)
        self.assertLess(profile.p95_ms, 25.0)
        self.assertGreater(profile.throughput_ops_sec, 100.0)


if __name__ == "__main__":
    unittest.main()
