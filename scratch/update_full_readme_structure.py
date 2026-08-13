#!/usr/bin/env python3
"""Rewrite README.md and RESEARCH_NOTES_CN.md to seamlessly connect 3-Stage Lexicon Induction (500->2500->Final) with Canonical Lemma NRC Audit & Code Logic."""

from pathlib import Path
import subprocess

readme_path = Path("README.md")
cn_path = Path("RESEARCH_NOTES_CN.md")

nrc_section_en = """
### 📊 7. NRC Lexicon Mapping & Comparative Audit ($N=630$ Words)

To validate the theoretical superiority of our **Corpus-Derived Gold Emotion Lexicon** over generic off-the-shelf lexicons, we mapped all **630 Master Gold Emotion Terms** against the **NRC Emotion Lexicon** (Mohammad & Turney):

![NRC Gold Lexicon Distribution](figures/nrc_emotion_plots/nrc_mapping_gold_lexicon_distribution.png)

#### 🔬 Dual-Layer Matching Protocol: Raw Exact Match vs. Canonical Lemma Match

In generic NLP pipelines, matching raw unnormalized words against static dictionaries leads to severe misclassification due to plurals, verb inflections, and typos. We compared **Raw String Matching** against our **Canonical Lemma Normalization Protocol**:

```python
import pandas as pd
from nrclex import NRCLex

# Load 630 Master Gold Emotion Codebook
df_gold = pd.read_csv("data/analyze/gold_emotion_master.csv")
nrc_dict = NRCLex().__lexicon__
NRC8 = {"anger", "anticipation", "disgust", "fear", "joy", "sadness", "surprise", "trust"}

# 1. Raw Exact String Match (Unnormalized)
raw_8 = sum(1 for row in df_gold.itertuples() if len(set(nrc_dict.get(str(row.word).lower().strip(), [])) & NRC8) > 0)

# 2. Canonical Lemma Match (Normalized via canonical_lemma)
lemma_8 = sum(1 for row in df_gold.itertuples() if len(set(nrc_dict.get(str(row.canonical_lemma).lower().strip(), [])) & NRC8) > 0 or len(set(nrc_dict.get(str(row.word).lower().strip(), [])) & NRC8) > 0)
```

| Matching Protocol | NRC 8-Emotion Match Count | Only Polarity Count | Completely Missed Count | Total Codebook Universe | Key Methodological Takeaway |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Raw Exact Match (Unnormalized)** | 269 words (42.70%) | 72 words (11.43%) | 289 words (45.87%) | 630 words | Plurals (-s), past participles (-ed), and typos are lost as "unmapped". |
| **Canonical Lemma Match (Normalized)** ⭐ | **286 words (45.40%)** | **72 words (11.43%)** | **272 words (43.17%)** | **630 words** | **Rescues 17 true 8-emotion terms via lemma root mapping! (Recommended)** |

$$\\text{Total Master Gold Codebook (630)} = 286 \\text{ (8-Emotions)} + 72 \\text{ (Polarity Only)} + 272 \\text{ (NRC Misses)}$$

---

#### 💡 17 Rescued Emotion Terms via Canonical Lemma Normalization

By instituting our **Canonical Lemma Normalization Protocol**, 17 inflected plurals, past participles, and typo variants were mapped back to their dictionary root lemmas, successfully recovering their 8-emotion tags:

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

#### 🔍 4 Root Causes of NRC Generic Lexicon Gaps ($N=272$ Missed Words):

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

nrc_section_cn = """
### 📊 八、 NRC 情感词典套入对比实验、双层匹配代码逻辑与 4 大归因审定 (N=630 个金标准词)

为实证验证本项目自建的**语料库推导金标准情感代码本**相较于传统通用词典（如 NRC Emotion Lexicon）的学术优越性，我们将 **630 个 Master 金标准情感实词** 全量套入 **NRC 词典**（Mohammad & Turney）进行映射与对比：

![NRC Gold Lexicon Distribution](figures/nrc_emotion_plots/nrc_mapping_gold_lexicon_distribution.png)

#### 🔬 双层匹配协议：原始字符串匹配 (Raw Match) vs. 词根归一化匹配 (Canonical Lemma Match)

在传统 NLP 处理流程中，如果不进行形态归一化直接用原始单词比对词典，会导致大量复数、过去分词与错别字变体被误判为“未识别”。我们设计了**双层匹配对照代码逻辑**：

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

$$\\text{全量金标准代码本 (630)} = 286 \\text{ (8大情绪)} + 72 \\text{ (仅正负极性)} + 272 \\text{ (都不在 NRC)}$$

---

