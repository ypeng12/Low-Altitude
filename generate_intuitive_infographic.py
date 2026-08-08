import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# Set style for clean presentation
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = ['PingFang SC', 'Microsoft YaHei', 'SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

out_dir = 'figures'
os.makedirs(out_dir, exist_ok=True)

# Create a 3-panel horizontal Master Infographic (18 x 6.5 inches)
fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 6.5), dpi=300)

# -----------------------------------------------------------------------------
# Panel 1: 飞行员：加分第 1，但被骂扣分最狠！
# -----------------------------------------------------------------------------
items = ['夸飞行员 (飞行员好评)', '老天爷天气不好 (大雾大雨)', '骂飞行员 (飞行员失职)']
impacts = [0.0862, -0.1415, -0.5217]
colors = ['#10B981', '#F59E0B', '#EF4444']

y_pos = np.arange(len(items))
bars1 = ax1.barh(y_pos, impacts, color=colors, height=0.45, edgecolor='black', linewidth=1.2, zorder=3)

ax1.axvline(0.0, color='#475569', linestyle='-', linewidth=1.5, zorder=2)
ax1.set_yticks(y_pos)
ax1.set_yticklabels(items, fontsize=11, fontweight='bold')
ax1.set_xlim(-0.7, 0.25)
ax1.set_xlabel('对游客星级评分的影响 (星级变化)', fontsize=11, fontweight='bold', labelpad=8)
ax1.set_title('核心 1：飞行员极重要\n【夸他加分最高，骂他扣分最狠】', fontsize=13, fontweight='bold', color='#1E293B', pad=12)

for bar, val in zip(bars1, impacts):
    width = bar.get_width()
    offset = 0.015 if val >= 0 else -0.015
    align = 'left' if val >= 0 else 'right'
    text_str = f"+{val:.3f} 星 (加分第1)" if val > 0 else f"{val:.3f} 星"
    ax1.text(width + offset, bar.get_y() + bar.get_height()/2.0, text_str, va='center', ha=align, fontsize=10.5, fontweight='bold', color=bar.get_facecolor())

# 气泡解释框
ax1.text(-0.65, 2.25, '[提示] 游客心理：老天爷刮风下雨不能怪商家，\n但飞行员如果态度差，坚决给差评！', bbox=dict(boxstyle='round,pad=0.5', facecolor='#F8FAFC', edgecolor='#64748B', alpha=0.95), fontsize=9.5, fontweight='bold', color='#334155')

# -----------------------------------------------------------------------------
# Panel 2: 恶劣天气下，飞行员如何神级“救场”？
# -----------------------------------------------------------------------------
steps = ['晴天默认\n体验', '遇到大雾大雨\n(扣分 -0.18星)', '大雾 + 飞行员救场\n(反弹 +0.31星!)']
ratings = [4.782, 4.602, 4.910]
step_colors = ['#94A3B8', '#EF4444', '#10B981']

bars2 = ax2.bar(steps, ratings, color=step_colors, width=0.45, edgecolor='black', linewidth=1.2, zorder=3)
ax2.set_ylim(4.5, 5.02)
ax2.set_ylabel('游客最终打分 (1 ~ 5 星)', fontsize=11, fontweight='bold', labelpad=8)
ax2.set_title('核心 2：飞行员能“神级救场”\n【即使天气不好，优秀服务也能反弹好评】', fontsize=13, fontweight='bold', color='#1E293B', pad=12)

for bar, r in zip(bars2, ratings):
    yval = bar.get_height()
    diff = r - ratings[0]
    diff_str = f"({diff:+.3f}星)" if abs(diff) > 0.001 else "(基准分)"
    ax2.text(bar.get_x() + bar.get_width()/2.0, yval + 0.008, f"{r:.3f} 分\n{diff_str}", ha='center', va='bottom', fontsize=10.5, fontweight='bold')

# 救场反弹标注框
ax2.annotate(
    '优质服务反弹救场！',
    xy=(2, 4.910), xytext=(1.05, 4.955),
    arrowprops=dict(facecolor='#10B981', shrink=0.08, width=2, headwidth=7),
    bbox=dict(boxstyle='round,pad=0.4', facecolor='#D1FAE5', edgecolor='#10B981', alpha=0.95),
    fontsize=9.5, fontweight='bold', color='#065F46'
)

# -----------------------------------------------------------------------------
# Panel 3: 说话看后半句 —— but 后面才是打分关键！
# -----------------------------------------------------------------------------
ax3.axis('off')
ax3.set_title('核心 3：说话看后半句 (but 法则)\n【前面写再多困难害怕，but 后是好评就是 5 星】', fontsize=13, fontweight='bold', color='#1E293B', pad=12)

# 画一个包含评论例句的直观展示卡片
card_html = (
    "真实例子解析：\n\n"
    "前半句 (害怕/晕机/大雾)：\n"
    "“起飞前我极其害怕，大雾弥漫...” [负面焦虑]\n"
    "  ↓ (转折词 BUT)\n"
    "后半句 (飞行员平稳/热心)：\n"
    "“但是飞行员开得超平稳，沿途解说太棒了！” [极度正面]\n\n"
    "---------------------------------------\n"
    "【打分结果】： 5 星满分好评！ (5.0 / 5.0)\n\n"
    "[核心结论]：决定星级的是转折句后半段！"
)

ax3.text(0.05, 0.92, card_html, transform=ax3.transAxes, va='top', ha='left', fontsize=11, fontweight='bold', color='#1E293B',
         bbox=dict(boxstyle='round,pad=0.8', facecolor='#FEF3C7', edgecolor='#F59E0B', linewidth=1.5, alpha=0.95))

fig.suptitle('低空观光游客打分心理三大核心规律（外行秒懂版通俗图解）', fontsize=16, fontweight='bold', y=1.03, color='#0F172A')
plt.tight_layout()

out_fig_path = os.path.join(out_dir, 'tourist_psychology_infographic.png')
plt.savefig(out_fig_path, dpi=300, bbox_inches='tight')
plt.close()

print(f"Successfully generated Master Infographic -> {out_fig_path}")
