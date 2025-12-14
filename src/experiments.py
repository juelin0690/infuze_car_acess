from __future__ import annotations

import os
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

from .model import CarAccessModel


def run_one(seed: int, **kwargs) -> pd.DataFrame:
    m = CarAccessModel(seed=seed, **kwargs)
    df = m.run_model()
    df["seed"] = seed
    return df


def run_grid(output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    print(">>> Entered run_grid(). CWD =", os.getcwd())
    print(">>> Output dir =", os.path.abspath(output_dir))

    scenarios = []
    for shared_cars in [10, 25, 50]:
        for friction in [0.2, 0.4, 0.6]:
            scenarios.append({"shared_cars": shared_cars, "booking_friction": friction})

    all_rows = []
    for i, sc in enumerate(scenarios):
        for seed in [1, 2, 3, 4, 5]:
            df = run_one(
                seed=seed,
                num_agents=500,
                steps=80,
                access_price=0.6,
                booking_fail_prob=0.10,
                prob_drop_ownership=0.55,
                **sc,
            )
            df["scenario_id"] = i
            df["shared_cars"] = sc["shared_cars"]
            df["friction"] = sc["booking_friction"]
            all_rows.append(df)

    out = pd.concat(all_rows, ignore_index=True)
    out_path = os.path.join(output_dir, "model_runs.csv")
    out.to_csv(out_path, index=False)

    last = out.groupby(["scenario_id", "shared_cars", "friction", "seed"], as_index=False).tail(1)
    summary = last.groupby(["shared_cars", "friction"], as_index=False)["adoption_rate"].mean()

    plt.figure()
    for shared_cars in sorted(summary["shared_cars"].unique()):
        sub = summary[summary["shared_cars"] == shared_cars].sort_values("friction")
        plt.plot(sub["friction"], sub["adoption_rate"], marker="o", label=f"cars={shared_cars}")
    plt.xlabel("booking friction (higher=worse)")
    plt.ylabel("mean final adoption rate")
    plt.legend()
    plt.tight_layout()

    fig_path = os.path.join(output_dir, "final_adoption_vs_friction.png")
    plt.savefig(fig_path, dpi=200)
    plt.close()

    print(f"Saved: {out_path}")
    print(f"Saved: {fig_path}")


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[1]
    run_grid(str(project_root / "outputs"))
