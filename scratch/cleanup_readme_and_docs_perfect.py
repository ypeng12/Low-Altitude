#!/usr/bin/env python3
"""Cleanup README.md, RESEARCH_NOTES_CN.md, and RESEARCH_NOTES.md: remove 17 Rescued table & duplicates, enhance Class 1, 2, 3 details."""

from pathlib import Path

readme_path = Path("README.md")
cn_path = Path("RESEARCH_NOTES_CN.md")
en_path = Path("RESEARCH_NOTES.md")

readme_text = readme_path.read_text(encoding="utf-8")
cn_text = cn_path.read_text(encoding="utf-8")
en_text = en_path.read_text(encoding="utf-8")

# 1. Clean README.md: remove everything after Section 6, remove 17 Rescued Table, make Class 1, 2, 3 super clean and detailed.
class3_section_en = """### 6. 3 Core Classes of Generic Lexicon Gaps ($N=272$ Missed Words)

All **272 missed words** are systematically classified into 3 core academic categories:

1. **Class 1: Participle & Morphological Derivation Gaps (127 Words, 46.69%)**:
   - **Participle Forms (-ing / -ed)** & **Adverbs/Superlatives (-ly, -est, -er)**: e.g., *loved (1,473), impressed (255), inspiring (210), relaxed (159), scared (144), amazed (120), thrilled (113), better (1,585), cheaper (208), perfectly (155), smoother (143), safely (132)*.
   - **Empirical Validation**: Among the 127 pure morphological words, **48.82% (62 words) have base dictionary roots (e.g., *amaze, love, impress, inspire, scare, thrill, good, safe*) already present in NRC**. However, static string matching fails to capture them, omitting **88.7% (15,581 review mentions)** of high-frequency emotional expressions.
   - *Deep Cause & Finding*: Generic NRC lexicons lack morphological derivation rules, causing significant classification omissions.

2. **Class 2: Omission of Modern Online Tourism Colloquial Superlatives & Base Terms (128 Words, 47.06%)**:
   - **Key Terms**: *great (11,541), awesome (2,530), fantastic (2,026), nice (1,794), incredible (1,612), comfortable (1,446), fabulous (508), enjoyable (460), unforgettable (459), funny (301), phenomenal (200)*.
   - **Empirical Validation**: Even after 100% Lemmatization root mapping, top terms such as `great`, `awesome`, `fantastic`, and `nice` remain 100% ABSENT from NRC. **10 top high-frequency colloquial superlatives account for 20,549 mentions (73.2% of Class 2 frequency, and 42.08% of total missed review frequency)**.
   - *Deep Cause & Finding*: NRC 2012 seed vocabulary prioritized formal written English corpora. Modern TripAdvisor reviewers rely heavily on colloquial high-arousal superlatives (*great, awesome, fantastic*), causing widespread generic lexicon failure in Web 2.0 online review contexts.

3. **Class 3: Low-Altitude Air Tourism Domain-Specific Lexicon (低空观光旅游特有词汇, 17 Words, 6.25%)**:
   - **Sub-dimension A: Low-Altitude Aerial Visual Awe & Aesthetic Emotions (Domain Awe Gap)**:
     - **Key Terms**: *breathtaking (1,346), stunning (552), scenic (400), awe (304), surreal (98), breathtakingly (30), mesmerizing (26), awed (15), sublime (6), spellbinding (4)*.
     - **Empirical Validation**: All 11 awe terms have **0 tags in NRC (100% unmapped)**, omitting **2,791 review mentions**.
     - **Deep Cause & Finding**: Low-altitude air tourism is uniquely defined by Aerial Visual Awe, a domain-specific aesthetic emotion completely absent from generic news or conversational lexicons.
   - **Sub-dimension B: Flight Perceived Risk & Somatic Symptoms (Aviation Risk Gap)**:
     - **Key Terms**: *airsick (33), claustrophobic (16), claustrophobia (9), jitters (5), unnerving (4), phobia (4)*.
     - **Empirical Validation**: All 6 flight risk terms have **0 tags in NRC (100% unmapped)**, omitting **71 review mentions**.
     - **Deep Cause & Finding**: Flight vibration, confined cabin space, and altitude suspense trigger somatic anxiety and perceived risk reactions specific to aviation tourism that generic sentiment dictionaries fail to capture."""

