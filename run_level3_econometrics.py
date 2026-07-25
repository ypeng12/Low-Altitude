import pandas as pd
import numpy as np
import re
import os
import sys
from nrclex import NRCLex
from scipy import stats
import statsmodels.api as sm
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt
import seaborn as sns

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

# Set aesthetic styling for plots
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

def extract_nrc_scores_batch(df):
    """
    Extract NRC 8 basic emotions and 2 sentiment valences using NRCLex for all reviews.
    Emotions: joy, trust, anticipation, surprise, fear, sadness, disgust, anger, positive, negative.
    """
    print("Extracting NRC Emotion Association Lexicon scores (NRCLex v4)...")
    nrc_cols = ['nrc_joy', 'nrc_trust', 'nrc_anticipation', 'nrc_surprise', 
                'nrc_fear', 'nrc_sadness', 'nrc_disgust', 'nrc_anger', 
                'nrc_positive', 'nrc_negative']
    
    nrc_obj = NRCLex()
    nrc_data = []
    total = len(df)
    
    for idx, text in enumerate(df['review_text']):
        if idx > 0 and idx % 5000 == 0:
            print(f"  Processed {idx}/{total} reviews ({idx/total*100:.1f}%)...")
            
        if not isinstance(text, str) or not text.strip():
            nrc_data.append({c: 0.0 for c in nrc_cols})
            continue
            
        words = re.findall(r'\b\w+\b', text.lower())
        word_count = len(words) if len(words) > 0 else 1
        
        nrc_obj.load_token_list(words)
        scores = nrc_obj.raw_emotion_scores
        
        # Calculate emotion word ratio (density)
        nrc_data.append({
            'nrc_joy': scores.get('joy', 0) / word_count,
            'nrc_trust': scores.get('trust', 0) / word_count,
            'nrc_anticipation': scores.get('anticipation', 0) / word_count,
            'nrc_surprise': scores.get('surprise', 0) / word_count,
            'nrc_fear': scores.get('fear', 0) / word_count,
            'nrc_sadness': scores.get('sadness', 0) / word_count,
            'nrc_disgust': scores.get('disgust', 0) / word_count,
            'nrc_anger': scores.get('anger', 0) / word_count,
            'nrc_positive': scores.get('positive', 0) / word_count,
            'nrc_negative': scores.get('negative', 0) / word_count,
        })
        
    nrc_df = pd.DataFrame(nrc_data)
    for col in nrc_cols:
        df[col] = nrc_df[col]
        
    print(f"Successfully computed NRC emotion scores for {total} reviews.")
    return df

def run_spearman_correlations(df, output_dir):
    """
    Compute Spearman Rank Correlations between NRC emotions and ratings across 5 traveler typologies.
    Methodology strictly follows Orea-Giner et al. (2022).
    """
    print("\n--- 1. Computing Spearman Rank Correlations (NRC Emotions vs Rating) ---")
    traveler_types = ['Couples', 'Family', 'Solo', 'Friends', 'Business']
    nrc_emotions = ['nrc_anger', 'nrc_anticipation', 'nrc_disgust', 'nrc_fear', 
                    'nrc_joy', 'nrc_sadness', 'nrc_surprise', 'nrc_trust', 
                    'nrc_positive', 'nrc_negative']
    
    records = []
    for t_type in traveler_types:
        sub_df = df[df['trip_type'] == t_type]
        if len(sub_df) < 50:
            continue
            
        row = {'Traveler_Type': t_type, 'N_Obs': len(sub_df)}
        for emo in nrc_emotions:
            r, p = stats.spearmanr(sub_df[emo], sub_df['rating'])
            # Format coefficient with significance stars
            stars = '***' if p < 0.001 else ('**' if p < 0.01 else ('*' if p < 0.05 else ''))
            row[emo] = f"{r:.3f}{stars}"
            row[f"{emo}_raw_r"] = r
            row[f"{emo}_p"] = p
        records.append(row)
        
    corr_df = pd.DataFrame(records)
    out_path = os.path.join(output_dir, 'paper_table_spearman_nrc_ratings.csv')
    corr_df.to_csv(out_path, index=False)
    print(f"Saved Spearman Rank Correlation Table to {out_path}")
    print(corr_df[['Traveler_Type', 'N_Obs', 'nrc_joy', 'nrc_trust', 'nrc_disgust', 'nrc_fear', 'nrc_negative']])
    return corr_df

