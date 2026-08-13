#!/usr/bin/env python3
"""Update README.md and RESEARCH_NOTES_CN.md to group Cause 3 & Cause 4 under Domain-Specific Low-Altitude Air Tourism Lexicon."""

from pathlib import Path

readme_path = Path("README.md")
cn_path = Path("RESEARCH_NOTES_CN.md")

readme_text = readme_path.read_text(encoding="utf-8")
cn_text = cn_path.read_text(encoding="utf-8")

causes_taxonomy_en = """### 6. 4 Root Causes of Generic Lexicon Gaps ($N=272$ Missed Words)

All **272 missed words** are systematically structured into a two-tier academic taxonomy:

#### 🔷 Tier 1: Generic Lexicon Technical & Coverage Failures (50.00% + 44.85%)
1. **Morphological & Participle Derivation Gaps (Pure Morphological Variants)**:
   - **Participle Forms (-ing / -ed)**: e.g., *loved (1,473), impressed (255), inspiring (210), relaxed (159), scared (144), amazed (120), thrilled (113), reassuring (97)*.
   - **Adverbs & Superlatives (-ly, -est, -er)**: e.g., *better (1,585), cheaper (208), perfectly (155), smoother (143), safely (132), smoothest (105), luckily (96)*.
   - **Empirical Validation**: Among 127 pure morphological words, **48.82% (62 words) have base dictionary roots already present in NRC**, but static string matching omits **88.7% (15,581 review mentions)** of high-frequency emotional expressions.

2. **Omission of Modern Online Tourism Colloquial Superlatives (Web 2.0 UGC Seed Gap)**:
   - **Key Terms**: *great (11,541), awesome (2,530), fantastic (2,026), nice (1,794), incredible (1,612), comfortable (1,446), fabulous (508), enjoyable (460), unforgettable (459), funny (301), phenomenal (200)*.
   - **Empirical Validation**: Even after 100% Lemmatization root mapping, top colloquial terms such as `great`, `awesome`, and `fantastic` remain 100% ABSENT from NRC. **10 top colloquial superlatives account for 20,549 mentions (73.2% of Cause 2 frequency, and 42.08% of total missed review frequency)**.

---

#### 🔶 Tier 2: Domain-Specific Low-Altitude Air Tourism Lexicon (低空观光旅游垂直领域特有词汇)
3. **Absence of Low-Altitude Aerial Visual Awe & Aesthetic Emotions (Aerial Awe Dimension, 3.31% of Misses)**:
   - **Key Terms**: *breathtaking (1,346), stunning (552), scenic (400), awe (304), surreal (98), breathtakingly (30), mesmerizing (26), awed (15), sublime (6), spellbinding (4)*.
   - **Empirical Validation**: All 11 awe terms have **0 tags in NRC (100% unmapped)**, omitting **2,791 review mentions**. Aerial visual perspectives trigger high-arousal aesthetic awe absent from generic conversational corpora.

4. **Absence of Flight Perceived Risk & Somatic Symptoms (Somatic Flight Risk Dimension, 1.84% of Misses)**:
   - **Key Terms**: *airsick (33), claustrophobic (16), claustrophobia (9), jitters (5), unnerving (4), phobia (4)*.
   - **Empirical Validation**: All 6 flight risk terms have **0 tags in NRC (100% unmapped)**, omitting **71 review mentions**. Altitude suspense, flight vibration, and confined cabin space induce somatic anxiety reactions specific to aviation tourism."""