#### 💡 通过 `canonical_lemma` 词根归一化协议救回的 17 个核心情感词：

通过建立 **`canonical_lemma` 词根归一化协议**，我们将 17 个复数变体、过去分词与错别字变体成功还原映射回字典词根，把这 17 个原本会被原始字符串匹配漏掉的 8 大情绪标签完整救了回来：

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

#### 🔍 NRC 通用词典发生遗漏的 4 大根本原因审定 ($N=272$ 个遗漏词)：

1. **原因 1：静态词典对现代语法形态变体（Morphological Variants）补全严重不足 (占比 50.00%)**：
   - **分词形式 (-ing / -ed)**：78 个词 (28.68%)。NRC 词典构建于 2012 年，主要收集基础动词/名词词根（如收录了 *amaze*），但对游客在评论中大量使用的过去分词与现在分词（如 *amazing, loved, breathtaking, stunning, impressed, inspiring, relaxed, scared, thrilling*）完全没有做变体映射！
   - **副词与比较级/最高级 (-ly, -est, -er)**：58 个词 (21.32%)。如 *best (3,420次), better (1,585次), incredibly (315次), perfectly (175次), cheaper, smoother, safely, regrettably*。
   - **论文结论**：传统 NRC 词典的词汇库缺乏形态学归一化机制，导致大批衍生情感形容词被漏掉。

2. **原因 2：NRC 原始种子词缺乏现代网络旅游的高频口语赞誉词 (占比 44.85%)**：
   - **典型词汇**：*great (11,541 次)、awesome (2,530 次)、fantastic (2,026 次)、incredible (1,612 次)、nice (1,794 次)、fabulous, phenomenal, unbeatable, top-notch*.
   - **深层原因**：NRC 在 2012 年使用 Amazon Mechanical Turk 众包标注时，选用的种子词表偏向传统正式书面语（通用大英词典选词）。而 TripAdvisor 上的现代游客在表达满意时，极其倾向于使用这些现代口语高唤起赞誉词（*great, awesome, fantastic*），导致 NRC 在现代在线评论场景中发生大规模失效！

3. **原因 3：通用词典缺失“低空高空视觉震撼与美学惊叹（Aerial Visual Awe）”领域词 (占比 3.31%)**：
   - **典型词汇**：*breathtaking (1,346 次)、stunning (552 次)、sublime (291 次)、scenic (400次), surreal (98次), majestic, panoramic, spellbinding, mesmerizing, awe (304次)*.
   - **深层原因**：低空观光旅游（直升机/水上飞机/观光飞行）的核心体验是**“空中俯瞰带来的高唤起美学惊叹与视觉冲击（Awe / Aesthetic Emotion）”**。这种情感极其专一且高度依赖特定场景（景致宏大、冰川大峡谷高空视角），在通用新闻或日常对话文本中出现频率低，因此通用 NRC 词典完全没有针对该维度进行设计。

4. **原因 4：低空飞行感知风险与身体/心理躯体化症状词 (占比 1.84%)**：
   - **典型词汇**：*claustrophobia (幽闭恐惧)、jitters (忐忑颤抖)、airsick (晕机)、phobia (恐高症)、unnerving (让人发慌)*.
   - **深层原因**：颠簸（turbulence）、密闭舱室与高空悬浮会引发游客独特的感知风险（Perceived Risk）与躯体化焦虑反应。这些词汇专属于低空飞行场景，通用情感词典无法捕捉此类垂直行业的特定生理/心理症状表达。
"""

readme_text = readme_path.read_text(encoding="utf-8")
cn_text = cn_path.read_text(encoding="utf-8")

# Replace Section 7 in README
start_idx_r = readme_text.find("### 📊 7. NRC Lexicon Mapping")
if start_idx_r != -1:
    readme_text = readme_text[:start_idx_r] + nrc_section_en
else:
    readme_text += "\n" + nrc_section_en

# Replace Section 8 in CN notes
start_idx_cn = cn_text.find("### 📊 八、 NRC 情感词典套入对比实验")
if start_idx_cn != -1:
    cn_text = cn_text[:start_idx_cn] + nrc_section_cn
else:
    cn_text += "\n" + nrc_section_cn

readme_path.write_text(readme_text, encoding="utf-8")
cn_path.write_text(cn_text, encoding="utf-8")

print("Successfully updated README.md and RESEARCH_NOTES_CN.md with complete dual-layer matching, python code blocks, tables, and 4 root causes!")

# Re-generate Chinese PDF report
res_pdf = subprocess.run(["python3", "scratch/generate_pdf_report.py"], capture_output=True, text=True)
print(res_pdf.stdout.strip())
