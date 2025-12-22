from __future__ import annotations
from pathlib import Path

import yaml
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

def load_params(path: str = "params.yaml") -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def main() -> None:
    params = load_params()

    raw_path = Path("data/raw") / params["dataset"]["raw_filename"]
    out_dir = Path("data/processed")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "adult_clean.csv"

    df = pd.read_csv(raw_path)

    # Remplacer ? par NaN
    df.replace(" ?", np.nan, inplace=True)

    # Drop duplicates si demandé
    if params["preprocess"]["drop_duplicates"]:
        df = df.drop_duplicates()

    # Drop lignes avec NaN si demandé
    if params["preprocess"]["drop_missing"]:
        df = df.dropna()

    # Normalisation des colonnes numériques
    num_cols = df.select_dtypes(include="number").columns
    scaler = StandardScaler()
    df[num_cols] = scaler.fit_transform(df[num_cols])

    # Nettoyer les noms de colonnes
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    df.to_csv(out_path, index=False)
    print("[preprocess] saved cleaned dataset to", out_path)

if __name__ == "__main__":
    main()