def run_logistic_odds_ratios(df, output_dir):
    """
    Estimate Multivariate Logistic Regressions for High Rating (Rating>=4 vs <4)
    and compute Odds Ratios (beta) by traveler typologies (Orea-Giner et al. 2022).
    """
    print("\n--- 2. Estimating Multivariate Logistic Regressions & Odds Ratios ---")
    df['high_rating'] = (df['rating'] >= 4).astype(int)
    traveler_types = ['Couples', 'Family', 'Solo', 'Friends', 'Business']
    
    nrc_emotions = ['nrc_anger', 'nrc_anticipation', 'nrc_disgust', 'nrc_fear', 
                    'nrc_joy', 'nrc_sadness', 'nrc_surprise', 'nrc_trust', 
                    'nrc_positive', 'nrc_negative']
    
    results = []
    for t_type in traveler_types:
        sub_df = df[df['trip_type'] == t_type].copy()
        if len(sub_df) < 100:
            continue
            
        # Standardize NRC scores for comparable Odds Ratios
        for emo in nrc_emotions:
            std = sub_df[emo].std()
            sub_df[f"{emo}_z"] = (sub_df[emo] - sub_df[emo].mean()) / std if std > 0 else 0
            
        formula = 'high_rating ~ ' + ' + '.join([f"{emo}_z" for emo in nrc_emotions]) + ' + review_word_count + is_us_domestic'
        try:
            model = smf.logit(formula, data=sub_df).fit(disp=False)
            
            row = {'Traveler_Type': t_type, 'N_Obs': len(sub_df), 'Pseudo_R2': model.prsquared}
            for emo in nrc_emotions:
                param = model.params.get(f"{emo}_z", 0)
                pval = model.pvalues.get(f"{emo}_z", 1.0)
                odds_ratio = np.exp(param)
                stars = '***' if pval < 0.001 else ('**' if pval < 0.01 else ('*' if pval < 0.05 else ''))
                row[f"{emo}_OddsRatio"] = f"{odds_ratio:.3f}{stars}"
                row[f"{emo}_OR_val"] = odds_ratio
                row[f"{emo}_p"] = pval
            results.append(row)
        except Exception as e:
            print(f"Warning: Logistic model for {t_type} failed: {e}")
            
    or_df = pd.DataFrame(results)
    out_path = os.path.join(output_dir, 'paper_table_nrc_logistic_odds_ratios.csv')
    or_df.to_csv(out_path, index=False)
    print(f"Saved Logistic Regression Odds Ratio Table to {out_path}")
    if not or_df.empty:
        print(or_df[['Traveler_Type', 'N_Obs', 'Pseudo_R2', 'nrc_joy_OddsRatio', 'nrc_trust_OddsRatio', 'nrc_disgust_OddsRatio']])
    return or_df

