from __future__ import annotations

from pathlib import Path
import json

import yaml
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

import joblib
import mlflow
import mlflow.sklearn

def load_params(path: str = "params.yaml") -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def main() -> None:
    params = load_params()
    seed = int(params["seed"])

    train_path = Path("data/splits/train.csv")
    test_path = Path("data/splits/test.csv")

    df_train = pd.read_csv(train_path)
    df_test = pd.read_csv(test_path)

    target = "income"
    X_train, y_train = df_train.drop(columns=[target]), df_train[target]
    X_test, y_test = df_test.drop(columns=[target]), df_test[target]

    cat_cols = X_train.select_dtypes(include=["object"]).columns.tolist()
    num_cols = [c for c in X_train.columns if c not in cat_cols]

    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), cat_cols),
            ("num", "passthrough", num_cols),
        ]
    )

    clf = Pipeline(
        steps=[
            ("prep", preprocessor),
            ("model", LogisticRegression(max_iter=1000, random_state=seed)),
        ]
    )

    mlflow.set_tracking_uri("file:./mlruns")
    mlflow.set_experiment("adult-income-dvc-mlflow")

    Path("models").mkdir(parents=True, exist_ok=True)
    Path("reports").mkdir(parents=True, exist_ok=True)

    with mlflow.start_run():
        mlflow.log_param("seed", seed)

        clf.fit(X_train, y_train)
        preds = clf.predict(X_test)
        acc = accuracy_score(y_test, preds)

        mlflow.log_metric("test_accuracy", float(acc))

        model_path = Path("models/model.joblib")
        joblib.dump(clf, model_path)
        mlflow.sklearn.log_model(clf, "model")

        metrics_path = Path("reports/metrics.json")
        with open(metrics_path, "w", encoding="utf-8") as f:
            json.dump({"test_accuracy": float(acc)}, f, indent=2)
        mlflow.log_artifact(str(metrics_path))

        print("[train] test_accuracy =", float(acc))
        print("[train] saved model:", model_path)
        print("[train] saved metrics:", metrics_path)

if __name__ == "__main__":
    main()
