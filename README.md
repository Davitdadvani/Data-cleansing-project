# Survey Data Cleaning & Analysis (Simulated Prolific-Style Study)

A small practice project on the workflow of an online survey study: **data-quality checks, cleaning, scale reliability, and basic statistical analysis** in Python.

> **Note:** All data is **simulated** (`generate_data.py`). No real participants are involved. The topic (digital competence and "helper demand" at work) is only used to make the practice dataset realistic.

> **AI assistance:** This project was built with AI assistance (Claude) as a learning project. I am working through the code to understand each step.

## Research question (practice)
Are employees with higher digital competence asked for help more often, and is higher helper demand associated with more job strain?

## What the project does
1. **Simulates** ~520 respondents with a 6-item competence scale, a 5-item helper-demand scale, a 5-item strain scale (all 1-5 Likert), an attention check, age and completion time, plus deliberately injected problems: speeders, straightliners, missing data and duplicates.
2. **Cleans** the data in a documented order:
   - duplicate submissions
   - failed attention check
   - speeders (< 40% of median completion time)
   - straightliners (no variation across scale items)
   - >20% missing scale items; small remaining gaps filled with the respondent's scale mean
3. **Analyses**: descriptive statistics, Cronbach's alpha, correlations, Welch t-test (high vs low competence), simple linear regression.
4. **Outputs** (created when you run the scripts): `data/clean_survey.csv`, `results.md` (cleaning log + results), `figures/demand_vs_strain.png`.

## How to run
```bash
pip install -r requirements.txt
python generate_data.py
python analyze.py
```

## Project structure
```
generate_data.py   # creates simulated raw data
analyze.py         # cleaning + analysis + chart
data/              # raw and cleaned CSV files (generated)
figures/           # charts (generated)
results.md         # results and cleaning log (generated)
```

## Limitations / possible next steps
- Simulated data: results only show that the pipeline works, not real-world effects.
- Missing-data handling is simple (person-mean imputation); a real study might use other methods.
- Next: repeat the pipeline on a real open survey dataset, add a multiple regression with controls, build a Power BI dashboard.

## Tools
Python, pandas, NumPy, SciPy, Matplotlib
