# DevOpsML

![CI Pipeline](https://github.com/Bosaj/DevOpsML/actions/workflows/ci_qa_monitoring.yml/badge.svg)
[![GitHub Wiki](https://img.shields.io/badge/Documentation-GitHub%20Wiki-blue.svg)](https://github.com/Bosaj/DevOpsML/wiki)
[![Quality Gate](https://img.shields.io/badge/Quality%20Gate-Passed-brightgreen.svg)](docs/MONITORING_AND_QA.md)

---

![CI](https://github.com/Bosaj/DevOpsML/actions/workflows/ci.yml/badge.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Python](https://img.shields.io/badge/python-3.12-blue.svg)

A hands-on progression through the core DevOps and MLOps toolchain — version control, automated testing, CI pipelines, static code quality, containerization, and reproducible ML pipelines.

## Overview

This repository is a series of labs (*travaux pratiques*) that build up, one tool at a time, the DevOps practices a software/ML engineer uses day to day: starting from a first `git` commit, through automated test suites and CI orchestration, to a fully tracked and reproducible machine learning training pipeline.

## Contents

| Lab | Topic | Highlights |
|---|---|---|
| [`tp1_git_intro/`](tp1_git_intro) | Git fundamentals | Introductory version-control exercise |
| [`tp2/`](tp2) | Automated testing with pytest | Unit, integration & functional (Flask) test suites, Poetry, coverage reporting |
| [`tp3/`](tp3) | CI with Jenkins | Declarative `Jenkinsfile` running tp2's full test suite in parallel stages, publishing HTML coverage |
| [`tp4/test-sonarqube/`](tp4/test-sonarqube) | Static analysis & code quality | A `Calculator` module fully covered by pytest, scanned with SonarQube |
| [`tp5/`](tp5) | Containerized web app | Flask + SQLAlchemy + Docker CRUD application (user management, contact form, REST endpoints) |
| [`tp6/`](tp6) | Kubernetes | Lab specification (minikube, kubectl, namespaces & pods) — reference material; not yet implemented in this repo |
| [`tp7/tp-dvc-mlflow/`](tp7/tp-dvc-mlflow) | Reproducible ML pipelines | DVC-orchestrated pipeline (download → preprocess → split → train → infer) with MLflow experiment tracking, on the UCI Adult Income dataset |

## Tech Stack

Python 3.12 · Poetry · pytest / pytest-cov · Flask · SQLAlchemy · Docker & Docker Compose · Jenkins (declarative pipelines) · SonarQube · DVC · MLflow · scikit-learn · pandas

## Getting Started

Each lab is self-contained — `cd` into the one you want:

```bash
# tp2 - pytest suite (unit / integration / functional)
cd tp2 && poetry install && poetry run pytest -v --cov=src

# tp4 - SonarQube-scanned calculator
cd tp4/test-sonarqube && poetry install && poetry run pytest -v --cov=src

# tp5 - Flask + Docker web app
cd tp5 && pip install -r requirements.txt && python app.py
# or: docker-compose up --build

# tp7 - DVC + MLflow pipeline
cd tp7/tp-dvc-mlflow && pip install pandas scikit-learn mlflow joblib pyyaml && dvc repro
```

## Testing / CI

[`.github/workflows/ci.yml`](.github/workflows/ci.yml) runs on every push to `main`:
- The real `tp2` pytest suite (unit, integration, functional)
- The real `tp4` pytest suite for the SonarQube-scanned `Calculator`
- A Python syntax/import sanity check across the remaining labs (`tp1`, `tp5`, `tp7`)

`tp3/Jenkinsfile` documents the equivalent pipeline for a self-hosted Jenkins runner (parallel test stages + coverage publishing), and `tp4` is designed to also be scanned by a SonarQube server (`pysonar` dependency, `.sonar/` report output).

## Project Structure

```
DevOpsML/
├── tp1_git_intro/        # Git basics
├── tp2/                  # pytest: unit + integration + functional tests
├── tp3/                  # Jenkinsfile (declarative CI pipeline)
├── tp4/test-sonarqube/   # Calculator module + SonarQube static analysis
├── tp5/                  # Flask + SQLAlchemy + Docker CRUD app
├── tp6/                  # Kubernetes lab spec (reference only)
└── tp7/tp-dvc-mlflow/    # DVC pipeline + MLflow tracking (Adult Income dataset)
```

## Changelog

See [CHANGELOG.md](CHANGELOG.md).

## License

This project is licensed under the MIT License — see [LICENSE](LICENSE).

## Author

Oussama EL HADJI — [github.com/Bosaj](https://github.com/Bosaj)


## 📊 Monitoring, Controlling, Evaluation & QA

This project includes a standardized 4-Pillar Observability and QA framework:
- **Logs & Prometheus/Grafana Monitoring**: Configured in `monitoring/` with Prometheus scraper configs and Grafana dashboards.
- **Health Controlling & Evaluation**: Liveness/readiness controllers in `monitoring/health.py` and evaluation harness in `scripts/eval_harness.py`.
- **QA & Testing**: Automated Pytest/Vitest integration and CI workflows via `.github/workflows/ci_qa_monitoring.yml`.

For complete instructions, architecture details, and commands, see [docs/MONITORING_AND_QA.md](docs/MONITORING_AND_QA.md).

---

## 📚 Documentation & GitHub Wiki
- 📖 **Official Project Wiki**: [https://github.com/Bosaj/DevOpsML/wiki](https://github.com/Bosaj/DevOpsML/wiki)
- 🔍 **Architecture & Design**: [https://github.com/Bosaj/DevOpsML/wiki/Architecture-and-Design](https://github.com/Bosaj/DevOpsML/wiki/Architecture-and-Design)
- 🚀 **Getting Started Guide**: [https://github.com/Bosaj/DevOpsML/wiki/Getting-Started](https://github.com/Bosaj/DevOpsML/wiki/Getting-Started)
- 📊 **Monitoring & Observability**: [docs/MONITORING_AND_QA.md](docs/MONITORING_AND_QA.md)
