import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os

# Set style for clean conceptual graph rendering
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = ['PingFang SC', 'Microsoft YaHei', 'SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

out_dir = 'figures'
os.makedirs(out_dir, exist_ok=True)

# -----------------------------------------------------------------------------
# Function to generate Chinese Version Conceptual Graph
# -----------------------------------------------------------------------------
def build_conceptual_graph_zh():
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(15, 11), dpi=300)
    
    # -------------------------------------------------------------------------
    # 机制 1：恐惧到安全感的心理转化 (Emotional Transformation Flow)
    # -------------------------------------------------------------------------
    ax1.axis('off')
    ax1.set_title('机制一：情绪唤起与心理转化模型 (Fear-to-Safety Transformation)', fontsize=13, fontweight='bold', color='#1E293B', pad=10)
    
    # Draw Boxes for Mechanism 1
    # Node 1: Initial Fear
    box1 = patches.FancyBboxPatch((0.05, 0.25), 0.24, 0.5, boxstyle="round,pad=0.08", fc="#FEE2E2", ec="#EF4444", lw=1.5)
    ax1.add_patch(box1)
    ax1.text(0.17, 0.5, "起初恐惧与情绪唤起\n(Initial Fear / Thrill)\n“terrified, nervous”\n[NRC/VADER误判为负面]", ha="center", va="center", fontsize=10, fontweight="bold", color="#991B1B")
    
    # Arrow 1
    ax1.annotate("", xy=(0.37, 0.5), xytext=(0.30, 0.5), arrowprops=dict(arrowstyle="->", lw=2.5, color="#64748B"))
    ax1.text(0.335, 0.62, "飞行员专业安抚\n(Pilot Reassurance)", ha="center", va="center", fontsize=9.5, fontweight="bold", color="#0369A1")
    
    # Node 2: Transformation Process
    box2 = patches.FancyBboxPatch((0.38, 0.25), 0.24, 0.5, boxstyle="round,pad=0.08", fc="#E0F2FE", ec="#0284C7", lw=1.5)
    ax1.add_patch(box2)
    ax1.text(0.50, 0.5, "心理转化与安全感确立\n(Safety Reassurance)\n“made me feel completely safe”\n[消除风险恐惧]", ha="center", va="center", fontsize=10, fontweight="bold", color="#075985")
    
    # Arrow 2
    ax1.annotate("", xy=(0.70, 0.5), xytext=(0.63, 0.5), arrowprops=dict(arrowstyle="->", lw=2.5, color="#10B981"))
    
    # Node 3: Transformed Peak Experience
    box3 = patches.FancyBboxPatch((0.71, 0.25), 0.24, 0.5, boxstyle="round,pad=0.08", fc="#D1FAE5", ec="#10B981", lw=1.5)
    ax1.add_patch(box3)
    ax1.text(0.83, 0.5, "转换为难忘高峰体验\n(Peak Experience)\n最终锁死 5 星满分！\n[Rating: 5.0 / 5.0]", ha="center", va="center", fontsize=10.5, fontweight="bold", color="#065F46")

    # -------------------------------------------------------------------------
    # 机制 2：责任归因拆分 (Locus of Attribution & Responsibility Split)
    # -------------------------------------------------------------------------
    ax2.axis('off')
    ax2.set_title('机制二：责任归因拆分与服务救场模型 (Locus of Control & Mitigation)', fontsize=13, fontweight='bold', color='#1E293B', pad=10)

    # Node: Negative Event
    box_ev = patches.FancyBboxPatch((0.03, 0.3), 0.20, 0.4, boxstyle="round,pad=0.06", fc="#F3F4F6", ec="#4B5563", lw=1.5)
    ax2.add_patch(box_ev)
    ax2.text(0.13, 0.5, "局部负面经历发生\n“clouds prevented\nseeing Denali”", ha="center", va="center", fontsize=9.5, fontweight="bold", color="#1F2937")

    # Divergent Arrows
    ax2.annotate("", xy=(0.33, 0.72), xytext=(0.24, 0.55), arrowprops=dict(arrowstyle="->", lw=2, color="#EF4444"))
    ax2.annotate("", xy=(0.33, 0.28), xytext=(0.24, 0.45), arrowprops=dict(arrowstyle="->", lw=2, color="#10B981"))

    # Upper Split: Uncontrollable Weather
    box_uncont = patches.FancyBboxPatch((0.34, 0.55), 0.28, 0.38, boxstyle="round,pad=0.06", fc="#FEF3C7", ec="#F59E0B", lw=1.5)
    ax2.add_patch(box_uncont)
    ax2.text(0.48, 0.74, "评价目标 A：不可控天气 (Weather)\n归因：老天爷自然条件 (非商家责任)\n影响：微弱扣分 (-0.1415星)", ha="center", va="center", fontsize=9.5, fontweight="bold", color="#92400E")

    # Lower Split: Controllable Operator Service
    box_cont = patches.FancyBboxPatch((0.34, 0.08), 0.28, 0.38, boxstyle="round,pad=0.06", fc="#E0F2FE", ec="#0284C7", lw=1.5)
    ax2.add_patch(box_cont)
    ax2.text(0.48, 0.27, "评价目标 B：可控服务人员 (Pilot)\n归因：飞行员热情解说/替代路线\n影响：巨大加分与救场 (+0.2788星)", ha="center", va="center", fontsize=9.5, fontweight="bold", color="#075985")

    # Convergent Arrows to Final Evaluation
    ax2.annotate("", xy=(0.71, 0.5), xytext=(0.63, 0.70), arrowprops=dict(arrowstyle="->", lw=2, color="#10B981"))
    ax2.annotate("", xy=(0.71, 0.5), xytext=(0.63, 0.30), arrowprops=dict(arrowstyle="->", lw=2, color="#10B981"))

    # Final Node: Net Positive Evaluation
    box_final2 = patches.FancyBboxPatch((0.72, 0.3), 0.23, 0.4, boxstyle="round,pad=0.06", fc="#D1FAE5", ec="#10B981", lw=1.5)
    ax2.add_patch(box_final2)
    ax2.text(0.835, 0.5, "对运营商评价占主导\n净效益翻盘为正！\n最终给出 5 星好评\n[Rating: 5.0 / 5.0]", ha="center", va="center", fontsize=10, fontweight="bold", color="#065F46")

    # -------------------------------------------------------------------------
    # 机制 3：服务补救的过程性结构 (Dynamic Process of Service Recovery)
    # -------------------------------------------------------------------------
    ax3.axis('off')
    ax3.set_title('机制三：服务补救过程结构模型 (Initial Failure → Recovery → Resolution)', fontsize=13, fontweight='bold', color='#1E293B', pad=10)

    # Phase 1: Initial Failure
    box_p1 = patches.FancyBboxPatch((0.05, 0.25), 0.24, 0.5, boxstyle="round,pad=0.08", fc="#FEE2E2", ec="#EF4444", lw=1.5)
    ax3.add_patch(box_p1)
    ax3.text(0.17, 0.5, "阶段 1：初始问题/故障\n(Initial Failure / Delay)\n大风延误/行程受阻/心理焦虑\n[产生局部负面词]", ha="center", va="center", fontsize=10, fontweight="bold", color="#991B1B")

    # Arrow 1->2
    ax3.annotate("", xy=(0.37, 0.5), xytext=(0.30, 0.5), arrowprops=dict(arrowstyle="->", lw=2.5, color="#64748B"))
    ax3.text(0.335, 0.62, "触发敏捷服务补救\n(Trigger Recovery)", ha="center", va="center", fontsize=9.5, fontweight="bold", color="#D97706")

    # Phase 2: Service Recovery
    box_p2 = patches.FancyBboxPatch((0.38, 0.25), 0.24, 0.5, boxstyle="round,pad=0.08", fc="#FEF3C7", ec="#F59E0B", lw=1.5)
    ax3.add_patch(box_p2)
    ax3.text(0.50, 0.5, "阶段 2：服务补救与改期\n(Service Recovery)\n快捷退款/改换绝佳替代路线\n飞行员耐心安抚", ha="center", va="center", fontsize=10, fontweight="bold", color="#92400E")

    # Arrow 2->3
    ax3.annotate("", xy=(0.70, 0.5), xytext=(0.63, 0.5), arrowprops=dict(arrowstyle="->", lw=2.5, color="#10B981"))
    ax3.text(0.665, 0.62, "赢得超预期信任\n(Trust Gain)", ha="center", va="center", fontsize=9.5, fontweight="bold", color="#047857")

    # Phase 3: Positive Resolution
    box_p3 = patches.FancyBboxPatch((0.71, 0.25), 0.24, 0.5, boxstyle="round,pad=0.08", fc="#D1FAE5", ec="#10B981", lw=1.5)
    ax3.add_patch(box_p3)
    ax3.text(0.83, 0.5, "阶段 3：正面圆满解决\n(Positive Resolution)\n“处理得非常妥善！”\n最终锁死 5 星好评！\n[Rating: 5.0 / 5.0]", ha="center", va="center", fontsize=10.5, fontweight="bold", color="#065F46")

    fig.suptitle('高满意度低空旅游评论中局部负面表达的三大深层机制结构图', fontsize=15, fontweight='bold', y=1.01, color='#0F172A')
    plt.tight_layout()

    zh_path = os.path.join(out_dir, 'three_mechanisms_conceptual_graph_zh.png')
    plt.savefig(zh_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved Chinese Conceptual Graph -> {zh_path}")


# -----------------------------------------------------------------------------
# Function to generate English Version Conceptual Graph
# -----------------------------------------------------------------------------
def build_conceptual_graph_en():
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(15.5, 11), dpi=300)
    
    # -------------------------------------------------------------------------
    # Mechanism 1: Fear-to-Safety Transformation
    # -------------------------------------------------------------------------
    ax1.axis('off')
    ax1.set_title('Mechanism 1: Emotional Arousal & Fear-to-Safety Psychological Transformation', fontsize=13, fontweight='bold', color='#1E293B', pad=10)
    
    box1 = patches.FancyBboxPatch((0.05, 0.25), 0.24, 0.5, boxstyle="round,pad=0.08", fc="#FEE2E2", ec="#EF4444", lw=1.5)
    ax1.add_patch(box1)
    ax1.text(0.17, 0.5, "Initial Fear & Arousal\n(High Perceived Risk)\n\"terrified, nervous\"\n[Flagged negative by Lexicons]", ha="center", va="center", fontsize=9.5, fontweight="bold", color="#991B1B")
    
    ax1.annotate("", xy=(0.37, 0.5), xytext=(0.30, 0.5), arrowprops=dict(arrowstyle="->", lw=2.5, color="#64748B"))
    ax1.text(0.335, 0.62, "Pilot Professional Reassurance\n(Safety Buffer)", ha="center", va="center", fontsize=9, fontweight="bold", color="#0369A1")
    
    box2 = patches.FancyBboxPatch((0.38, 0.25), 0.24, 0.5, boxstyle="round,pad=0.08", fc="#E0F2FE", ec="#0284C7", lw=1.5)
    ax1.add_patch(box2)
    ax1.text(0.50, 0.5, "Psychological Transformation\n(Safety Reassurance)\n\"made me feel completely safe\"\n[Risk Conquered]", ha="center", va="center", fontsize=9.5, fontweight="bold", color="#075985")
    
    ax1.annotate("", xy=(0.70, 0.5), xytext=(0.63, 0.5), arrowprops=dict(arrowstyle="->", lw=2.5, color="#10B981"))
    
    box3 = patches.FancyBboxPatch((0.71, 0.25), 0.24, 0.5, boxstyle="round,pad=0.08", fc="#D1FAE5", ec="#10B981", lw=1.5)
    ax1.add_patch(box3)
    ax1.text(0.83, 0.5, "Transformed Peak Experience\n(High Thrill + Security)\nLocks in 5.0 Star Rating!\n[Rating: 5.0 / 5.0]", ha="center", va="center", fontsize=10, fontweight="bold", color="#065F46")

    # -------------------------------------------------------------------------
    # Mechanism 2: Locus of Control & Mitigation
    # -------------------------------------------------------------------------
    ax2.axis('off')
    ax2.set_title('Mechanism 2: Responsibility Attribution Split & Service Mitigation Effect', fontsize=13, fontweight='bold', color='#1E293B', pad=10)

    box_ev = patches.FancyBboxPatch((0.03, 0.3), 0.20, 0.4, boxstyle="round,pad=0.06", fc="#F3F4F6", ec="#4B5563", lw=1.5)
    ax2.add_patch(box_ev)
    ax2.text(0.13, 0.5, "Local Negative Event\n\"clouds prevented\nseeing Denali\"", ha="center", va="center", fontsize=9.5, fontweight="bold", color="#1F2937")

    ax2.annotate("", xy=(0.33, 0.72), xytext=(0.24, 0.55), arrowprops=dict(arrowstyle="->", lw=2, color="#EF4444"))
    ax2.annotate("", xy=(0.33, 0.28), xytext=(0.24, 0.45), arrowprops=dict(arrowstyle="->", lw=2, color="#10B981"))

    box_uncont = patches.FancyBboxPatch((0.34, 0.55), 0.28, 0.38, boxstyle="round,pad=0.06", fc="#FEF3C7", ec="#F59E0B", lw=1.5)
    ax2.add_patch(box_uncont)
    ax2.text(0.48, 0.74, "Target A: Uncontrollable Weather\nAttribution: Nature / Force Majeure\nImpact: Minor Penalty (-0.1415★)", ha="center", va="center", fontsize=9, fontweight="bold", color="#92400E")

    box_cont = patches.FancyBboxPatch((0.34, 0.08), 0.28, 0.38, boxstyle="round,pad=0.06", fc="#E0F2FE", ec="#0284C7", lw=1.5)
    ax2.add_patch(box_cont)
    ax2.text(0.48, 0.27, "Target B: Controllable Operator Service\nAttribution: Pilot Excellence / Alt Route\nImpact: Major Rebound (+0.2788★)", ha="center", va="center", fontsize=9, fontweight="bold", color="#075985")

    ax2.annotate("", xy=(0.71, 0.5), xytext=(0.63, 0.70), arrowprops=dict(arrowstyle="->", lw=2, color="#10B981"))
    ax2.annotate("", xy=(0.71, 0.5), xytext=(0.63, 0.30), arrowprops=dict(arrowstyle="->", lw=2, color="#10B981"))

    box_final2 = patches.FancyBboxPatch((0.72, 0.3), 0.23, 0.4, boxstyle="round,pad=0.06", fc="#D1FAE5", ec="#10B981", lw=1.5)
    ax2.add_patch(box_final2)
    ax2.text(0.835, 0.5, "Operator Attribution Dominates\nNet Utility Positive!\nFinal Rating: 5.0 Stars\n[Rating: 5.0 / 5.0]", ha="center", va="center", fontsize=9.5, fontweight="bold", color="#065F46")

    # -------------------------------------------------------------------------
    # Mechanism 3: Dynamic Process of Service Recovery
    # -------------------------------------------------------------------------
    ax3.axis('off')
    ax3.set_title('Mechanism 3: Dynamic Process Structure of Service Recovery (Failure → Recovery → Resolution)', fontsize=13, fontweight='bold', color='#1E293B', pad=10)

    box_p1 = patches.FancyBboxPatch((0.05, 0.25), 0.24, 0.5, boxstyle="round,pad=0.08", fc="#FEE2E2", ec="#EF4444", lw=1.5)
    ax3.add_patch(box_p1)
    ax3.text(0.17, 0.5, "Phase 1: Initial Failure\n(Weather Delay / Friction)\nFlight cancelled or bumpy\n[Generates local neg words]", ha="center", va="center", fontsize=9.5, fontweight="bold", color="#991B1B")

    ax3.annotate("", xy=(0.37, 0.5), xytext=(0.30, 0.5), arrowprops=dict(arrowstyle="->", lw=2.5, color="#64748B"))
    ax3.text(0.335, 0.62, "Triggers Agile Service Recovery", ha="center", va="center", fontsize=9, fontweight="bold", color="#D97706")

    box_p2 = patches.FancyBboxPatch((0.38, 0.25), 0.24, 0.5, boxstyle="round,pad=0.08", fc="#FEF3C7", ec="#F59E0B", lw=1.5)
    ax3.add_patch(box_p2)
    ax3.text(0.50, 0.5, "Phase 2: Service Recovery\n(Adaptive Action)\nFast refund / Alternative route\nPilot reassuring narration", ha="center", va="center", fontsize=9.5, fontweight="bold", color="#92400E")

    ax3.annotate("", xy=(0.70, 0.5), xytext=(0.63, 0.5), arrowprops=dict(arrowstyle="->", lw=2.5, color="#10B981"))
    ax3.text(0.665, 0.62, "Builds Trust & Gratitude", ha="center", va="center", fontsize=9, fontweight="bold", color="#047857")

    box_p3 = patches.FancyBboxPatch((0.71, 0.25), 0.24, 0.5, boxstyle="round,pad=0.08", fc="#D1FAE5", ec="#10B981", lw=1.5)
    ax3.add_patch(box_p3)
    ax3.text(0.83, 0.5, "Phase 3: Positive Resolution\n(Satisfactory Outcome)\n\"Handled exceptionally well!\"\nLocks in 5.0 Star Rating!\n[Rating: 5.0 / 5.0]", ha="center", va="center", fontsize=10, fontweight="bold", color="#065F46")

    fig.suptitle('Structural Model of Rating–Text Incongruence Mechanisms in Aerial Tourism', fontsize=15, fontweight='bold', y=1.01, color='#0F172A')
    plt.tight_layout()

    en_path = os.path.join(out_dir, 'three_mechanisms_conceptual_graph_en.png')
    plt.savefig(en_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved English Conceptual Graph -> {en_path}")


if __name__ == '__main__':
    build_conceptual_graph_zh()
    build_conceptual_graph_en()