def run_econometric_regressions(df, output_dir):
    """
    Estimate Structural Econometric Regressions (OLS & Product Fixed Effects).
    Y = Rating (1-5 stars)
    X = NRC Emotions + VADER Sentiment Polarity + Low-Altitude Domain Lexicons + Product FE
    """
    print("\n--- 3. Estimating Structural Econometric Regressions (OLS + Product FE) ---")
    sub_df = df[df['is_english'] == 1].copy()
    
    # Model 1: Baseline Controls
    m1 = smf.ols('rating ~ review_word_count + uppercase_ratio + is_us_domestic + has_photo', data=sub_df).fit(cov_type='HC1')
    
    # Model 2: Adding VADER & NRC Emotions
    m2 = smf.ols('rating ~ sentiment_polarity + nrc_joy + nrc_trust + nrc_disgust + nrc_fear + review_word_count + is_us_domestic + has_photo', data=sub_df).fit(cov_type='HC1')
    
    # Model 3: Adding Domain Touchpoints & Risk Features
    m3 = smf.ols('rating ~ sentiment_polarity + nrc_joy + nrc_trust + nrc_disgust + pilot_mention + safety_mention + price_value_mention + weather_mention + review_word_count + is_us_domestic + has_photo', data=sub_df).fit(cov_type='HC1')
    
    # Model 4: Full Model with Product Fixed Effects (C(tour_name))
    m4 = smf.ols('rating ~ sentiment_polarity + nrc_joy + nrc_trust + nrc_disgust + pilot_mention + safety_mention + price_value_mention + weather_mention + review_word_count + is_us_domestic + has_photo + C(tour_name)', data=sub_df).fit(cov_type='HC1')
    
    print("\n=== MODEL SUMMARY (MODEL 4: FULL ECONOMETRIC MODEL WITH PRODUCT FIXED EFFECTS) ===")
    print(f"N Observations: {m4.nobs}")
    print(f"R-squared: {m4.rsquared:.4f} | Adj R-squared: {m4.rsquared_adj:.4f}")
    
    key_vars = ['Intercept', 'sentiment_polarity', 'nrc_joy', 'nrc_trust', 'nrc_disgust', 
                'pilot_mention', 'safety_mention', 'price_value_mention', 'weather_mention', 'is_us_domestic']
    
    summary_data = []
    for var in key_vars:
        if var in m4.params:
            coef = m4.params[var]
            se = m4.bse[var]
            pval = m4.pvalues[var]
            stars = '***' if pval < 0.001 else ('**' if pval < 0.01 else ('*' if pval < 0.05 else ''))
            summary_data.append({
                'Variable': var,
                'Model1_Coef': f"{m1.params.get(var, np.nan):.4f}" if var in m1.params else "-",
                'Model2_Coef': f"{m2.params.get(var, np.nan):.4f}" if var in m2.params else "-",
                'Model3_Coef': f"{m3.params.get(var, np.nan):.4f}" if var in m3.params else "-",
                'Model4_Full_FE': f"{coef:.4f}{stars}",
                'Std_Err': f"({se:.4f})",
                'P_Value': f"{pval:.4f}"
            })
            
    reg_df = pd.DataFrame(summary_data)
    out_path = os.path.join(output_dir, 'paper_table_econometric_regressions.csv')
    reg_df.to_csv(out_path, index=False)
    print(f"Saved Econometric Regression Results Table to {out_path}")
    print(reg_df[['Variable', 'Model4_Full_FE', 'Std_Err', 'P_Value']])
    return reg_df

