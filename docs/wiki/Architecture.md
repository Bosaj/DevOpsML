# Architecture

DevOpsML is not a single application — it's seven independent labs, each isolating one layer of the DevOps/MLOps stack.

| Lab | Topic | What's actually inside |
|---|---|---|
| `tp1_git_intro/` | Git fundamentals | An introductory version-control exercise. |
| `tp2/` | Automated testing | Four exercise modules (`Ex1`–`Ex4`: arithmetic, list de-duplication, file I/O, CSV filtering) plus a small Flask app, each covered by unit, integration, and functional pytest suites, managed with Poetry and measured with `pytest-cov`. |
| `tp3/` | CI with Jenkins | A declarative `Jenkinsfile` that runs `tp2`'s full test suite across parallel stages (unit / integration / functional) and publishes HTML coverage — designed for a self-hosted Jenkins runner. |
| `tp4/test-sonarqube/` | Static analysis | A four-method `Calculator` class (add, subtract, multiply, divide-with-zero-check), fully covered by pytest, wired up for a SonarQube static-analysis scan (`pysonar`, `.sonar/` report output). |
| `tp5/` | Containerized web app | A Flask + SQLAlchemy CRUD application: `User` and `Contact` models, a home/about/contact/users page set, and Docker + Docker Compose packaging. |
| `tp6/` | Kubernetes | A written lab specification (minikube, kubectl, namespaces, pods) — reference material, not an implemented deployment. |
| `tp7/tp-dvc-mlflow/` | Reproducible ML pipeline | A DVC-orchestrated pipeline on the UCI Adult Income dataset. |

## The tp7 pipeline in detail

`tp7` is the most complete lab: it wires DVC stages together with MLflow experiment tracking.

- **DVC stages** (`dvc.yaml`): `download` (fetches `adult.csv` from the UCI repository) → `preprocess` (drops missing values and duplicates, normalizes numeric columns, one-hot encodes categoricals) → `split` (stratified 70/15/15 train/val/test split, seeded via `params.yaml`).
- **Training and inference**: `src/train/train.py` and `src/infer/predict.py` sit alongside the DVC-tracked stages and are logged through MLflow (`mlruns/`), including the trained model artifact, its `conda.yaml`/`requirements.txt` environment spec, and run parameters (e.g. `seed: 42`).
- **Tracked result**: the logged MLflow run for this pipeline recorded a test-set accuracy of **~0.85 (85%)**.
- **Parameters** (`params.yaml`): dataset URL, preprocessing flags, and the 70/15/15 stratified split ratios are all centralized here rather than hardcoded, so `dvc repro` reproduces the same pipeline deterministically.

## Toolchain summary

Python 3.12 · Poetry · pytest / pytest-cov · Flask · SQLAlchemy · Docker & Docker Compose · Jenkins (declarative pipelines) · SonarQube · DVC · MLflow · scikit-learn · pandas
