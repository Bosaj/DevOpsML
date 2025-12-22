from __future__ import annotations
from pathlib import Path

import yaml
import pandas as pd
from sklearn.model_selection import train_test_split

def load_params(path: str = "params.yaml") -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def dist(series: pd.Series) -> dict:
    vc = series.value_counts(normalize=True)
    return {str(k): float(v) for k, v in vc.items()}

def main() -> None:
    params = load_params()

    seed = int(params["seed"])
    split_cfg = params["split"]
    train_ratio = float(split_cfg["train_ratio"])
    val_ratio = float(split_cfg["val_ratio"])
    test_ratio = float(split_cfg["test_ratio"])
    stratify = bool(split_cfg.get("stratify", True))

    total = train_ratio + val_ratio + test_ratio
    if abs(total - 1.0) > 1e-9:
        raise ValueError(f"Split ratios must sum to 1.0, got {total}")

    in_path = Path("data/processed") / "adult_clean.csv"
    df = pd.read_csv(in_path)

    if "income" not in df.columns:
        raise ValueError("Target column 'income' not found. Check preprocessing output.")

    X = df.drop(columns=["income"])
    y = df["income"]

    X_train, X_temp, y_train, y_temp = train_test_split(
        X,
        y,
        test_size=1.0 - train_ratio,
        random_state=seed,
        stratify=y if stratify else None,
    )

    val_ratio_adjusted = val_ratio / (val_ratio + test_ratio)
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp,
        y_temp,
        test_size=1.0 - val_ratio_adjusted,
        random_state=seed,
        stratify=y_temp if stratify else None,
    )

    out_dir = Path("data/splits")
    out_dir.mkdir(parents=True, exist_ok=True)

    train_df = X_train.copy()
    train_df["income"] = y_train.values
    val_df = X_val.copy()
    val_df["income"] = y_val.values
    test_df = X_test.copy()
    test_df["income"] = y_test.values

    train_path = out_dir / "train.csv"
    val_path = out_dir / "val.csv"
    test_path = out_dir / "test.csv"

    train_df.to_csv(train_path, index=False)
    val_df.to_csv(val_path, index=False)
    test_df.to_csv(test_path, index=False)

    print(f"[split] Input: {in_path} shape={df.shape}")
    print(f"[split] seed={seed} stratify={stratify}")
    print(f"[split] train={len(train_df)} val={len(val_df)} test={len(test_df)}")
    print(f"[split] train class dist: {dist(train_df['income'])}")
    print(f"[split] val   class dist: {dist(val_df['income'])}")
    print(f"[split] test  class dist: {dist(test_df['income'])}")
    print(f"[split] Saved: {train_path}, {val_path}, {test_path}")

if __name__ == "__main__":
    main()
