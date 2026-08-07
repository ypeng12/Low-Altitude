import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Set aesthetic style
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

out_dir = 'figures'
os.makedirs(out_dir, exist_ok=True)

# -----------------------------------------------------------------------------
# Figure 1: ABSA Marginal Impact Forest Plot (Point 1: Impact Ranking)
# -----------------------------------------------------------------------------
absa_csv = 'data/derived_outputs/deep_research_absa_regressions.csv'
df_absa = pd.read_csv(absa_csv)

# Filter out Intercept, word_count, and domestic controls for domain focus
df_domain = df_absa[~df_absa['Variable'].isin(['Intercept', 'word_count_std', 'is_us_domestic'])].copy()

# Friendly Variable Names
name_map = {
    'pilot_pos': 'Pilot Positive (+)',
    'scenery_pos': 'Scenery Positive (+)',
    'safety_assurance': 'Safety Assurance (+)',
    'fear_anxiety': 'Fear / Anxiety (+)',
    'ground_staff_pos': 'Ground Staff Positive (+)',
    'weather_pos': 'Weather Positive (+)',
    'price_value_pos': 'Price / Value Positive (+)',
    'scenery_neg': 'Scenery Negative (-)',
    'weather_neg': 'Weather Negative (-)',
    'pilot_neg': 'Pilot Negative (-)',
    'ground_staff_neg': 'Ground Staff Negative (-)',
    'price_value_neg': 'Price / Value Negative (-)'
}

df_domain['Clean_Name'] = df_domain['Variable'].map(lambda x: name_map.get(x, x))
df_domain['CI_Lower'] = df_domain['Coef_ABSA_Baseline'] - 1.96 * df_domain['StdErr_ABSA_Baseline']
df_domain['CI_Upper'] = df_domain['Coef_ABSA_Baseline'] + 1.96 * df_domain['StdErr_ABSA_Baseline']

# Sort by coefficient value
df_domain = df_domain.sort_values(by='Coef_ABSA_Baseline', ascending=True)

fig, ax = plt.subplots(figsize=(12, 7.5), dpi=300)

y_positions = np.arange(len(df_domain))
coefs = df_domain['Coef_ABSA_Baseline'].values
errors = 1.96 * df_domain['StdErr_ABSA_Baseline'].values
colors = ['#DC2626' if c < 0 else '#16A34A' for c in coefs]

for i, (c, y, col, err) in enumerate(zip(coefs, y_positions, colors, errors)):
    ax.errorbar(c, y, xerr=err, fmt='none', ecolor=col, elinewidth=2.5, capsize=4, capthick=1.5, zorder=3)
    ax.scatter(c, y, color=col, s=110, zorder=4, edgecolors='black', linewidth=1)
    align = 'left' if c >= 0 else 'right'
    offset = 0.015 if c >= 0 else -0.015
    ax.text(c + offset, y, f"{c:+.4f}", va='center', ha=align, fontsize=10, fontweight='bold', color=col)

ax.axvline(0.0, color='#64748B', linestyle='--', linewidth=1.5, zorder=2)
ax.set_yticks(y_positions)
ax.set_yticklabels(df_domain['Clean_Name'], fontsize=11, fontweight='bold')
ax.set_xlabel('Marginal Impact on Tourist Rating (OLS Regression Coefficient β with 95% CI)', fontsize=12, labelpad=10)
ax.set_title('Figure 1: ABSA Marginal Impact on Tourist Star Rating (Aspect Polarity Ranking)\n[Pilot Positive is #1 Positive Driver (+0.086); Price & Service Negatives Cause Severe Penalties (-0.52 to -0.66)]', fontsize=13, fontweight='bold', pad=15)

plt.tight_layout()
fig1_path = os.path.join(out_dir, 'absa_marginal_effects_forest_plot.png')
plt.savefig(fig1_path, dpi=300, bbox_inches='tight')
plt.close()
print(f"Saved Figure 1 -> {fig1_path}")

# -----------------------------------------------------------------------------
# Figure 2: Attribution Compensation Effect (Point 2: Weather vs Pilot Mitigation)
# -----------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 6), dpi=300)

scenarios = [
    'Baseline\n(Good Weather / Neutral Service)',
    'Bad Weather Only\n(Weather Neg = 1, Pilot Neutral)',
    'Bad Weather + Superior Pilot\n(Weather Neg = 1, Pilot Pos = 1)'
]

