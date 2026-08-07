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

# 1. Model 1: ABSA Aspect Sentiment Polarity Utility OLS Regression
f1 = 'rating ~ pilot_pos + pilot_neg + weather_pos + weather_neg + ground_staff_pos + ground_staff_neg + price_value_pos + price_value_neg + scenery_pos + scenery_neg + safety_assurance + fear_anxiety + word_count_std + is_us_domestic'
m1 = smf.ols(f1, data=df_en).fit(cov_type='HC3')

print("\n=======================================================")
print("Model 1: ABSA Aspect Sentiment Polarity OLS Regression (HC3 Robust SE)")
print("=======================================================")
print(m1.summary().tables[1])
print(f"R-squared: {m1.rsquared:.4f} | Adj R-squared: {m1.rsquared_adj:.4f} | F-stat: {m1.fvalue:.2f}")

# 2. Model 2: Attribution Theory & Discourse Clause Dynamics Regression
# Testing Weather_Neg * Pilot_Pos (Service mitigation of uncontrollable bad weather)
# Testing Fear_Trans (Scared -> Safety Assurance transformation effect)
# Testing Sentiment_Post_But (Post-adversative clause dominance)
f2 = 'rating ~ weather_neg * pilot_pos + fear_trans + fear_anxiety + safety_assurance + sentiment_post_but + discourse_shift_pos2neg + discourse_shift_neg2pos + pilot_pos + ground_staff_pos + ground_staff_neg + price_value_neg + word_count_std + is_us_domestic'
m2 = smf.ols(f2, data=df_en).fit(cov_type='HC3')

print("\n=======================================================")
print("Model 2: Attribution Mitigation & Discourse Clause Dynamics OLS")
print("=======================================================")
print(m2.summary().tables[1])
print(f"R-squared: {m2.rsquared:.4f} | Adj R-squared: {m2.rsquared_adj:.4f} | F-stat: {m2.fvalue:.2f}")

# 3. Model 3: Ordered Probit Regression with ABSA & Attribution Features
print("\n=======================================================")
print("Model 3: Ordered Probit Regression for Ordinal Star Ratings")
print("=======================================================")
try:
    probit_vars = ['pilot_pos', 'pilot_neg', 'weather_pos', 'weather_neg', 'ground_staff_pos', 'ground_staff_neg', 'safety_assurance', 'fear_anxiety', 'sentiment_post_but', 'word_count_std', 'is_us_domestic']
    m3 = OrderedModel(
        df_en['rating'],
        df_en[probit_vars],
        distr='probit'
    ).fit(method='bfgs', maxiter=100, disp=False)
    print(m3.summary().tables[1])
except Exception as e:
    print(f"Ordered Probit Model Note: {e}")

# Save Paper Summary Tables
table1_df = pd.DataFrame({
    'Variable': m1.params.index,
    'Coef_ABSA_Baseline': m1.params.values.round(4),
    'StdErr_ABSA_Baseline': m1.bse.values.round(4),
    'PValue_ABSA_Baseline': m1.pvalues.values.round(4)
})

table2_df = pd.DataFrame({
    'Variable': m2.params.index,
    'Coef_Attribution_Discourse': m2.params.values.round(4),
    'StdErr_Attribution_Discourse': m2.bse.values.round(4),
    'PValue_Attribution_Discourse': m2.pvalues.values.round(4)
})

out_table1_path = 'data/derived_outputs/deep_research_absa_regressions.csv'
out_table2_path = 'data/derived_outputs/deep_research_attribution_discourse_regressions.csv'
table1_df.to_csv(out_table1_path, index=False, encoding='utf-8-sig')
table2_df.to_csv(out_table2_path, index=False, encoding='utf-8-sig')
print(f"\nSaved ABSA Baseline Regressions Summary -> {out_table1_path}")
print(f"Saved Attribution & Discourse Dynamics Summary -> {out_table2_path}")