def plot_nrc_visualizations(df, figures_dir):
    """
    Generate publication-quality figures for NRC emotion distributions across traveler types and touchpoints.
    """
    print("\n--- 4. Generating Publication-Quality Figures for NRC Emotions ---")
    
    # Figure 1: NRC 8 Emotions across 5 Traveler Typologies
    traveler_types = ['Couples', 'Family', 'Solo', 'Friends', 'Business']
    nrc_8 = ['nrc_joy', 'nrc_trust', 'nrc_anticipation', 'nrc_surprise', 
             'nrc_fear', 'nrc_sadness', 'nrc_disgust', 'nrc_anger']
    
    mean_data = []
    for t in traveler_types:
        sub = df[df['trip_type'] == t]
        if len(sub) > 0:
            for emo in nrc_8:
                mean_data.append({
                    'Traveler_Type': t,
                    'Emotion': emo.replace('nrc_', '').capitalize(),
                    'Mean_Ratio': sub[emo].mean() * 100
                })
                
    emo_df = pd.DataFrame(mean_data)
    
    plt.figure(figsize=(12, 6))
    ax = sns.barplot(data=emo_df, x='Emotion', y='Mean_Ratio', hue='Traveler_Type', palette='Set2')
    plt.title('NRC 8 Basic Psychological Emotions Across 5 Traveler Typologies', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel('NRC Basic Emotion Dimensions', fontsize=12, fontweight='bold')
    plt.ylabel('Average Word Density (%)', fontsize=12, fontweight='bold')
    plt.legend(title='Traveler Typology', frameon=True, facecolor='white')
    plt.tight_layout()
    fig1_path = os.path.join(figures_dir, 'nrc_emotions_by_traveler_type.png')
    plt.savefig(fig1_path, dpi=300)
    plt.close()
    print(f"Saved Figure 1: {fig1_path}")
    
    # Figure 2: Touchpoint Disaggregation (Pilot vs Guide vs Staff) vs NRC Emotions
    touchpoints = [('pilot_mention', 'Pilot Touchpoint'), 
                   ('guide_mention', 'Tour Guide Touchpoint'), 
                   ('staff_service_mention', 'Ground Staff Touchpoint')]
    
    tp_data = []
    for col, label in touchpoints:
        sub = df[df[col] == 1]
        for emo in ['nrc_joy', 'nrc_trust', 'nrc_disgust', 'nrc_fear', 'nrc_anger']:
            tp_data.append({
                'Touchpoint': label,
                'Emotion': emo.replace('nrc_', '').capitalize(),
                'Mean_Ratio': sub[emo].mean() * 100
            })
            
    tp_df = pd.DataFrame(tp_data)
    
    plt.figure(figsize=(10, 5))
    ax = sns.barplot(data=tp_df, x='Emotion', y='Mean_Ratio', hue='Touchpoint', palette='viridis')
    plt.title('NRC Emotions Disaggregated by Service Touchpoints (Pilots vs Guides vs Staff)', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel('Key NRC Emotion Dimensions', fontsize=12, fontweight='bold')
    plt.ylabel('Average Word Density (%)', fontsize=12, fontweight='bold')
    plt.legend(title='Service Touchpoint', frameon=True, facecolor='white')
    plt.tight_layout()
    fig2_path = os.path.join(figures_dir, 'nrc_emotions_by_touchpoint.png')
    plt.savefig(fig2_path, dpi=300)
    plt.close()
    print(f"Saved Figure 2: {fig2_path}")

def main():
    master_path = 'data/cleaned_datasets/tripadvisor_processed_master.csv'
    derived_dir = 'data/derived_outputs'
    figures_dir = 'figures'
    
    os.makedirs(derived_dir, exist_ok=True)
    os.makedirs(figures_dir, exist_ok=True)
    
    print(f"Loading Master Dataset from {master_path}...")
    df = pd.read_csv(master_path)
    print(f"Loaded {len(df)} clean records.")
    
    # Step 1: Compute NRC Emotion Scores if not present or recalculate
    df = extract_nrc_scores_batch(df)
    
    # Save enriched master dataset back
    df.to_csv(master_path, index=False)
    print(f"Updated Master Dataset with NRC Emotion columns at {master_path}")
    
    # Also save a dedicated Level 3 CSV for econometrics
    level3_csv = 'data/cleaned_datasets/tripadvisor_level3_econometrics.csv'
    df.to_csv(level3_csv, index=False)
    print(f"Saved Level 3 Econometric Dataset to {level3_csv}")
    
    # Step 2: Run Spearman Correlations
    run_spearman_correlations(df, derived_dir)
    
    # Step 3: Run Logistic Regressions & Odds Ratios
    run_logistic_odds_ratios(df, derived_dir)
    
    # Step 4: Run Econometric OLS & Fixed Effects Regressions
    run_econometric_regressions(df, derived_dir)
    
    # Step 5: Generate Visualizations
    plot_nrc_visualizations(df, figures_dir)
    
    print("\n=======================================================")
    print("✅ LEVEL 3 ECONOMETRIC & NRC EMOTION PIPELINE COMPLETE!")
    print("=======================================================")

if __name__ == '__main__':
    main()
