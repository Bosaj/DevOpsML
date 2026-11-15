"""SemVer-aware, checksum-verified ModelArtifactRegistry for DevOpsML."""

from __future__ import annotations

import hashlib
import re
import threading

from src.devops_ml.contracts import ModelArtifactRecord

_SEMVER_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")


def parse_semver(version: str) -> tuple[int, int, int]:
    """Parse strict MAJOR.MINOR.PATCH version tuples."""
    match = _SEMVER_RE.match(version.strip())
    if not match:
        raise ValueError(f"Invalid semantic version '{version}'; expected MAJOR.MINOR.PATCH.")
    return (int(match.group(1)), int(match.group(2)), int(match.group(3)))


def compute_bytes_sha256(payload: bytes) -> str:
    """Compute canonical SHA-256 hex digest for model weight blobs."""
    return hashlib.sha256(payload).hexdigest()


class ModelArtifactRegistry:
    """Thread-safe model registry enforcing monotonic versions and stage promotions."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._records: dict[str, dict[str, ModelArtifactRecord]] = {}

    def register(self, record: ModelArtifactRecord) -> ModelArtifactRecord:
        parse_semver(record.version)
        with self._lock:
            versions = self._records.setdefault(record.name, {})
            if record.version in versions:
                raise ValueError(f"Artifact '{record.name}:{record.version}' is already registered.")
            versions[record.version] = record
        return record

    def promote(self, name: str, version: str, target_stage: str) -> ModelArtifactRecord:
        if target_stage not in {"staging", "production", "archived"}:
            raise ValueError(f"Cannot promote to unsupported target stage '{target_stage}'.")
        with self._lock:
            versions = self._records.get(name, {})
            if version not in versions:
                raise KeyError(f"Artifact '{name}:{version}' not found.")
            current = versions[version]
            if target_stage == "production" and current.stage == "development":
                raise ValueError("Models must pass 'staging' validation before promotion to 'production'.")
            if target_stage == "production":
                for existing_ver, existing_rec in list(versions.items()):
                    if existing_rec.stage == "production" and existing_ver != version:
                        versions[existing_ver] = ModelArtifactRecord(
                            name=existing_rec.name,
                            version=existing_rec.version,
                            sha256_digest=existing_rec.sha256_digest,
                            stage="archived",
                            metrics=dict(existing_rec.metrics),
                        )
            updated = ModelArtifactRecord(
                name=current.name,
                version=current.version,
                sha256_digest=current.sha256_digest,
                stage=target_stage,
                metrics=dict(current.metrics),
            )
            versions[version] = updated
            return updated

    def get_production(self, name: str) -> ModelArtifactRecord | None:
        with self._lock:
            for record in self._records.get(name, {}).values():
                if record.stage == "production":
                    return record
        return None

    def latest_version(self, name: str) -> ModelArtifactRecord | None:
        with self._lock:
            versions = list(self._records.get(name, {}).values())
        if not versions:
            return None
        return max(versions, key=lambda rec: parse_semver(rec.version))