class3_section_cn = """### 6. NRC 通用词典发生遗漏的 3 大归因类别 ($N=272$ 个遗漏词)

全量 **272 个遗漏词** 被系统梳理划分为 3 大清晰的归因类别：

1. **第 1 类：语法分词与形态衍生词 (Participle & Morphological Variants, 127 个词, 占比 46.69%)**：
   - **分词形式 (-ing / -ed)** 与 **副词/比较级 (-ly, -est, -er)**：如 *loved (1,473次), impressed (255次), inspiring (210次), relaxed (159次), scared (144次), amazed (120次), thrilled (113次), better (1,585次), cheaper (208次), perfectly (155次), smoother (143次), safely (132次)*。
   - **实证验证与核验发现**：在 127 个形态变体词中，**48.82%（62 个词）的底层词根（如 *amaze, love, impress, inspire, scare, thrill, good, safe*）实际上在 NRC 中已有收录**。由于缺乏形态学还原规则，导致评论语料中 **88.7%（累计 15,581 次）的高频情感提及未能被有效匹配捕捉**。
   - **深层原因与学术结论**：通用 NRC 词典缺乏形态学归一化机制（Morphological Normalization），引发了显著的词汇提取偏误。

2. **第 2 类：NRC 缺失的现代网络游客高频口语赞誉与基础词汇 (Modern Online Tourism Colloquial Superlatives, 128 个词, 占比 47.06%)**：
   - **典型词汇**：*great (11,541次)、awesome (2,530次)、fantastic (2,026次)、nice (1,794次)、incredible (1,612次)、comfortable (1,446次)、fabulous (508次)、unforgettable (459次)、enjoyable (460次)、funny (301次)、phenomenal (200次)*。
   - **实证验证与核验发现**：与第 1 类不同，即使做 100% 词根还原，`great, awesome, fantastic, nice` 等词在 NRC 中依然 100% 完全缺失。前 10 个头部口语赞美词独自贡献了 **20,549 次提及（占据第 2 类频次的 73.2%，以及全量遗漏语料频次的 42.08%）**。
   - **深层原因与学术结论**：NRC 选词偏向传统正式书面语，而 TripAdvisor 上的现代游客极其倾向于使用现代口语高唤起赞誉词，揭示了传统通用词典在 Web 2.0 用户生成内容（UGC）场景中的系统性失灵。

3. **第 3 类：低空观光旅游垂直领域特有词汇 (Low-Altitude Air Tourism Domain-Specific Lexicon, 17 个词, 占比 6.25%)**：
   - **子维度 A：空中高空美学视觉震撼与美学惊叹 (Aerial Visual Awe Dimension)**：
     - **典型词汇**：*breathtaking (1,346次)、stunning (552次)、scenic (400次)、awe (304次)、surreal (98次)、breathtakingly (30次)、mesmerizing (26次)、awed (15次)、sublime (6次)、spellbinding (4次)*。
     - **实证验证**：11 个美学震撼词在 NRC 词典中 **100% 未被收录（匹配标签数全为 0）**，导致评论语料中 **2,791 次高空美学表达遗漏**。
     - **深层原因与学术结论**：空中俯瞰视角引发的高唤起美学惊叹（Awe / Aesthetic Emotion）高度依赖低空观光场景，通用对话语料完全未针对该维度进行设计。
   - **子维度 B：低空飞行感知风险与身体/心理躯体化症状 (Somatic Flight Risk Dimension)**：
     - **典型词汇**：*airsick (33次，晕机躯体症状)、claustrophobic (16次)、claustrophobia (9次，密闭舱室幽闭恐惧)、jitters (5次，飞行前紧张抖抖)、unnerving (4次，心理发慌不安)、phobia (4次，恐高症)*。
     - **实证验证**：6 个飞行感知风险词在 NRC 词典中 **100% 未被收录（匹配标签数全为 0）**，导致评论语料中 **71 次垂直风险表述遗漏**。
     - **深层原因与学术结论**：机舱密闭、气流颠簸与高空悬浮诱发的躯体化焦虑反应为低空观光所特有，通用情感词典完全无法捕捉此类特定生理/心理症状表达。"""

# Cut off duplicate/redundant tail in README.md
for doc, path, content_en_cn in [(readme_text, readme_path, class3_section_en), (cn_text, cn_path, class3_section_cn), (en_text, en_path, class3_section_en)]:
    start_idx = doc.find("### 6. 3 Core Classes")
    if start_idx == -1:
        start_idx = doc.find("### 6. 4 Root Causes")
    if start_idx == -1:
        start_idx = doc.find("### 6. NRC 通用词典发生遗漏的 3 大")
    if start_idx == -1:
        start_idx = doc.find("### 6. NRC 通用词典发生遗漏的 4 大")
        
    end_idx = doc.find("## 📈 Summary Data")
    if end_idx == -1:
        end_idx = doc.find("## 📈 四、 步骤 6")

    if start_idx != -1 and end_idx != -1:
        updated = doc[:start_idx] + content_en_cn + "\n\n" + doc[end_idx:]
        
        # Remove 17 Rescued Table if present in the document
        table_start = updated.find("### 5. 17 Rescued Emotion Terms")
        if table_start != -1:
            table_end = updated.find("### 6. ", table_start)
            if table_end != -1:
                updated = updated[:table_start] + updated[table_end:]
                
        table_start_cn = updated.find("##### 5. 17 Rescued Emotion Terms")
        if table_start_cn != -1:
            table_end_cn = updated.find("### 6. ", table_start_cn)
            if table_end_cn != -1:
                updated = updated[:table_start_cn] + updated[table_end_cn:]
                
        path.write_text(updated, encoding="utf-8")
        print(f"Successfully cleaned & updated '{path.name}'!")
