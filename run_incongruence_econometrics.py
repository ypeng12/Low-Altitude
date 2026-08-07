import pandas as pd
import numpy as np
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.miscmodels.ordinal_model import OrderedModel
import sys

sys.stdout.reconfigure(encoding='utf-8')

dataset_path = 'data/derived_outputs/deep_research_quintuple_extracted.csv'
print(f"Loading Quintuple Extracted Dataset from {dataset_path}...")
df = pd.read_csv(dataset_path)
print(f"Total Dataset Rows: {len(df)}")

# Filter pure English reviews for econometric precision
df_en = df[df['is_english'] == 1].copy()
print(f"Pure English Regressor Subset Rows: {len(df_en)}")

# Standardize continuous control variables
df_en['word_count_std'] = (df_en['review_word_count'] - df_en['review_word_count'].mean()) / df_en['review_word_count'].std()

# 1. Model 1: Baseline Aspect Utility OLS Regression
f1 = 'rating ~ aspect_Scenery + aspect_Pilot + aspect_GroundStaff + aspect_CabinComfort + aspect_Safety + aspect_Weather + aspect_PriceValue + aspect_ServiceRecovery + aspect_Companion + aspect_LifetimeExperience + word_count_std + is_us_domestic'
m1 = smf.ols(f1, data=df_en).fit(cov_type='HC3')

print("\n=======================================================")
print("Model 1: Baseline Aspect Utility OLS Regression (Robust HC3 SE)")
print("=======================================================")
print(m1.summary().tables[1])
print(f"R-squared: {m1.rsquared:.4f} | Adj R-squared: {m1.rsquared_adj:.4f} | F-stat: {m1.fvalue:.2f}")

# 2. Model 2: Dual-Factor Interaction Mechanism Regression
f2 = 'rating ~ aspect_Scenery * aspect_Pilot + aspect_Weather * aspect_ServiceRecovery + aspect_Safety * aspect_Pilot + aspect_PriceValue * aspect_LifetimeExperience + aspect_GroundStaff + aspect_CabinComfort + word_count_std + is_us_domestic'
m2 = smf.ols(f2, data=df_en).fit(cov_type='HC3')

print("\n=======================================================")
print("Model 2: Dual-Factor Interaction Mechanism OLS Regression")
print("=======================================================")
print(m2.summary().tables[1])
print(f"R-squared: {m2.rsquared:.4f} | Adj R-squared: {m2.rsquared_adj:.4f} | F-stat: {m2.fvalue:.2f}")

# 3. Model 3: Ordered Probit Regression (Handling Ceiling Distribution)
print("\n=======================================================")
print("Model 3: Ordered Probit Regression for Ordinal Star Ratings")
print("=======================================================")
try:
    m3 = OrderedModel(
        df_en['rating'],
        df_en[['aspect_Scenery', 'aspect_Pilot', 'aspect_GroundStaff', 'aspect_CabinComfort', 'aspect_Safety', 'aspect_Weather', 'aspect_PriceValue', 'aspect_ServiceRecovery', 'word_count_std', 'is_us_domestic']],
        distr='probit'
    ).fit(method='bfgs', maxiter=100, disp=False)
    print(m3.summary().tables[1])
except Exception as e:
    print(f"Ordered Probit Model Note: {e}")

# Save Paper Summary Tables
table1_df = pd.DataFrame({
    'Variable': m1.params.index,
    'Coef_Baseline': m1.params.values.round(4),
    'StdErr_Baseline': m1.bse.values.round(4),
    'PValue_Baseline': m1.pvalues.values.round(4),
    'Coef_Interaction': m2.params.reindex(m1.params.index).values.round(4),
    'PValue_Interaction': m2.pvalues.reindex(m1.params.index).values.round(4)
})

out_table_path = 'data/derived_outputs/deep_research_econometric_regressions.csv'
table1_df.to_csv(out_table_path, index=False, encoding='utf-8-sig')
print(f"\nSaved Deep Research Econometric Regressions Summary -> {out_table_path}")
