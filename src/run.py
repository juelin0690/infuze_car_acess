from __future__ import annotations

from pathlib import Path
from .model import CarAccessModel

def main():
    project_root = Path(__file__).resolve().parents[1]
    out_dir = project_root / "outputs"
    out_dir.mkdir(exist_ok=True)

    m = CarAccessModel(seed=42, num_agents=500, shared_cars=25, steps=80)
    df = m.run_model()

    out_csv = out_dir / "model_runs.csv"
    df.to_csv(out_csv, index=False)

    print(df.tail())
    print(f"Saved: {out_csv}")

if __name__ == "__main__":
    main()
print("hehello")