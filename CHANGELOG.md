# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-12-22

### Added
- `tp1_git_intro/`: introductory Git version-control exercise.
- `tp2/`: pytest test suite (unit, integration, functional) for basic math operations and a small Flask app, managed with Poetry, with HTML/XML coverage reporting.
- `tp3/`: declarative Jenkins pipeline (`Jenkinsfile`) running the `tp2` test suite across parallel stages (unit / integration / functional) and publishing coverage reports.
- `tp4/test-sonarqube/`: a `Calculator` module with full pytest coverage, set up for static analysis via SonarQube (`pysonar`).
- `tp5/`: full-stack Flask + SQLAlchemy + Docker application — user CRUD, contact form, REST API, Docker Compose setup.
- `tp6/`: Kubernetes lab specification (minikube, kubectl, namespaces and pods).
- `tp7/tp-dvc-mlflow/`: DVC-orchestrated ML pipeline (download → preprocess → split → train → infer) with MLflow experiment tracking, trained on the UCI Adult Income dataset.
- Project-wide `README.md`, `LICENSE` (MIT), and this changelog.
- `.github/workflows/ci.yml`: GitHub Actions pipeline running the real `tp2` and `tp4` pytest suites plus a syntax/lint check on the remaining labs.
- `.gitignore` to keep local build artifacts (`__pycache__`, `.coverage`, `.sonar/`, `mlruns/`, etc.) out of version control.

### Changed
- Removed previously committed Python bytecode caches and coverage artifacts (`__pycache__/`, `*.pyc`, `.coverage`) from version control.