causes_taxonomy_cn = """### 6. NRC 通用词典发生遗漏的 4 大归因审定 ($N=272$ 个遗漏词)

为了保证学术分类的严谨性，全量 **272 个遗漏词** 被系统构建为双层学术归因架构：

#### 🔷 第一层：通用词典技术与覆盖性失灵 (Generic Lexicon Technical Failures)
1. **归因 1：纯粹语法形态与分词变体补全不足 (Morphological Variants, 占比 50.00%)**：
   - **分词形式 (-ing / -ed)**：如 *loved (1,473次), impressed (255次), inspiring (210次), relaxed (159次), scared (144次), amazed (120次), thrilled (113次), reassuring (97次)*。
   - **副词与比较级/最高级 (-ly, -est, -er)**：如 *better (1,585次), cheaper (208次), perfectly (155次), smoother (143次), safely (132次), smoothest (105次), luckily (96次)*。
   - **词根验证与实证发现**：在 127 个纯形态变体词中，**48.82%（62 个词）的底层词根实际上在 NRC 中已有收录**。由于缺乏形态学还原规则，导致评论语料中 **88.7%（累计 15,581 次）的高频情感提及未能被有效匹配捕捉**。

2. **归因 2：NRC 原始种子词缺乏现代网络旅游的高频口语赞誉与基础词汇 (Web 2.0 UGC Gap, 占比 44.85%)**：
   - **典型词汇**：*great (11,541次)、awesome (2,530次)、fantastic (2,026次)、nice (1,794次)、incredible (1,612次)、comfortable (1,446次)、fabulous (508次)、unforgettable (459次)、enjoyable (460次)*。
   - **帕累托二八定律验证**：与归因 1 不同，归因 2 代表了词汇库的绝对缺口。即使做 100% 词根还原，`great, awesome, fantastic` 等词在 NRC 中依然 100% 完全缺失。前 10 个头部口语赞美词独自贡献了 **20,549 次提及（占据归因 2 频次的 73.2%，以及全量遗漏语料频次的 42.08%）**。

---

#### 🔶 第二层：低空观光旅游垂直领域特有词汇 (Domain-Specific Low-Altitude Tourism Lexicon)
3. **归因 3：低空高空视觉震撼与美学惊叹领域词 (Aerial Visual Awe Dimension, 占比 3.31%)**：
   - **典型词汇**：*breathtaking (1,346次)、stunning (552次)、scenic (400次)、awe (304次)、surreal (98次)、breathtakingly (30次)、mesmerizing (26次)、awed (15次)、sublime (6次)、spellbinding (4次)*。
   - **实证验证**：11 个美学震撼词在 NRC 中 **100% 未被收录（标签全为 0）**，导致 **2,791 次高空美学表达遗漏**。空中俯瞰引发的高唤起美学惊叹（Aesthetic Emotion）依赖特定场景，通用对话语料完全未设计该维度。

4. **归因 4：低空飞行感知风险与身体/心理躯体化症状词 (Somatic Flight Risk Dimension, 占比 1.84%)**：
   - **典型词汇**：*airsick (33次，晕机躯体症状)、claustrophobic (16次)、claustrophobia (9次，密闭舱室幽闭恐惧)、jitters (5次，飞行前紧张抖抖)、unnerving (4次，心理发慌不安)、phobia (4次，恐高症)*。
   - **实证验证**：6 个飞行感知风险词在 NRC 中 **100% 未被收录（标签全为 0）**，导致 **71 次垂直风险表述遗漏**。机舱密闭、气流颠簸与高空悬浮诱发的躯体化焦虑反应为低空观光所特有。"""

start_r = readme_text.find("### 6. 4 Root Causes of Generic Lexicon Gaps")
end_r = readme_text.find("### 5. Master Gold Emotion Lexicon Scatter Plot")
if end_r == -1:
    end_r = readme_text.find("## 📈 Summary Data & Empirical Metrics Ledger")

if start_r != -1 and end_r != -1:
    readme_text = readme_text[:start_r] + causes_taxonomy_en + "\n\n" + readme_text[end_r:]
    readme_path.write_text(readme_text, encoding="utf-8")
    print("Successfully updated taxonomy in README.md!")

start_cn = cn_text.find("### 6. NRC 通用词典发生遗漏的 4 大归因审定")
end_cn = cn_text.find("### 5. Master 金标准代码本 VADER 极性")
if end_cn == -1:
    end_cn = cn_text.find("## 📈 四、 步骤 6：N-Gram 挖掘与学术图表产出")

if start_cn != -1 and end_cn != -1:
    cn_text = cn_text[:start_cn] + causes_taxonomy_cn + "\n\n" + cn_text[end_cn:]
    cn_path.write_text(cn_text, encoding="utf-8")
    print("Successfully updated taxonomy in RESEARCH_NOTES_CN.md!")
