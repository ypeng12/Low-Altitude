#!/usr/bin/env python3
"""Ensure RESEARCH_NOTES_CN.md has explicit Stage 1 vs Stage 2 heading structure."""

from pathlib import Path
import subprocess

cn_path = Path("RESEARCH_NOTES_CN.md")
cn_text = cn_path.read_text(encoding="utf-8")

# Find heading 🔬
start_idx = cn_text.find("## 🔬 第一阶段：语料库推导")
if start_idx == -1:
    start_idx = cn_text.find("## 🔬")

end_idx = cn_text.find("## 📈 四、 步骤 6：N-Gram 挖掘与学术图表产出")

cn_two_stage_section = """## 🔬 第一阶段：语料库推导 Master 金标准情感代码本构建 (数据清洗与代码本推导阶段)

为避免盲目套用通用的标准情感词典（如 NRC、VADER 或 LIWC），本项目开发了一套针对**低空观光旅游（Low-Altitude Air Tourism）**的 **3 步语料库推导与人机协同审定方法论**。在全部 **21,215 条 Clean English 真实游客评论** 中，全量提取、规范化并审定领域专属的情感与评价词汇。

```text
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                       全量 Clean English 语料库 (N=21,215 条)                                   │
└────────────────────────────────────────────────────────┬────────────────────────────────────────────────────────┘
                                                         │
         ┌───────────────────────────────────────────────┼───────────────────────────────────────────────┐
         ▼                                               ▼                                               ▼
┌──────────────────────────────────────┐     ┌──────────────────────────────────────┐     ┌──────────────────────────────────────┐
│ 步骤 1: 500 条探索性抽样 (Discovery)  │     │ 步骤 2: 2,000 条金标准扩充 (Expansion) │     │ 步骤 3: 18,901 条全量未抽样评论补齐   │
│ 分层随机抽样 (Seed 42)               │     │ 分层随机抽样 (Seed 100)              │     │ 剩余未抽样全量语料                   │
│ 提取 372 个核心情感词                │     │ 扩充 173 个新情感词                  │     │ 提取 4,213 个候选词并精选补齐        │
└──────────────────┬───────────────────┘     └──────────────────┬───────────────────┘     └──────────────────┬───────────────────┘
                   │                                            │                                            │
                   └────────────────────────────────────────────┼────────────────────────────────────────────┘
                                                                │
                                                                ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 人机协同深度审定与错别字归一化 (canonical_lemma)                                                                │
│ - 错别字归一化: suprised->surprised, exhilerating->exhilarating, aprehensive->apprehensive                      │
│ - 严格规则剔除: 剔除 Grand Canyon 地名实体 (grand)、价格属性 (expensive)、口语感叹词 (wow/yay)                 │
│ - 最终定稿产物: 630 个 Master 金标准情感词 | 8,096 个 Master 被剔除词日志 (100% 零交集完备划分)                   │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### 1. 全过程推导步骤与演进历程

> [!IMPORTANT]
> **金标准情感词典递进相加公式与阶段关系**:
> 1. **初始 2,500 条样本阶段金标准情感词典 ($N=2,500$)**:
>    $$\\text{Stage 1 Discovery (500 条评论: 372 个词)} + \\text{Stage 2 Expansion (2,000 条评论: 173 个词)} = \\mathbf{545 \\text{ 个初始金标准情感词}}$$
> 2. **全量 21,215 条评论未精炼代码本 ($N=21,215$)**:
>    $$\\text{初始 2,500 样本情感词典 (545 个词)} + \\text{Stage Final 全量补齐新词 (63 个词)} = \\mathbf{608 \\text{ 个情感词}}$$
> 3. ** Master 终极精炼金标准代码本 ($N=630$)**:
>    $$\\text{基础代码本 (608 个词)} + \\text{人机协同细粒度扩充与精炼调整} = \\mathbf{630 \\text{ 个 Master 金标准情感词}}$$

#### 📍 步骤 1：500 条探索性抽样与词典发现 ($N=500$)
- **抽样协议**：采用分层随机抽样 ($N=500$, Seed 42)，跨 46 个观光产品、1–5 星级评分分布、机型与评论长度分位数进行均衡抽样。
- **推导产物**：提取出 **372 个纯正情感与评价词**（`data/derived_outputs/stage_discovery_500/clean_emotion_words_500_reviews.xlsx`）。

#### 📍 步骤 2：2,000 条金标准扩充与词汇扩展 ($N=2,000$)
- **抽样协议**：第二次分层随机抽样 ($N=2,000$, Seed 100，包含 1,814 条全新未抽样评论)。
- **推导产物**：新增挖掘出 **173 个新情感词**（`data/derived_outputs/stage_gold_2000/clean_emotion_words_2000_reviews.xlsx`），建立 545 词样本代码本。

#### 📍 步骤 3：18,901 条未抽样评论全量补齐 ($N=18,901$)
- **范围**：全量扫描剩余未抽样的 18,901 条评论 ($21,215 - 2,314 = 18,901$)。
- **推导产物**：提取 4,213 个词频 $\\ge 3$ 的候选词，人机协同精选补齐 63 个新词（`data/derived_outputs/stage_final/clean_new_emotion_words_18901.xlsx`）。

#### 📍 步骤 4：人机协同深度审定、错别字归一化与细粒度筛选法则
1. **错别字归一化 (`canonical_lemma`)**：建立了标准化字典词根双索引映射 (`word` $\\rightarrow$ `canonical_lemma`)，解决 `suprised` (4次) $\\rightarrow$ `surprised`、`worries` (38次) $\\rightarrow$ `worry` 词频分散问题。
2. **保留项法则 (630 词)**：涵盖 $E_1$ 体验者直接心理情绪 (*nervous, afraid, happy, thrilled*)、$E_2$ 刺激物与服务品质评价 (*scary, spectacular, smooth, professional*) 和美学惊叹 (*breathtakingly, sublime*)。
3. **剔除项法则 (8,096 词)**：清除了 `grand` (2,534次，大峡谷地名专有名词实体)、`expensive` (529次，客观价格属性评价)、`wow`/`yay` (结构感叹标记)、`knowledgeable`/`informative` (解说效率技能词) 及 `choppy` (气流颠簸物理感受)。

---

## 📊 第二阶段：通用词典套入对比实验与 NRC 理论框架归类分析 (数据分析阶段)

在 **第二阶段数据分析**（主要在 `data/analyze/` 目录下完成）中，我们将定稿的 **630 个 Master 金标准情感实词** 全量套入经典的 **NRC Emotion Lexicon**（Mohammad & Turney）中进行了对比映射与理论归类。

![NRC Gold Lexicon Distribution](figures/nrc_emotion_plots/nrc_mapping_gold_lexicon_distribution.png)

### 1. NRC 理论框架归类分析与结构分布 ($N=630$ 个金标准词)

```text
Master 金标准情感代码本 (全量 N = 630 个词)
│
├── 1️⃣ 开启词根归一化比对 (Lemma Normalized Match) ── 286 词 (45.40%) ⭐ (学术推荐使用)
│       (将复数、分词与错别字变体还原为字典词根后再比对，救回了 17 个真正具备 8 大情绪的词！)
│
├── 2️⃣ 只有 Positive / Negative 极性标记的词 ───────── 72 词 (11.43%)
│       (如: worth, interesting, cool, calm, fortunate, grateful, pristine)
│
└── 3️⃣ 完全不在 NRC 词库里的领域专属词 ───────────── 272 词 (43.17%)
        (如: great, amazing, best, awesome, fantastic, incredible, breathtaking, stunning, awe)
```

$$\\text{全量金标准代码本 (630)} = 286 \\text{ (8大情绪)} + 72 \\text{ (仅正负极性)} + 272 \\text{ (都不在 NRC)}$$

---

### 2. 双层匹配代码逻辑：原始字符串匹配 (Raw Match) vs. 词根归一化匹配 (Canonical Lemma Match)

```python
import pandas as pd
from nrclex import NRCLex

# 1. 加载 630 个 Master 金标准情感代码本
df_gold = pd.read_csv("data/analyze/gold_emotion_master.csv")
nrc_dict = NRCLex().__lexicon__
NRC8 = {"anger", "anticipation", "disgust", "fear", "joy", "sadness", "surprise", "trust"}

# 2. 原始字符串匹配 (Raw Exact String Match)
raw_8 = sum(1 for row in df_gold.itertuples() if len(set(nrc_dict.get(str(row.word).lower().strip(), [])) & NRC8) > 0)

# 3. 开启 canonical_lemma 词根归一化匹配 (Canonical Lemma Match)
lemma_8 = sum(1 for row in df_gold.itertuples() if len(set(nrc_dict.get(str(row.canonical_lemma).lower().strip(), [])) & NRC8) > 0 or len(set(nrc_dict.get(str(row.word).lower().strip(), [])) & NRC8) > 0)
```

| 匹配协议维度 | NRC 8 大情绪匹配词数 | 仅正负极性词数 | 彻底遗漏词数 | 代码本总词数 | 方法论对比结论 |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **原始字符串匹配 (Raw Exact Match)** | 269 个词 (42.70%) | 72 个词 (11.43%) | 289 个词 (45.87%) | 630 个词 | 错别字、动词过去式与复数变体被误判为“未识别” |
| **词根归一化匹配 (Canonical Lemma Match)** ⭐ | **286 个词 (45.40%)** | **72 个词 (11.43%)** | **272 个词 (43.17%)** | **630 个词** | **【推荐使用！】通过词根映射成功救回 17 个真实 8 大情绪词！** |

---

### 3. 通过 `canonical_lemma` 词根归一化协议救回的 17 个核心情感词

| 游客原始评论词 (`word`) | 归一化字典词根 (`canonical_lemma`) | 21,215 词频 | 被 NRC 提取出的真实 8 大情绪标签 | 为什么 Raw Match 会漏掉？ |
| :--- | :--- | :---: | :--- | :--- |
| **`worries`** | **`worry`** | 38 | `fear, anticipation, sadness` | NRC 原版只有单数 *worry*，复数 *-es* 漏掉了 |
| **`surprises`** | **`surprise`** | 21 | `fear, joy, surprise` | NRC 原版只有单数 *surprise*，复数 *-s* 漏掉了 |
| **`cherished`** | **`cherish`** | 8 | `trust, anticipation, joy, surprise` | NRC 只有原形 *cherish*，过去式 *-ed* 漏掉了 |
| **`hates`** | **`hate`** | 5 | `anger, fear, disgust, sadness` | 动词三单加 *-s* 漏掉了 |
| **`hated`** | **`hate`** | 5 | `anger, fear, disgust, sadness` | 动词过去式 *-ed* 漏掉了 |
| **`marveled`** | **`marvel`** | 5 | `surprise` | 动词过去式 *-ed* 漏掉了 |
| **`dreaded`** | **`dread`** | 4 | `fear, anticipation` | 分词形式 *-ed* 漏掉了 |
| **`dreading`** | **`dread`** | 4 | `fear, anticipation` | 分词形式 *-ing* 漏掉了 |
| **`scaring`** | **`scare`** | 3 | `anger, fear, anticipation, surprise` | 动词分词 *-ing* 漏掉了 |
| **`horribly`** | **`horrible`** | 3 | `anger, fear, disgust` | 副词后缀 *-ly* 漏掉了 |
| **`apprehensions`**| **`apprehension`** | 3 | `fear` | 名词复数 *-s* 漏掉了 |
| **`suprise`** | **`surprise`** | 5 | `fear, joy, surprise` | 游客错别字变体 (漏打 r) |
| **`suprised`** | **`surprised`** | 4 | `surprise` | 游客错别字变体 |
| **`dissapointed`** | **`disappointed`** | 8 | `anger, disgust, sadness` | 游客错别字变体 |
| **`aprehensive`** | **`apprehensive`** | 3 | `fear, anticipation` | 游客错别字变体 |
| **`disappointingly`**| **`disappointed`**| 3 | `anger, disgust, sadness` | 副词衍生变体 |
| **`lucked`** | **`lucky`** | 86 | `joy, surprise` | 动词化变体 |

---

### 4. NRC 通用词典发生遗漏的 4 大根本原因审定 ($N=272$ 个遗漏词)

1. **原因 1：静态词典对现代语法形态变体（Morphological Variants）补全严重不足 (占比 50.00%)**：
   - **分词形式 (-ing / -ed)**：78 个词 (28.68%)。如 *amazing, loved, breathtaking, stunning, impressed, inspiring, relaxed, scared, thrilling*.
   - **副词与比较级/最高级 (-ly, -est, -er)**：58 个词 (21.32%)。如 *best (3,420次), better (1,585次), incredibly (315次), perfectly (175次), cheaper, smoother, safely, regrettably*.
   - **论文结论**：传统 NRC 词典的词汇库缺乏形态学归一化机制，导致大批衍生情感形容词被漏掉。

2. **原因 2：NRC 原始种子词缺乏现代网络旅游的高频口语赞誉词 (占比 44.85%)**：
   - **典型词汇**：*great (11,541 次)、awesome (2,530 次)、fantastic (2,026 次)、incredible (1,612 次)、nice (1,794 次)、fabulous, phenomenal, unbeatable, top-notch*.
   - **深层原因**：NRC 选词偏向传统正式书面语，而 TripAdvisor 上的现代游客在表达满意时极其倾向于使用现代口语高唤起赞誉词（*great, awesome, fantastic*），导致 NRC 在现代在线评论场景中发生大规模失效！

3. **原因 3：通用词典缺失“低空高空视觉震撼与美学惊叹（Aerial Visual Awe）”领域词 (占比 3.31%)**：
   - **典型词汇**：*breathtaking (1,346 次)、stunning (552 次)、sublime (291 次)、scenic (400次), surreal (98次), majestic, panoramic, spellbinding, mesmerizing, awe (304次)*.
   - **深层原因**：低空观光旅游的核心体验是**“空中俯瞰带来的高唤起美学惊叹与视觉冲击（Awe / Aesthetic Emotion）”**。通用 NRC 词典完全没有针对该维度进行设计。

4. **原因 4：低空飞行感知风险与身体/心理躯体化症状词 (占比 1.84%)**：
   - **典型词汇**：*claustrophobia (幽闭恐惧)、jitters (忐忑颤抖)、airsick (晕机)、phobia (恐高症)、unnerving (让人发慌)*.
   - **深层原因**：颠簸、密闭舱室与高空悬浮引发游客独特的感知风险（Perceived Risk）与躯体化焦虑反应。

---

### 5. Master 金标准代码本 VADER 极性 vs. 游客星级散点图 (0.0 to 5.0 Stars)

![Master Gold VADER NRC Scatter Plot](data/analyze/master_gold_vader_nrc_scatter.png)
"""

if start_idx != -1 and end_idx != -1:
    cn_text = cn_text[:start_idx] + cn_two_stage_section + "\n\n" + cn_text[end_idx:]
    cn_path.write_text(cn_text, encoding="utf-8")
    print("Successfully replaced section in RESEARCH_NOTES_CN.md!")

# Re-generate Chinese PDF report
res_pdf = subprocess.run(["python3", "scratch/generate_pdf_report.py"], capture_output=True, text=True)
print(res_pdf.stdout.strip())
