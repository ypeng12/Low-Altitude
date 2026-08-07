import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Set font family to support Chinese & English cleanly
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = ['PingFang SC', 'Microsoft YaHei', 'SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

out_dir = 'figures'
os.makedirs(out_dir, exist_ok=True)

# -----------------------------------------------------------------------------
# 图 1：ABSA 属性极性影响 —— 清晰拆分为加分项与扣分项双面板对比图
# -----------------------------------------------------------------------------
absa_csv = 'data/derived_outputs/deep_research_absa_regressions.csv'
df_absa = pd.read_csv(absa_csv)

# 正面好评因素子集
pos_vars = ['pilot_pos', 'scenery_pos', 'safety_assurance', 'ground_staff_pos', 'weather_pos', 'price_value_pos']
pos_labels = [
    '飞行员服务优异 (Pilot Positive)',
    '景色震撼壮丽 (Scenery Positive)',
    '安全感建立确立 (Safety Reassurance)',
    '地勤接待热情 (Ground Staff Positive)',
    '天气晴朗能见度高 (Weather Positive)',
    '价格合理划算 (Price Positive)'
]

# 负面抱怨因素子集
neg_vars = ['price_value_neg', 'ground_staff_neg', 'pilot_neg', 'weather_neg', 'scenery_neg']
neg_labels = [
    '价格昂贵/极不划算 (Price Negative)',
    '地面前台服务恶劣 (Ground Staff Negative)',
    '飞行员失职/服务差 (Pilot Negative)',
    '老天爷天气恶劣/大雾 (Weather Negative)',
    '景色地貌不佳 (Scenery Negative)'
]

df_pos = df_absa[df_absa['Variable'].isin(pos_vars)].copy()
df_pos['Label'] = df_pos['Variable'].map(dict(zip(pos_vars, pos_labels)))
df_pos = df_pos.sort_values(by='Coef_ABSA_Baseline', ascending=True)

df_neg = df_absa[df_absa['Variable'].isin(neg_vars)].copy()
df_neg['Label'] = df_neg['Variable'].map(dict(zip(neg_vars, neg_labels)))
df_neg = df_neg.sort_values(by='Coef_ABSA_Baseline', ascending=False) # Most negative at bottom

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6.5), dpi=300)

# 上/左面板：正面加分项
y1 = np.arange(len(df_pos))
c1 = df_pos['Coef_ABSA_Baseline'].values
l1 = df_pos['Label'].values

bars1 = ax1.barh(y1, c1, color='#10B981', height=0.55, edgecolor='black', linewidth=1.0, zorder=3)
ax1.set_yticks(y1)
ax1.set_yticklabels(l1, fontsize=10.5, fontweight='bold')
ax1.set_xlim(0.0, 0.11)
ax1.set_xlabel('加分影响程度 (+ 星级)', fontsize=11, fontweight='bold', labelpad=8)
ax1.set_title('【左图：正面体验加分项】\n飞行员优秀服务加分第 1 名 (+0.0862星)', fontsize=12, fontweight='bold', color='#065F46')

for bar, val in zip(bars1, c1):
    ax1.text(val + 0.003, bar.get_y() + bar.get_height()/2.0, f"+{val:.4f} 星", va='center', ha='left', fontsize=10, fontweight='bold', color='#047857')

# 右面板：负面扣分项
y2 = np.arange(len(df_neg))
c2 = df_neg['Coef_ABSA_Baseline'].values
l2 = df_neg['Label'].values

bars2 = ax2.barh(y2, c2, color='#EF4444', height=0.55, edgecolor='black', linewidth=1.0, zorder=3)
ax2.set_yticks(y2)
ax2.set_yticklabels(l2, fontsize=10.5, fontweight='bold')
ax2.set_xlim(-0.75, 0.0)
ax2.set_xlabel('扣分严重程度 (- 星级)', fontsize=11, fontweight='bold', labelpad=8)
ax2.set_title('【右图：负面体验扣分项】\n价格昂贵与地勤态度差扣分最惨重 (-0.56 ~ -0.66星)', fontsize=12, fontweight='bold', color='#991B1B')

for bar, val in zip(bars2, c2):
    ax2.text(val - 0.015, bar.get_y() + bar.get_height()/2.0, f"{val:.4f} 星", va='center', ha='right', fontsize=10, fontweight='bold', color='#B91C1C')

