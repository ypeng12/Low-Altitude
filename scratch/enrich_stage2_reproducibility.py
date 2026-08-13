#!/usr/bin/env python3
"""Enrich Stage 2 in README.md and RESEARCH_NOTES_CN.md with exact python script paths, output files, and mathematical step-by-step derivation."""

from pathlib import Path
import subprocess

readme_path = Path("README.md")
cn_path = Path("RESEARCH_NOTES_CN.md")

readme_text = readme_path.read_text(encoding="utf-8")
cn_text = cn_path.read_text(encoding="utf-8")

readme_stage2_rich = """## 📊 Stage 2: Generic Lexicon Audit & NRC Framework Classification (Data Analysis & Reproducibility)

In **Stage 2 Data Analysis** (conducted in `data/analyze/`), we mapped our **630 Master Gold Emotion Terms** (`data/analyze/gold_emotion_master.csv`) against the **NRC Emotion Lexicon v0.92** (14,182 vocabulary universe) to evaluate generic lexicon coverage gaps and categorize our domain codebook under the NRC theoretical framework.

![NRC Gold Lexicon Distribution](figures/nrc_emotion_plots/nrc_mapping_gold_lexicon_distribution.png)

---

### 1. File Directory, Script Locations & Direct Artifact Links

All scripts and derived outputs for Stage 2 are transparently stored in the repository:

| Stage 2 Core Component | File Path / Command | Description & Operational Purpose | Direct Link |
| :--- | :--- | :--- | :---: |
| **Input Master Gold Codebook** | `data/analyze/gold_emotion_master.csv` | Primary input file containing all 630 Master Gold Emotion Terms with `canonical_lemma` mapping. | 👉 [`gold_emotion_master.csv`](file:///Users/yuliangpeng/Desktop/Low-Altitude/data/analyze/gold_emotion_master.csv) |
| **Audit Verification Script** | `scratch/audit_gold_630_nrc_tree.py` | Executable python audit script that reads NRC lexicon and calculates the exact 3-level tree breakdown. | 👉 [`audit_gold_630_nrc_tree.py`](file:///Users/yuliangpeng/Desktop/Low-Altitude/scratch/audit_gold_630_nrc_tree.py) |
| **Full NRC Combined Output** | `data/analyze/gold_emotion_nrc_combined.xlsx` | Combined dataset merging 630 Gold words with NRC 8-emotion tags and polarity labels. | 👉 [`gold_emotion_nrc_combined.xlsx`](file:///Users/yuliangpeng/Desktop/Low-Altitude/data/analyze/gold_emotion_nrc_combined.xlsx) |
| **NRC Included Words Table** | `data/analyze/nrc_words_included.xlsx` | Exported Excel table containing **358 words** covered by NRC (286 8-emotion + 72 polarity). | 👉 [`nrc_words_included.xlsx`](file:///Users/yuliangpeng/Desktop/Low-Altitude/data/analyze/nrc_words_included.xlsx) |
| **NRC Missed Words Table** | `data/analyze/nrc_words_missed.xlsx` | Exported Excel table containing **272 words** completely missed by NRC lexicon. | 👉 [`nrc_words_missed.xlsx`](file:///Users/yuliangpeng/Desktop/Low-Altitude/data/analyze/nrc_words_missed.xlsx) |
| **VADER-NRC Scatter Plot** | `data/analyze/master_gold_vader_nrc_scatter.png` | Scatter plot visualization mapping 630 Gold words across VADER valence vs. star ratings. | 👉 [`master_gold_vader_nrc_scatter.png`](file:///Users/yuliangpeng/Desktop/Low-Altitude/data/analyze/master_gold_vader_nrc_scatter.png) |

---

### 2. Step-by-Step Calculation Logic & Python Implementation

To obtain the exact numbers (**286**, **72**, **358**, and **272**), execute the audit script [`scratch/audit_gold_630_nrc_tree.py`](file:///Users/yuliangpeng/Desktop/Low-Altitude/scratch/audit_gold_630_nrc_tree.py):

```python
import pandas as pd
from nrclex import NRCLex

# 1. Load Master Gold Codebook (630 words)
df_gold = pd.read_csv("data/analyze/gold_emotion_master.csv")
nrc_dict = NRCLex().__lexicon__
NRC8 = {"anger", "anticipation", "disgust", "fear", "joy", "sadness", "surprise", "trust"}

# 2. Iterate through all 630 words using canonical_lemma mapping
cnt_8_emotion = 0
cnt_polarity_only = 0
cnt_missed = 0

for row in df_gold.itertuples():
    w = str(row.word).lower().strip()
    lemma = str(row.canonical_lemma).lower().strip()
    nrc_tags = nrc_dict.get(w, []) or nrc_dict.get(lemma, [])
    
    if len(set(nrc_tags) & NRC8) > 0:
        cnt_8_emotion += 1        # Category 1: Has at least 1 of 8 NRC emotions (286 words)
    elif len(nrc_tags) > 0:
        cnt_polarity_only += 1    # Category 2: Has NO 8 emotions, but has Positive/Negative (72 words)
    else:
        cnt_missed += 1           # Category 3: NOT in NRC lexicon at all (272 words)

cnt_covered_total = cnt_8_emotion + cnt_polarity_only  # Total Covered by NRC (358 words)
```

---

### 3. NRC Theoretical Framework Classification & Structural Breakdown ($N=630$ Words)

```text
Master Gold Emotion Codebook (N = 630 Words)
│
├── 1️⃣ Total Mapped into NRC Vocabulary Universe (在 NRC 词库里的总词数) ── 358 words (56.83%)
│   │
│   ├── 1a. Mapped to NRC 8-Emotion Categories ────────────────── 286 words (45.40%) ⭐ (Recommended)
│   │       (via Canonical Lemma Normalization, rescuing 17 inflected/typo words)
│   │
│   └── 1b. Mapped to Positive / Negative Polarity Only ──────── 72 words (11.43%)
│           (e.g., worth, interesting, cool, calm, fortunate, grateful, pristine)
│
└── 2️⃣ Completely MISSED by NRC Lexicon (不在 NRC 词库里的领域词) ────── 272 words (43.17%)
        (e.g., great, amazing, best, awesome, fantastic, incredible, breathtaking, stunning, awe)
```

$$\\text{Total NRC Vocabulary Coverage (358)} = 286 \\text{ (8-Emotions)} + 72 \\text{ (Polarity Only)}$$
$$\\text{Total Master Gold Codebook (630)} = 358 \\text{ (Total NRC Covered)} + 272 \\text{ (Completely Missed by NRC)}$$

---

### 4. Dual-Layer Matching Protocol: Raw Exact Match vs. Canonical Lemma Match

| Matching Protocol | NRC 8-Emotion Match Count | Only Polarity Count | Completely Missed Count | Total Codebook Universe | Methodological Takeaway |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Raw Exact Match (Unnormalized)** | 269 words (42.70%) | 72 words (11.43%) | 289 words (45.87%) | 630 words | Plurals (-s), past participles (-ed), and typos are lost as "unmapped". |
| **Canonical Lemma Match (Normalized)** ⭐ | **286 words (45.40%)** | **72 words (11.43%)** | **272 words (43.17%)** | **630 words** | **Rescues 17 true 8-emotion terms via lemma root mapping! (Recommended)** |

---

### 5. 17 Rescued Emotion Terms via Canonical Lemma Normalization

| Raw Token in Review (`word`) | Normalized Root Lemma (`canonical_lemma`) | Review Freq ($N=21,215$) | Rescued NRC 8-Emotion Categories | Why Raw String Matching Failed |
| :--- | :--- | :---: | :--- | :--- |
| **`worries`** | **`worry`** | 38 | `fear, anticipation, sadness` | Raw NRC misses plural *-es* suffix |
| **`surprises`** | **`surprise`** | 21 | `fear, joy, surprise` | Raw NRC misses plural *-s* suffix |
| **`cherished`** | **`cherish`** | 8 | `trust, anticipation, joy, surprise` | Raw NRC misses past participle *-ed* |
| **`hates`** | **`hate`** | 5 | `anger, fear, disgust, sadness` | Raw NRC misses verb inflection *-s* |
| **`hated`** | **`hate`** | 5 | `anger, fear, disgust, sadness` | Raw NRC misses past tense *-ed* |
| **`marveled`** | **`marvel`** | 5 | `surprise` | Raw NRC misses past tense *-ed* |
| **`dreaded`** | **`dread`** | 4 | `fear, anticipation` | Raw NRC misses participle *-ed* |
| **`dreading`** | **`dread`** | 4 | `fear, anticipation` | Raw NRC misses participle *-ing* |
| **`scaring`** | **`scare`** | 3 | `anger, fear, anticipation, surprise` | Raw NRC misses participle *-ing* |
| **`horribly`** | **`horrible`** | 3 | `anger, fear, disgust` | Raw NRC misses adverbial *-ly* |
| **`apprehensions`** | **`apprehension`** | 3 | `fear` | Raw NRC misses noun plural *-s* |
| **`suprise`** | **`surprise`** | 5 | `fear, joy, surprise` | Raw NRC misses typo variant (missing r) |
| **`suprised`** | **`surprised`** | 4 | `surprise` | Raw NRC misses typo variant |
| **`dissapointed`** | **`disappointed`** | 8 | `anger, disgust, sadness` | Raw NRC misses typo variant |
| **`aprehensive`** | **`apprehensive`** | 3 | `fear, anticipation` | Raw NRC misses typo variant |
| **`disappointingly`**| **`disappointed`** | 3 | `anger, disgust, sadness` | Raw NRC misses adverbial derivation |
| **`lucked`** | **`lucky`** | 86 | `joy, surprise` | Raw NRC misses verbalized inflection |

---

### 6. 4 Root Causes of Generic NRC Lexicon Gaps ($N=272$ Missed Words)

1. **Morphological & Participle Omissions (50.00% of Misses)**:
   - **Participle Forms (-ing / -ed)**: 78 words (28.68%), e.g., *amazing, loved, breathtaking, stunning, impressed, inspiring, relaxed, scared, thrilling*.
   - **Adverbs & Superlatives (-ly, -est, -er)**: 58 words (21.32%), e.g., *best (3,420), better (1,585), incredibly (315), perfectly (175), cheaper, smoother, safely*.
   - *Finding*: Generic NRC lexicons lack morphological derivation rules, causing massive loss of participle emotion adjectives.

2. **Omission of Modern Online Tourism Colloquial Superlatives (44.85% of Misses)**:
   - **Key Terms**: *great (11,541), awesome (2,530), fantastic (2,026), incredible (1,612), nice (1,794), fabulous, phenomenal, unbeatable, top-notch*.
   - *Deep Cause*: NRC 2012 seed vocabulary prioritized formal written English. Modern TripAdvisor reviewers rely heavily on colloquial high-arousal superlatives (*great, awesome, fantastic*), causing widespread generic lexicon failure in online review contexts.

3. **Absence of Low-Altitude Aerial Visual Awe & Aesthetic Emotions (3.31% of Misses)**:
   - **Key Terms**: *breathtaking (1,346), stunning (552), sublime (291), scenic (400), surreal (98), majestic, panoramic, spellbinding, mesmerizing, awe (304)*.
   - *Deep Cause*: Low-altitude air tourism is uniquely defined by **Aerial Visual Awe**, a domain-specific aesthetic emotion completely absent from generic news or conversational lexicons.

4. **Absence of Flight Perceived Risk & Somatic Symptoms (1.84% of Misses)**:
   - **Key Terms**: *claustrophobia, jitters, airsick, phobia, unnerving*.
   - *Deep Cause*: Flight vibration, confined cabin space, and altitude suspense trigger somatic anxiety and perceived risk reactions specific to aviation tourism.
"""

