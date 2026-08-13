#!/usr/bin/env python3
"""Update README.md and RESEARCH_NOTES_CN.md with the perfect formal Cause 3 and Cause 4 academic summaries."""

from pathlib import Path
import subprocess

readme_path = Path("README.md")
cn_path = Path("RESEARCH_NOTES_CN.md")

readme_text = readme_path.read_text(encoding="utf-8")
cn_text = cn_path.read_text(encoding="utf-8")

causes3_4_en_formal = """3. **Absence of Low-Altitude Aerial Visual Awe & Aesthetic Emotions (Domain Awe Gap, 3.31% of Misses)**:
   - **Key Terms**: *breathtaking (1,346), stunning (552), scenic (400), awe (304), surreal (98), breathtakingly (30), mesmerizing (26), awed (15), sublime (6), spellbinding (4)*.
   - **Empirical Validation**: All 11 awe terms have **0 tags in NRC (100% unmapped)**, omitting **2,791 review mentions**.
   - *Deep Cause & Finding*: Low-altitude air tourism is uniquely defined by **Aerial Visual Awe**, a domain-specific aesthetic emotion completely absent from generic news or conversational lexicons.

4. **Absence of Flight Perceived Risk & Somatic Symptoms (Aviation Risk Gap, 1.84% of Misses)**:
   - **Key Terms**: *airsick (33), claustrophobic (16), claustrophobia (9), jitters (5), unnerving (4), phobia (4)*.
   - **Empirical Validation**: All 6 flight risk terms have **0 tags in NRC (100% unmapped)**, omitting **71 review mentions**.
   - *Deep Cause & Finding*: Flight vibration, confined cabin space, and altitude suspense trigger somatic anxiety and perceived risk reactions specific to aviation tourism that generic sentiment dictionaries fail to capture."""

causes3_4_cn_formal = """3. **归因 3：通用词典缺失“低空高空视觉震撼与美学惊叹 (Aerial Visual Awe)”领域词 (占比 3.31%)**：
   - **典型词汇**：*breathtaking (1,346次)、stunning (552次)、scenic (400次)、awe (304次)、surreal (98次)、breathtakingly (30次)、mesmerizing (26次)、awed (15次)、sublime (6次)、spellbinding (4次)*。
   - **实证验证与核验发现**：归因 3 的 11 个美学震撼词在 NRC 词典中 **100% 未被收录（匹配标签数全为 0）**，导致评论语料中 **2,791 次高空美学情感表达未能被传统词典捕捉**。
   - **深层原因与论文学术结论**：低空观光旅游（直升机/水上飞机/观光飞行）的核心体验是**“空中俯瞰带来的高唤起美学惊叹与视觉冲击（Aerial Visual Awe / Aesthetic Emotion）”**。这种情感极其专一且高度依赖特定场景（景致宏大、冰川大峡谷高空视角），在通用新闻或日常对话文本中出现频率极低，因此通用 NRC 词典完全没有针对该维度进行设计。

4. **归因 4：低空飞行感知风险与身体/心理躯体化症状词 (占比 1.84%)**：
   - **典型词汇**：*airsick (33次，晕机躯体症状)、claustrophobic (16次)、claustrophobia (9次，密闭舱室幽闭恐惧)、jitters (5次，飞行前紧张抖抖)、unnerving (4次，心理发慌不安)、phobia (4次，恐高症)*。
   - **实证验证与核验发现**：归因 4 的 6 个飞行感知风险词在 NRC 词典中 **100% 未被收录（匹配标签数全为 0）**，导致评论语料中 **71 次垂直领域躯体化风险表述未能被有效捕获**。
   - **深层原因与论文学术结论**：气流颠簸（Turbulence）、密闭机舱空间与高空悬浮会引发游客独特的**感知风险（Perceived Risk）与躯体化焦虑反应**。这些词汇专属于低空飞行垂直场景，通用情感词典完全无法捕捉此类特定生理/心理症状表达。"""

start_r = readme_text.find("3. **Absence of Low-Altitude Aerial Visual Awe")
end_r = readme_text.find("### 5. Master Gold Emotion Lexicon Scatter Plot")
if end_r == -1:
    end_r = readme_text.find("## 📈 Summary Data & Empirical Metrics Ledger")

if start_r != -1 and end_r != -1:
    readme_text = readme_text[:start_r] + causes3_4_en_formal + "\n\n" + readme_text[end_r:]
    readme_path.write_text(readme_text, encoding="utf-8")
    print("Successfully updated Cause 3 and Cause 4 in README.md!")

start_cn = cn_text.find("3. **归因 3：通用词典缺失“低空高空视觉震撼与美学惊叹")
end_cn = cn_text.find("### 5. Master 金标准代码本 VADER 极性")
if end_cn == -1:
    end_cn = cn_text.find("## 📈 四、 步骤 6：N-Gram 挖掘与学术图表产出")

if start_cn != -1 and end_cn != -1:
    cn_text = cn_text[:start_cn] + causes3_4_cn_formal + "\n\n" + cn_text[end_cn:]
    cn_path.write_text(cn_text, encoding="utf-8")
    print("Successfully updated Cause 3 and Cause 4 in RESEARCH_NOTES_CN.md!")
