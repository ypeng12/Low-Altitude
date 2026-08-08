import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# Set style for clean publication presentation
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
plt.rcParams['axes.unicode_minus'] = False

out_dir = 'figures'
os.makedirs(out_dir, exist_ok=True)

# Create a 3-panel horizontal Master Infographic (18.5 x 6.5 inches)
fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18.5, 6.5), dpi=300)

# -----------------------------------------------------------------------------
# Panel 1: Core 1: Asymmetric Pilot Impact
# -----------------------------------------------------------------------------
items = ['Praising Pilot (Pilot Positive)', 'Bad Weather (Uncontrollable Factor)', 'Blaming Pilot (Pilot Negative)']
impacts = [0.0862, -0.1415, -0.5217]
colors = ['#10B981', '#F59E0B', '#EF4444']

y_pos = np.arange(len(items))
bars1 = ax1.barh(y_pos, impacts, color=colors, height=0.45, edgecolor='black', linewidth=1.2, zorder=3)

ax1.axvline(0.0, color='#475569', linestyle='-', linewidth=1.5, zorder=2)
ax1.set_yticks(y_pos)
ax1.set_yticklabels(items, fontsize=10.5, fontweight='bold')
ax1.set_xlim(-0.75, 0.28)
ax1.set_xlabel('Marginal Rating Impact (Star Rating Change Δ)', fontsize=11, fontweight='bold', labelpad=8)
ax1.set_title('Core 1: Asymmetric Pilot Impact\n[Praise yields #1 gain (+0.086★); Fault yields severe penalty (-0.522★)]', fontsize=12.5, fontweight='bold', color='#1E293B', pad=12)

for bar, val in zip(bars1, impacts):
    width = bar.get_width()
    offset = 0.015 if val >= 0 else -0.015
    align = 'left' if val >= 0 else 'right'
    text_str = f"+{val:.3f}★ (#1 Positive Gain)" if val > 0 else f"{val:.3f}★ (Severe Drop)" if val < -0.3 else f"{val:.3f}★"
    ax1.text(width + offset, bar.get_y() + bar.get_height()/2.0, text_str, va='center', ha=align, fontsize=10, fontweight='bold', color=bar.get_facecolor())

ax1.text(-0.70, 2.25, '[Insight] Bad weather is attributed to nature, but\npoor pilot service triggers heavy rating penalties!', bbox=dict(boxstyle='round,pad=0.5', facecolor='#F8FAFC', edgecolor='#64748B', alpha=0.95), fontsize=9.5, fontweight='bold', color='#334155')

# -----------------------------------------------------------------------------
# Panel 2: Core 2: Service Mitigation Effect
# -----------------------------------------------------------------------------
steps = ['Good Weather\n(Baseline: 4.782★)', 'Bad Weather Only\n(Drops by -0.180★)', 'Bad Weather + Pilot Rebound\n(Rebounds by +0.31★!)']
ratings = [4.782, 4.602, 4.910]
step_colors = ['#94A3B8', '#EF4444', '#10B981']

bars2 = ax2.bar(steps, ratings, color=step_colors, width=0.45, edgecolor='black', linewidth=1.2, zorder=3)
ax2.set_ylim(4.5, 5.02)
ax2.set_ylabel('Predicted Tourist Star Rating (Scale 1-5)', fontsize=11, fontweight='bold', labelpad=8)
ax2.set_title('Core 2: Service Mitigation Effect\n[Pilot excellence rebounds rating losses caused by bad weather]', fontsize=12.5, fontweight='bold', color='#1E293B', pad=12)

for bar, r in zip(bars2, ratings):
    yval = bar.get_height()
    diff = r - ratings[0]
    diff_str = f"({diff:+.3f}★)" if abs(diff) > 0.001 else "(Baseline)"
    ax2.text(bar.get_x() + bar.get_width()/2.0, yval + 0.008, f"{r:.3f}★\n{diff_str}", ha='center', va='bottom', fontsize=10.5, fontweight='bold')

ax2.annotate(
    'Service Mitigation & Rebound!\n(+0.2788 Interaction)',
    xy=(2, 4.910), xytext=(0.95, 4.955),
    arrowprops=dict(facecolor='#10B981', shrink=0.08, width=2, headwidth=7),
    bbox=dict(boxstyle='round,pad=0.4', facecolor='#D1FAE5', edgecolor='#10B981', alpha=0.95),
    fontsize=9.5, fontweight='bold', color='#065F46'
)

# -----------------------------------------------------------------------------
# Panel 3: Core 3: Post-Adversative Clause Focus
# -----------------------------------------------------------------------------
ax3.axis('off')
ax3.set_title('Core 3: Post-Adversative Clause Focus\n[Post-adversative clause ("but") resolution dominates final rating]', fontsize=12.5, fontweight='bold', color='#1E293B', pad=12)

card_html = (
    "Actual Review Breakdown:\n\n"
    "Pre-Adversative Clause (Fear / Bad Weather):\n"
    "\"I was terrified before takeoff, cloudy weather...\" [Negative Arousal]\n"
    "  ↓ (Discourse Connector BUT)\n"
    "Post-Adversative Clause (Pilot Narration / Smooth Flight):\n"
    "\"BUT the pilot was super reassuring and smooth!\" [Positive Resolution]\n\n"
    "----------------------------------------------------\n"
    "[Final Tourist Rating]: 5.0 / 5.0 Stars (Full Rating)\n\n"
    "[Key Takeaway]: Post-adversative resolution dominates star rating!"
)

ax3.text(0.02, 0.92, card_html, transform=ax3.transAxes, va='top', ha='left', fontsize=10.5, fontweight='bold', color='#1E293B',
         bbox=dict(boxstyle='round,pad=0.7', facecolor='#FEF3C7', edgecolor='#F59E0B', linewidth=1.5, alpha=0.95))

fig.suptitle('Tourist Rating Psychology in Low-Altitude Aerial Tourism: 3 Core Mechanisms', fontsize=15, fontweight='bold', y=1.03, color='#0F172A')
plt.tight_layout()

out_fig_path_en = os.path.join(out_dir, 'tourist_psychology_infographic_en.png')
out_fig_path_main = os.path.join(out_dir, 'tourist_psychology_infographic.png')
plt.savefig(out_fig_path_en, dpi=300, bbox_inches='tight')
plt.savefig(out_fig_path_main, dpi=300, bbox_inches='tight')
plt.close()

print(f"Successfully generated English Master Infographic -> {out_fig_path_en}")
