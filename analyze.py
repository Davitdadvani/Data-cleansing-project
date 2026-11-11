"""
Step 2: Clean the raw survey data and run basic analyses.
Run:  python analyze.py
"""
import os
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

df = pd.read_csv("data/raw_survey.csv")
log = []   # we document every cleaning decision (documentation matters!)


def record(step, before, after):
    log.append(f"{step}: removed {before - after} rows ({before} -> {after})")


comp = [c for c in df.columns if c.startswith("comp_")]
help_ = [c for c in df.columns if c.startswith("help_")]
strain = [c for c in df.columns if c.startswith("strain_")]
scale_cols = comp + help_ + strain

# ---------------- DATA CLEANING ----------------
n = len(df)
df = df.drop_duplicates(subset=[c for c in df.columns if c != "respondent_id"])
record("Duplicate submissions", n, len(df)); n = len(df)

df = df[df["attention_check"] == 4]                 # failed the instructed-response item
record("Failed attention check", n, len(df)); n = len(df)

# Speeders: faster than 40% of the median completion time (a common rule of thumb)
cutoff = df["completion_seconds"].median() * 0.4
df = df[df["completion_seconds"] >= cutoff]
record(f"Speeders (< {cutoff:.0f}s)", n, len(df)); n = len(df)

# Straightliners: zero variation across all scale items
df = df[df[scale_cols].std(axis=1) > 0]
record("Straightliners", n, len(df)); n = len(df)

# Too much missing data: more than 20% of scale items empty
df = df[df[scale_cols].isna().mean(axis=1) <= 0.20]
record("Too many missing answers", n, len(df)); n = len(df)

# Remaining small gaps: fill with the respondent's own scale mean (simple approach)
for cols in (comp, help_, strain):
    df[cols] = df[cols].apply(lambda r: r.fillna(r.mean()), axis=1)

# Build scale scores (average of items)
df["competence"] = df[comp].mean(axis=1)
df["helper_demand"] = df[help_].mean(axis=1)
df["strain"] = df[strain].mean(axis=1)
df.to_csv("data/clean_survey.csv", index=False)


# ---------------- ANALYSIS ----------------
def cronbach_alpha(items):
    """Reliability of a scale: closer to 1 = items measure the same thing."""
    k = items.shape[1]
    return k / (k - 1) * (1 - items.var(ddof=1).sum() / items.sum(axis=1).var(ddof=1))


results = ["# Results\n", "## Cleaning log"] + [f"- {l}" for l in log]
results.append(f"\nFinal sample: {len(df)} respondents\n")

results.append("## Descriptive statistics")
results.append(df[["age", "competence", "helper_demand", "strain"]].describe().round(2).to_markdown())

results.append("\n## Scale reliability (Cronbach's alpha)")
for name, cols in [("Competence", comp), ("Helper demand", help_), ("Strain", strain)]:
    results.append(f"- {name}: {cronbach_alpha(df[cols]):.2f}")

results.append("\n## Correlations")
results.append(df[["competence", "helper_demand", "strain"]].corr().round(2).to_markdown())

# Do highly competent people get asked for help more? (t-test, median split)
high = df[df["competence"] >= df["competence"].median()]["helper_demand"]
low = df[df["competence"] < df["competence"].median()]["helper_demand"]
t, p = stats.ttest_ind(high, low, equal_var=False)
results.append(f"\n## t-test: helper demand, high vs low competence\n"
               f"High mean = {high.mean():.2f}, low mean = {low.mean():.2f}, t = {t:.2f}, p = {p:.4g}")

# Does helper demand predict strain? (simple linear regression)
reg = stats.linregress(df["helper_demand"], df["strain"])
results.append(f"\n## Regression: strain ~ helper demand\n"
               f"slope = {reg.slope:.2f}, R² = {reg.rvalue**2:.2f}, p = {reg.pvalue:.4g}")

with open("results.md", "w", encoding="utf-8") as f:
    f.write("\n".join(results))

# Chart
os.makedirs("figures", exist_ok=True)
plt.figure(figsize=(6, 4))
plt.scatter(df["helper_demand"], df["strain"], alpha=0.4)
x = np.array([df["helper_demand"].min(), df["helper_demand"].max()])
plt.plot(x, reg.intercept + reg.slope * x, color="red")
plt.xlabel("Helper demand (1-5)")
plt.ylabel("Job strain (1-5)")
plt.title("Helper demand vs. job strain (simulated data)")
plt.tight_layout()
plt.savefig("figures/demand_vs_strain.png", dpi=150)
print("\n".join(results))
