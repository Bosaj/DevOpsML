"""Monitoring, telemetry, health probe, and evaluation harness QA suite."""

from __future__ import annotations

import json
import logging
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from monitoring.health import check_liveness, check_readiness, get_health_status
from monitoring.logger import JsonFormatter, setup_logger
from monitoring.metrics import record_request, set_health_status, update_eval_metric
from scripts.eval_harness import run_evaluation


class TestMonitoringAndQA(unittest.TestCase):
    def test_liveness_and_readiness(self) -> None:
        self.assertIs(check_liveness(), True)
        self.assertIs(check_readiness(), True)

    def test_health_status(self) -> None:
        status = get_health_status()
        self.assertEqual(status["status"], "UP")
        self.assertEqual(status["service"], "DevOpsML")
        self.assertTrue(status["checks"]["liveness"])
        self.assertTrue(status["checks"]["readiness"])

    def test_eval_harness(self) -> None:
        results = run_evaluation(iterations=10)
        self.assertEqual(results["status"], "PASSED")
        self.assertIn("quality_index", results["metrics"])
        self.assertIn("p95_latency_ms", results["metrics"])
        self.assertGreater(results["metrics"]["quality_index"], 0.7)

    def test_structured_json_logger_and_metrics(self) -> None:
        record = logging.LogRecord(
            name="devopsml.test",
            level=logging.INFO,
            pathname=__file__,
            lineno=1,
            msg="synthetic probe",
            args=(),
            exc_info=None,
        )
        formatted = json.loads(JsonFormatter().format(record))
        self.assertEqual(formatted["level"], "INFO")
        self.assertEqual(formatted["message"], "synthetic probe")

        logger = setup_logger("devopsml.qa.probe")
        self.assertGreaterEqual(len(logger.handlers), 1)
        record_request("GET", "/health", "200", 0.002)
        update_eval_metric("qa_probe", 0.99)
        set_health_status(True)


if __name__ == "__main__":
    unittest.main()
