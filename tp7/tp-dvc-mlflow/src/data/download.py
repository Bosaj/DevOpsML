import yaml
import pandas as pd
from pathlib import Path

def load_params(path: str = "params.yaml") -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def main() -> None:
    params = load_params()

    url = params["dataset"]["url"]
    columns = [
        "age", "workclass", "fnlwgt", "education", "education_num",
        "marital_status", "occupation", "relationship", "race", "sex",
        "capital_gain", "capital_loss", "hours_per_week",
        "native_country", "income",
    ]

    df = pd.read_csv(url, header=None, names=columns)

    raw_dir = Path("data/raw")
    raw_dir.mkdir(parents=True, exist_ok=True)
    out_path = raw_dir / params["dataset"]["raw_filename"]

    df.to_csv(out_path, index=False)
    print("[download] saved raw dataset to", out_path)

if __name__ == "__main__":
    main()
