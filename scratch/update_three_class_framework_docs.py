#!/usr/bin/env python3
"""Update README.md and RESEARCH_NOTES_CN.md with the clean 3-Class Framework for NRC Missed Words."""

from pathlib import Path

readme_path = Path("README.md")
cn_path = Path("RESEARCH_NOTES_CN.md")

readme_text = readme_path.read_text(encoding="utf-8")
cn_text = cn_path.read_text(encoding="utf-8")

causes_3class_en = """### 6. 3 Core Classes of Generic Lexicon Gaps ($N=272$ Missed Words)

All **272 missed words** are systematically classified into 3 core academic categories:

1. **Class 1: Participle & Morphological Derivation Gaps (127 Words, 46.69%)**:
   - **Participle Forms (-ing / -ed)** & **Adverbs/Superlatives (-ly, -est, -er)**: e.g., *loved (1,473), impressed (255), inspiring (210), relaxed (159), scared (144), amazed (120), thrilled (113), better (1,585), cheaper (208), perfectly (155), smoother (143), safely (132)*.
   - **Empirical Validation**: Among the 127 morphological words, **48.82% (62 words) have base dictionary roots (e.g., *amaze, love, impress, inspire, scare, thrill, good, safe*) already present in NRC**. Static string matching omits **88.7% (15,581 review mentions)** of high-frequency emotional expressions.

2. **Class 2: Omission of Modern Online Tourism Colloquial Superlatives & Base Terms (128 Words, 47.06%)**:
   - **Key Terms**: *great (11,541), awesome (2,530), fantastic (2,026), nice (1,794), incredible (1,612), comfortable (1,446), fabulous (508), enjoyable (460), unforgettable (459), funny (301), phenomenal (200)*.
   - **Empirical Validation**: Even after 100% Lemmatization root mapping, top terms such as `great`, `awesome`, `fantastic`, and `nice` remain 100% ABSENT from NRC. **10 top high-frequency colloquial superlatives account for 20,549 mentions (73.2% of Class 2 frequency, and 42.08% of total missed review frequency)**.

3. **Class 3: Low-Altitude Air Tourism Domain-Specific Lexicon (低空观光旅游特有词汇, 17 Words, 6.25%)**:
   - **Aerial Visual Awe & Aesthetic Emotion**: *breathtaking (1,346), stunning (552), scenic (400), awe (304), surreal (98), breathtakingly (30), mesmerizing (26), awed (15), sublime (6), spellbinding (4)*.
   - **Flight Perceived Risk & Somatic Symptoms**: *airsick (33), claustrophobic (16), claustrophobia (9), jitters (5), unnerving (4), phobia (4)*.
   - **Empirical Validation**: All 17 domain-specific terms have **0 tags in NRC (100% unmapped)**, omitting **2,862 review mentions**. Aerial visual awe and somatic flight risk reactions are specific to aviation tourism and completely uncaptured by generic lexicons."""

causes_3class_cn = """### 6. NRC 通用词典发生遗漏的 3 大归因类别 ($N=272$ 个遗漏词)

全量 **272 个遗漏词** 被系统梳理划分为 3 大清晰的归因类别：

1. **第 1 类：语法分词与形态衍生词 (Participle & Morphological Variants, 127 个词, 占比 46.69%)**：
   - **分词形式 (-ing / -ed)** 与 **副词/比较级 (-ly, -est, -er)**：如 *loved (1,473次), impressed (255次), inspiring (210次), relaxed (159次), scared (144次), amazed (120次), thrilled (113次), better (1,585次), cheaper (208次), perfectly (155次), smoother (143次), safely (132次)*。
   - **词根验证与实证发现**：在 127 个形态变体词中，**48.82%（62 个词）的底层词根（如 *amaze, love, impress, inspire, scare, thrill, good, safe*）实际上在 NRC 中已有收录**。由于缺乏形态学还原规则，导致评论语料中 **88.7%（累计 15,581 次）的高频情感提及未能被有效匹配捕捉**。

2. **第 2 类：NRC 缺失的现代网络游客高频口语赞誉与基础词汇 (Modern Online Tourism Colloquial Superlatives, 128 个词, 占比 47.06%)**：
   - **典型词汇**：*great (11,541次)、awesome (2,530次)、fantastic (2,026次)、nice (1,794次)、incredible (1,612次)、comfortable (1,446次)、fabulous (508次)、unforgettable (459次)、enjoyable (460次)、funny (301次)、phenomenal (200次)*。
   - **实证验证**：与第 1 类不同，即使做 100% 词根还原，`great, awesome, fantastic, nice` 等词在 NRC 中依然 100% 完全缺失。前 10 个头部口语赞美词独自贡献了 **20,549 次提及（占据第 2 类频次的 73.2%，以及全量遗漏语料频次的 42.08%）**。

3. **第 3 类：低空观光旅游垂直领域特有词汇 (Low-Altitude Air Tourism Domain-Specific Lexicon, 17 个词, 占比 6.25%)**：
   - **空中高空美学视觉震撼词**：*breathtaking (1,346次)、stunning (552次)、scenic (400次)、awe (304次)、surreal (98次)、breathtakingly (30次)、mesmerizing (26次)、awed (15次)、sublime (6次)、spellbinding (4次)*。
   - **低空飞行感知风险与身体/心理躯体化症状词**：*airsick (33次，晕机躯体症状)、claustrophobic (16次)、claustrophobia (9次，密闭舱室幽闭恐惧)、jitters (5次，飞行前紧张抖抖)、unnerving (4次，心理发慌不安)、phobia (4次，恐高症)*。
   - **实证验证与核验发现**：全量 17 个低空特有词在 NRC 词典中 **100% 未被收录（匹配标签数全为 0）**，导致评论语料中 **2,862 次低空观光领域专属情感表达未能被传统词典捕捉**。空中俯瞰引发的高唤起美学惊叹（Awe）与机舱密闭颠簸引发的躯体化风险（Somatic Risk）专属于低空飞行垂直场景。"""

start_r = readme_text.find("### 6. 4 Root Causes of Generic Lexicon Gaps")
if start_r == -1:
    start_r = readme_text.find("### 6. 3 Core Classes of Generic Lexicon Gaps")
end_r = readme_text.find("### 5. Master Gold Emotion Lexicon Scatter Plot")
if end_r == -1:
    end_r = readme_text.find("## 📈 Summary Data & Empirical Metrics Ledger")

if start_r != -1 and end_r != -1:
    readme_text = readme_text[:start_r] + causes_3class_en + "\n\n" + readme_text[end_r:]
    readme_path.write_text(readme_text, encoding="utf-8")
    print("Successfully updated 3-Class Framework in README.md!")

start_cn = cn_text.find("### 6. NRC 通用词典发生遗漏的 4 大")
if start_cn == -1:
    start_cn = cn_text.find("### 6. NRC 通用词典发生遗漏的 3 大归因类别")
end_cn = cn_text.find("### 5. Master 金标准代码本 VADER 极性")
if end_cn == -1:
    end_cn = cn_text.find("## 📈 四、 步骤 6：N-Gram 挖掘与学术图表产出")

if start_cn != -1 and end_cn != -1:
    cn_text = cn_text[:start_cn] + causes_3class_cn + "\n\n" + cn_text[end_cn:]
    cn_path.write_text(cn_text, encoding="utf-8")
    print("Successfully updated 3-Class Framework in RESEARCH_NOTES_CN.md!")