baseline = 4.7822
bad_weather_only = baseline - 0.1803
bad_weather_good_pilot = baseline - 0.1803 + 0.0297 + 0.2788  # +0.1282 net improvement

ratings = [baseline, bad_weather_only, bad_weather_good_pilot]
bar_colors = ['#94A3B8', '#EF4444', '#10B981']

bars = ax.bar(scenarios, ratings, color=bar_colors, width=0.55, edgecolor='black', linewidth=1.2, zorder=3)

ax.set_ylim(4.5, 5.0)
ax.set_ylabel('Predicted Tourist Star Rating (Scale 1-5)', fontsize=12, labelpad=10)
ax.set_title('Figure 2: Attribution Compensation Effect\n[How Superior Pilot Service (+0.2788 Interaction) Mitigates Bad Weather Rating Loss]', fontsize=13, fontweight='bold', pad=15)

for bar, r in zip(bars, ratings):
    yval = bar.get_height()
    diff = r - baseline
    diff_text = f" ({diff:+.3f})" if abs(diff) > 0.001 else " (Ref)"
    ax.text(bar.get_x() + bar.get_width()/2.0, yval + 0.01, f"{r:.3f}{diff_text}", ha='center', va='bottom', fontsize=11, fontweight='bold')

ax.annotate(
    'Mitigation & Rebound (+0.2788 Interaction)',
    xy=(2, bad_weather_good_pilot), xytext=(1.15, 4.93),
    arrowprops=dict(facecolor='#10B981', shrink=0.08, width=2, headwidth=8),
    fontsize=11, fontweight='bold', color='#047857'
)

plt.tight_layout()
fig2_path = os.path.join(out_dir, 'attribution_mitigation_interaction.png')
plt.savefig(fig2_path, dpi=300, bbox_inches='tight')
plt.close()
print(f"Saved Figure 2 -> {fig2_path}")

# -----------------------------------------------------------------------------
# Figure 3: Discourse Clause Focus & R-squared Jump (Point 3: 'But' Clause)
# -----------------------------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), dpi=300)

# Panel A: R-squared Jump Comparison
models = ['Model 1: Aspect Polarity Baseline\n(Without Discourse Clause)', 'Model 2: Discourse-Aware Model\n(With Post-But Clause & Attribution)']
r2_values = [11.87, 24.88]
p_colors = ['#64748B', '#6366F1']

bars_r2 = ax1.bar(models, r2_values, color=p_colors, width=0.5, edgecolor='black', linewidth=1.2, zorder=3)
ax1.set_ylim(0, 30)
ax1.set_ylabel('Model Explanatory Power (R² %)', fontsize=12, labelpad=10)
ax1.set_title('Panel A: Model Explanatory Power (R² Jump)', fontsize=12, fontweight='bold')

for bar, val in zip(bars_r2, r2_values):
    ax1.text(bar.get_x() + bar.get_width()/2.0, val + 0.8, f"{val:.2f}%", ha='center', va='bottom', fontsize=12, fontweight='bold')

ax1.annotate(
    '+109.6% Increase in R²',
    xy=(1, 24.88), xytext=(0.35, 27),
    arrowprops=dict(facecolor='#6366F1', shrink=0.08, width=2, headwidth=8),
    fontsize=11, fontweight='bold', color='#4338CA'
)

# Panel B: Post-But Sentiment Marginal Impact (Slope = +0.8094)
post_but_x = np.linspace(-1.0, 1.0, 100)
pred_rating_y = 4.176 + 0.8094 * post_but_x

ax2.plot(post_but_x, pred_rating_y, color='#4338CA', linewidth=3, label='Post-But Clause Compound Sentiment (β = +0.8094, p < 0.001)')
ax2.axvline(0.0, color='#94A3B8', linestyle='--', linewidth=1.2)
ax2.set_xlabel('Post-Adversative Clause Sentiment Score (S_post_but)', fontsize=11, labelpad=10)
ax2.set_ylabel('Predicted Tourist Rating (Scale 1-5)', fontsize=11, labelpad=10)
ax2.set_title('Panel B: Post-But Clause Sentiment Slope (β = +0.8094)', fontsize=12, fontweight='bold')
ax2.legend(loc='lower right', fontsize=10)

fig.suptitle('Figure 3: Discourse Clause Focus ("But" Dynamics) & Model R² Jump', fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
fig3_path = os.path.join(out_dir, 'discourse_clause_r2_jump.png')
plt.savefig(fig3_path, dpi=300, bbox_inches='tight')
plt.close()
print(f"Saved Figure 3 -> {fig3_path}")
