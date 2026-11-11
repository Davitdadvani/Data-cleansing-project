"""
Step 1: Create a SIMULATED survey dataset (no real people involved).

It mimics a Prolific-style online survey about digital competence at work,
including typical data-quality problems (speeders, straightliners, etc.)
so we can practice finding and removing them.
"""
import os
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)   # fixed seed -> same data every run
N = 520                            # number of simulated respondents


def likert(latent, noise=0.8):
    """Turn a hidden score into a 1-5 Likert answer (rounded + clipped)."""
    return np.clip(np.round(latent + rng.normal(0, noise, len(latent))), 1, 5).astype(int)


# Hidden "true" levels per person. Digital competence drives helper demand,
# and helper demand drives strain -> gives us real relationships to find.
competence = rng.normal(3.4, 0.8, N)
demand = 0.5 * competence + rng.normal(1.5, 0.7, N)
strain = 0.5 * demand + rng.normal(1.0, 0.7, N)

df = pd.DataFrame({"respondent_id": [f"P{i:04d}" for i in range(N)]})
for i in range(1, 7):
    df[f"comp_{i}"] = likert(competence)    # digital competence scale (6 items)
for i in range(1, 6):
    df[f"help_{i}"] = likert(demand)        # "colleagues ask me for help" (5 items)
for i in range(1, 6):
    df[f"strain_{i}"] = likert(strain)      # job strain (5 items)

df["attention_check"] = rng.choice([4]*23 + [2, 3], N)  # instructed answer = 4
df["age"] = rng.integers(20, 63, N)
df["completion_seconds"] = rng.normal(420, 90, N).clip(150).round()

# ---- Inject data-quality problems on purpose ----
scale_cols = [c for c in df.columns if c.startswith(("comp_", "help_", "strain_"))]

speeders = rng.choice(N, 25, replace=False)
df.loc[speeders, "completion_seconds"] = rng.integers(40, 110, 25)

straight = rng.choice(N, 20, replace=False)
for idx in straight:
    df.loc[idx, scale_cols] = rng.integers(1, 6)        # same answer everywhere

missing_rows = rng.choice(N, 30, replace=False)
for idx in missing_rows:
    cols = rng.choice(scale_cols, 6, replace=False)
    df.loc[idx, cols] = np.nan

dupes = df.sample(8, random_state=1)                      # duplicate submissions
df = pd.concat([df, dupes], ignore_index=True)

os.makedirs("data", exist_ok=True)
df.to_csv("data/raw_survey.csv", index=False)
print(f"Saved data/raw_survey.csv with {len(df)} rows")
