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
# 图 1：各个体验维度对星级评分的影响（加分项 vs 扣分项 对比图）
# -----------------------------------------------------------------------------
absa_csv = 'data/derived_outputs/deep_research_absa_regressions.csv'
df_absa = pd.read_csv(absa_csv)

# 筛选核心领域维度
df_domain = df_absa[~df_absa['Variable'].isin(['Intercept', 'word_count_std', 'is_us_domestic'])].copy()

# 中文通俗标签映射
zh_name_map = {
    'pilot_pos': '飞行员表现优异 (Pilot Positive)',
    'scenery_pos': '景色壮丽震撼 (Scenery Positive)',
    'safety_assurance': '安全感确立 (Safety Reassurance)',
    'fear_anxiety': '心理紧张/刺激 (Fear/Thrill)',
    'ground_staff_pos': '地勤服务热情 (Ground Staff Positive)',
    'weather_pos': '天气晴朗能见度高 (Weather Positive)',
    'price_value_pos': '价格合理划算 (Price Positive)',
    'scenery_neg': '景观不佳 (Scenery Negative)',
    'weather_neg': '天气恶劣/大雾 (Weather Negative)',
    'pilot_neg': '飞行员态度/技术差 (Pilot Negative)',
    'ground_staff_neg': '地勤服务态度恶劣 (Ground Staff Negative)',
    'price_value_neg': '价格昂贵/极不划算 (Price Negative)'
}

df_domain['ZH_Name'] = df_domain['Variable'].map(lambda x: zh_name_map.get(x, x))
df_domain = df_domain.sort_values(by='Coef_ABSA_Baseline', ascending=True)

fig, ax = plt.subplots(figsize=(13, 8), dpi=300)

y_pos = np.arange(len(df_domain))
coefs = df_domain['Coef_ABSA_Baseline'].values
names = df_domain['ZH_Name'].values
colors = ['#E11D48' if c < 0 else '#10B981' for c in coefs]

bars = ax.barh(y_pos, coefs, color=colors, height=0.6, edgecolor='black', linewidth=1.0, zorder=3)

ax.axvline(0.0, color='#475569', linestyle='-', linewidth=1.5, zorder=2)
ax.set_yticks(y_pos)
ax.set_yticklabels(names, fontsize=11, fontweight='bold')
ax.set_xlabel('对游客星级评分的影响程度 (回归系数 β)', fontsize=12, fontweight='bold', labelpad=10)
ax.set_title('图 1：低空旅游各个体验维度的评分影响（加分 vs 扣分）\n【绿色右边为加分项：飞行员好评加分最多 (+0.086星) | 红色左边为扣分项：价格昂贵与服务差扣分最惨 (-0.52~-0.66星)】', fontsize=13, fontweight='bold', pad=15)

for bar, c in zip(bars, coefs):
    width = bar.get_width()
    offset = 0.012 if c >= 0 else -0.012
    align = 'left' if c >= 0 else 'right'
    color = '#047857' if c >= 0 else '#B91C1C'
    label_str = f"+{c:.4f} 星" if c >= 0 else f"{c:.4f} 星"
    ax.text(width + offset, bar.get_y() + bar.get_height()/2.0, label_str, va='center', ha=align, fontsize=10.5, fontweight='bold', color=color)

# 添加重点标注框
ax.text(0.09, 10.8, '[+] 飞行员优秀服务：\n加分第 1 名 (+0.0862星)', bbox=dict(boxstyle='round,pad=0.5', facecolor='#D1FAE5', edgecolor='#10B981', alpha=0.9), fontsize=10, fontweight='bold', color='#065F46')
ax.text(-0.62, 1.2, '[-] 价格昂贵与地勤恶劣：\n扣分最惨重 (-0.56 ~ -0.66星)', bbox=dict(boxstyle='round,pad=0.5', facecolor='#FEE2E2', edgecolor='#EF4444', alpha=0.9), fontsize=10, fontweight='bold', color='#991B1B')

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

# 弧线箭头标注“救场反弹”
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

# 左图：模型解释力提升（R² 暴涨）
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

# 右图：转折句后半段得分与评分的关系
x_post = np.linspace(-1.0, 1.0, 100)
y_pred = 4.176 + 0.8094 * x_post

ax2.plot(x_post, y_pred, color='#4338CA', linewidth=3.5, label='转折句后半段情感得分 (β = +0.8094)')
ax2.axvline(0.0, color='#94A3B8', linestyle='--', linewidth=1.2)
ax2.set_xlabel('but (但是) 转折句后半段的情感极性 (-1负面 ~ +1正面)', fontsize=11, fontweight='bold', labelpad=10)
ax2.set_ylabel('游客预测星级评分 (1 ~ 5 星)', fontsize=11, fontweight='bold', labelpad=10)
ax2.set_title('右图：but 转折句后半段越正面，评分越高\n(斜率 β = +0.8094, 极具决定性)', fontsize=12, fontweight='bold', pad=12)

# 在右图添加文字解释
ax2.text(-0.85, 4.75, '前半句再多害怕或抱怨\n只要 but 后半句是好评\n最终就是 5 星！', bbox=dict(boxstyle='round,pad=0.5', facecolor='#FEF3C7', edgecolor='#F59E0B', alpha=0.95), fontsize=10, fontweight='bold', color='#92400E')

fig.suptitle('图 3：为什么转折句 "but" 后的内容才是决定游客最终打分的关键？', fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
fig3_path = os.path.join(out_dir, 'discourse_clause_r2_jump.png')
plt.savefig(fig3_path, dpi=300, bbox_inches='tight')
plt.close()
print(f"Saved Figure 3 -> {fig3_path}")