cn_stage2_rich = """## 📊 第二阶段：通用词典套入对比实验与 NRC 理论框架归类分析 (数据分析阶段)

在 **第二阶段数据分析**（主要在 `data/analyze/` 目录下完成）中，我们将定稿的 **630 个 Master 金标准情感实词** (`data/analyze/gold_emotion_master.csv`) 全量套入经典的 **NRC Emotion Lexicon v0.92**（包含 14,182 个官方词汇宇宙）中进行了对比映射与理论归类。

![NRC Gold Lexicon Distribution](figures/nrc_emotion_plots/nrc_mapping_gold_lexicon_distribution.png)

---

### 1. 第二阶段代码目录、审计脚本与导出文件直达链接

第二阶段的所有计算脚本、导出的 CSV/Excel 表格及绘图产物均严谨地存储于项目中：

| 核心文件与脚本名称 | 文件相对路径 | 脚本与文件的具体功能用途 | 直达链接 |
| :--- | :--- | :--- | :---: |
| **输入代码本主文件** | `data/analyze/gold_emotion_master.csv` | 包含全部 630 个 Master 金标准情感词及 `canonical_lemma` 映射的基础表。 | 👉 [`gold_emotion_master.csv`](file:///Users/yuliangpeng/Desktop/Low-Altitude/data/analyze/gold_emotion_master.csv) |
| **树状归类校验脚本** | `scratch/audit_gold_630_nrc_tree.py` | **核心可执行 Python 校验脚本**，运行即得出 286 / 72 / 358 / 272 精确数据。 | 👉 [`audit_gold_630_nrc_tree.py`](file:///Users/yuliangpeng/Desktop/Low-Altitude/scratch/audit_gold_630_nrc_tree.py) |
| **全量 NRC 归类合并表** | `data/analyze/gold_emotion_nrc_combined.xlsx` | 包含 630 个金标准词映射 NRC 8 大情绪及正负极性标签的全量合并表格。 | 👉 [`gold_emotion_nrc_combined.xlsx`](file:///Users/yuliangpeng/Desktop/Low-Altitude/data/analyze/gold_emotion_nrc_combined.xlsx) |
| **NRC 已收录词汇表** | `data/analyze/nrc_words_included.xlsx` | 导出的 NRC 覆盖的 **358 个词汇表**（包含 286 个 8-Emotion 词 + 72 个极性词）。 | 👉 [`nrc_words_included.xlsx`](file:///Users/yuliangpeng/Desktop/Low-Altitude/data/analyze/nrc_words_included.xlsx) |
| **NRC 彻底遗漏词汇表** | `data/analyze/nrc_words_missed.xlsx` | 导出的 NRC 彻底遗漏的 **272 个领域专属情感词表**（按词频排序）。 | 👉 [`nrc_words_missed.xlsx`](file:///Users/yuliangpeng/Desktop/Low-Altitude/data/analyze/nrc_words_missed.xlsx) |
| **VADER-NRC 散点图** | `data/analyze/master_gold_vader_nrc_scatter.png` | 630 个金标准词在 VADER 情感极性与游客星级评分维度下的学术散点图。 | 👉 [`master_gold_vader_nrc_scatter.png`](file:///Users/yuliangpeng/Desktop/Low-Altitude/data/analyze/master_gold_vader_nrc_scatter.png) |

---

### 2. 计算步骤、Python 代码实现与复现命令

运行脚本 [`scratch/audit_gold_630_nrc_tree.py`](file:///Users/yuliangpeng/Desktop/Low-Altitude/scratch/audit_gold_630_nrc_tree.py) 可一步直接复现核心数据：

```python
import pandas as pd
from nrclex import NRCLex

# 1. 加载 630 个 Master 金标准情感代码本
df_gold = pd.read_csv("data/analyze/gold_emotion_master.csv")
nrc_dict = NRCLex().__lexicon__
NRC8 = {"anger", "anticipation", "disgust", "fear", "joy", "sadness", "surprise", "trust"}

cnt_8_emotion = 0
cnt_polarity_only = 0
cnt_missed = 0

# 2. 遍历 630 个词，结合 canonical_lemma 进行映射计算
for row in df_gold.itertuples():
    w = str(row.word).lower().strip()
    lemma = str(row.canonical_lemma).lower().strip()
    nrc_tags = nrc_dict.get(w, []) or nrc_dict.get(lemma, [])
    
    if len(set(nrc_tags) & NRC8) > 0:
        cnt_8_emotion += 1        # 类别 1: 包含 NRC 8 大情绪至少一种 -> 286 个词 (45.40%)
    elif len(nrc_tags) > 0:
        cnt_polarity_only += 1    # 类别 2: 无 8 大情绪，但包含正负极性 -> 72 个词 (11.43%)
    else:
        cnt_missed += 1           # 类别 3: 完全不在 NRC 词库中 -> 272 个词 (43.17%)

cnt_covered_total = cnt_8_emotion + cnt_polarity_only  # NRC 词库收录总数 -> 358 个词 (56.83%)
```

---

### 3. NRC 理论框架归类分析与结构分布 ($N=630$ 个金标准词)

```text
Master 金标准情感代码本 (全量 N = 630 个词)
│
├── 1️⃣ 能够在 NRC 词库中找到的总词数 (Covered in NRC Vocabulary) ──── 358 词 (56.83%)
│   │
│   ├── 1a. 能够映射到 8 大 Emotion 情绪分类的词 ──────────────── 286 词 (45.40%) ⭐ (推荐使用)
│   │       (如: beautiful, friendly, wonderful, happy, nervous, disappointed)
│   │
│   └── 1b. 只有 Positive / Negative 极性标记的词 ────────────── 72 词 (11.43%)
│           (如: worth, interesting, cool, calm, fortunate, grateful, pristine)
│
└── 2️⃣ 完全不在 NRC 词库里的领域专属词 (Completely Missed by NRC) ────── 272 词 (43.17%)
        (如: great, amazing, best, awesome, fantastic, incredible, breathtaking, stunning, awe)
```

$$\\text{NRC 词库收录总数 (358)} = 286 \\text{ (8大情绪)} + 72 \\text{ (仅正负极性)}$$
$$\\text{全量金标准代码本 (630)} = 358 \\text{ (NRC 收录总数)} + 272 \\text{ (都不在 NRC)}$$

---

### 4. 双层匹配代码逻辑：原始字符串匹配 (Raw Match) vs. 词根归一化匹配 (Canonical Lemma Match)

| 匹配协议维度 | NRC 8 大情绪匹配词数 | 仅正负极性词数 | 彻底遗漏词数 | 代码本总词数 | 方法论对比结论 |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **原始字符串匹配 (Raw Exact Match)** | 269 个词 (42.70%) | 72 个词 (11.43%) | 289 个词 (45.87%) | 630 个词 | 错别字、动词过去式与复数变体被误判为“未识别” |
| **词根归一化匹配 (Canonical Lemma Match)** ⭐ | **286 个词 (45.40%)** | **72 个词 (11.43%)** | **272 个词 (43.17%)** | **630 个词** | **【推荐使用！】通过词根映射成功救回 17 个真实 8 大情绪词！** |

---

### 5. 通过 `canonical_lemma` 词根归一化协议救回的 17 个核心情感词

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

### 6. NRC 通用词典发生遗漏的 4 大根本原因审定 ($N=272$ 个遗漏词)

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

### 7. Master 金标准代码本 VADER 极性 vs. 游客星级散点图 (0.0 to 5.0 Stars)

![Master Gold VADER NRC Scatter Plot](data/analyze/master_gold_vader_nrc_scatter.png)
"""

start_r = readme_text.find("## 📊 Stage 2: Generic Lexicon Audit")
end_r = readme_text.find("## 📈 Summary Data & Empirical Metrics Ledger")

if start_r != -1 and end_r != -1:
    readme_text = readme_text[:start_r] + readme_stage2_rich + "\n\n" + readme_text[end_r:]
    readme_path.write_text(readme_text, encoding="utf-8")
    print("Successfully enriched Stage 2 details in README.md!")

start_cn = cn_text.find("## 📊 第二阶段：通用词典套入对比实验")
end_cn = cn_text.find("## 📈 四、 步骤 6：N-Gram 挖掘与学术图表产出")

if start_cn != -1 and end_cn != -1:
    cn_text = cn_text[:start_cn] + cn_stage2_rich + "\n\n" + cn_text[end_cn:]
    cn_path.write_text(cn_text, encoding="utf-8")
    print("Successfully enriched Stage 2 details in RESEARCH_NOTES_CN.md!")

# Re-generate Chinese PDF report
res_pdf = subprocess.run(["python3", "scratch/generate_pdf_report.py"], capture_output=True, text=True)
print(res_pdf.stdout.strip())