fig.suptitle('图 1：ABSA 属性级极性对星级评分的影响（正面加分 vs 负面扣分）', fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
fig1_path = os.path.join(out_dir, 'absa_marginal_effects_forest_plot.png')
plt.savefig(fig1_path, dpi=300, bbox_inches='tight')
plt.close()
print(f"Saved Figure 1 -> {fig1_path}")

# -----------------------------------------------------------------------------
# 图 2：恶劣天气下，飞行员能否“救场”？（归因缓冲三步法对比图）
# -----------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(11, 6.5), dpi=300)

steps = [
    '第 1 步：正常体验\n(晴朗天气 / 默认服务)',
    '第 2 步：遇到恶劣天气/大雾\n(天气负面扣分 -0.18星)',
    '第 3 步：恶劣天气 + 飞行员神级救场\n(飞行员优秀服务补救反弹 +0.31星!)'
]

baseline = 4.7822
bad_weather = baseline - 0.1803
bad_weather_good_pilot = baseline - 0.1803 + 0.0297 + 0.2788  # 4.9104

ratings = [baseline, bad_weather, bad_weather_good_pilot]
step_colors = ['#94A3B8', '#F43F5E', '#10B981']

bars2 = ax.bar(steps, ratings, color=step_colors, width=0.48, edgecolor='black', linewidth=1.2, zorder=3)

ax.set_ylim(4.5, 5.0)
ax.set_ylabel('游客预测平均评分 (1 ~ 5 星)', fontsize=12, fontweight='bold', labelpad=10)
ax.set_title('图 2：恶劣天气下飞行员的“救场反弹效应”（归因缓冲机制）\n【恶劣天气本来会导致评分下降 (-0.18星)，但飞行员优质服务拉动了 +0.2788 的巨大反弹！】', fontsize=13, fontweight='bold', pad=15)

for bar, r in zip(bars2, ratings):
    yval = bar.get_height()
    diff = r - baseline
    diff_str = f" ({diff:+.3f}星)" if abs(diff) > 0.001 else " (基准线)"
    ax.text(bar.get_x() + bar.get_width()/2.0, yval + 0.008, f"{r:.3f} 星\n{diff_str}", ha='center', va='bottom', fontsize=11, fontweight='bold')

ax.annotate(
    '飞行员救场反弹效应！\n(+0.2788 交互作用补救)',
    xy=(2, bad_weather_good_pilot), xytext=(1.15, 4.935),
    arrowprops=dict(facecolor='#10B981', shrink=0.08, width=2.5, headwidth=9),
    bbox=dict(boxstyle='round,pad=0.5', facecolor='#D1FAE5', edgecolor='#10B981', alpha=0.95),
    fontsize=11, fontweight='bold', color='#065F46'
)

plt.tight_layout()
fig2_path = os.path.join(out_dir, 'attribution_mitigation_interaction.png')
plt.savefig(fig2_path, dpi=300, bbox_inches='tight')
plt.close()
print(f"Saved Figure 2 -> {fig2_path}")

# -----------------------------------------------------------------------------
# 图 3：为什么转折句 "but" 后面才是打分关键？（模型对比图）
# -----------------------------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6.5), dpi=300)

models = ['旧方法：忽略转折句\n(仅看属性词)', '新方法：加入 but 转折句分析\n(看转折句后半段极性)']
r2_vals = [11.87, 24.88]
m_colors = ['#94A3B8', '#6366F1']

bars_r2 = ax1.bar(models, r2_vals, color=m_colors, width=0.45, edgecolor='black', linewidth=1.2, zorder=3)
ax1.set_ylim(0, 32)
ax1.set_ylabel('模型解释能力 (R² 解释率 %)', fontsize=12, fontweight='bold', labelpad=10)
ax1.set_title('左图：对游客打分行为的解释能力对比\n(加入转折句分析后，解释力暴涨 109%)', fontsize=12, fontweight='bold', pad=12)

for bar, val in zip(bars_r2, r2_vals):
    ax1.text(bar.get_x() + bar.get_width()/2.0, val + 0.8, f"{val:.2f}%", ha='center', va='bottom', fontsize=12, fontweight='bold')

ax1.annotate(
    '解释力翻倍暴涨！\n(+109.6% 提升)',
    xy=(1, 24.88), xytext=(0.3, 27.5),
    arrowprops=dict(facecolor='#6366F1', shrink=0.08, width=2.5, headwidth=8),
    bbox=dict(boxstyle='round,pad=0.4', facecolor='#EEF2FF', edgecolor='#6366F1', alpha=0.9),
    fontsize=10.5, fontweight='bold', color='#3730A3'
)

x_post = np.linspace(-1.0, 1.0, 100)
y_pred = 4.176 + 0.8094 * x_post

ax2.plot(x_post, y_pred, color='#4338CA', linewidth=3.5, label='转折句后半段情感得分 (β = +0.8094)')
ax2.axvline(0.0, color='#94A3B8', linestyle='--', linewidth=1.2)
ax2.set_xlabel('but (但是) 转折句后半段的情感极性 (-1负面 ~ +1正面)', fontsize=11, fontweight='bold', labelpad=10)
ax2.set_ylabel('游客预测星级评分 (1 ~ 5 星)', fontsize=11, fontweight='bold', labelpad=10)
ax2.set_title('右图：but 转折句后半段越正面，评分越高\n(斜率 β = +0.8094, 极具决定性)', fontsize=12, fontweight='bold', pad=12)

ax2.text(-0.85, 4.75, '前半句再多害怕或抱怨\n只要 but 后半句是好评\n最终就是 5 星！', bbox=dict(boxstyle='round,pad=0.5', facecolor='#FEF3C7', edgecolor='#F59E0B', alpha=0.95), fontsize=10, fontweight='bold', color='#92400E')

fig.suptitle('图 3：为什么转折句 "but" 后的内容才是决定游客最终打分的关键？', fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
fig3_path = os.path.join(out_dir, 'discourse_clause_r2_jump.png')
plt.savefig(fig3_path, dpi=300, bbox_inches='tight')
plt.close()
print(f"Saved Figure 3 -> {fig3_path}")
