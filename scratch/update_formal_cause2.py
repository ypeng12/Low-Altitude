#!/usr/bin/env python3
"""Update README.md and RESEARCH_NOTES_CN.md to refine Cause 2 into formal academic language."""

from pathlib import Path

readme_path = Path("README.md")
cn_path = Path("RESEARCH_NOTES_CN.md")

readme_text = readme_path.read_text(encoding="utf-8")
cn_text = cn_path.read_text(encoding="utf-8")

cause2_en_formal = """2. **Omission of Modern Online Tourism Colloquial Superlatives (Web 2.0 UGC Gap)**:
   - **Key Terms**: *great (11,541), awesome (2,530), fantastic (2,026), nice (1,794), incredible (1,612), fabulous (508), incredibly (315), phenomenal (200), unbeatable (21)*.
   - **Empirical Validation & Root Comparison**: Unlike Cause 1 (where base roots can be recovered via Lemmatization), **even after 100% Lemmatization root mapping, top colloquial terms such as `great` (11,541), `awesome` (2,530), `fantastic` (2,026), and `nice` (1,794) remain 100% ABSENT from NRC**. This structural omission leaves **20,549 review mentions** of high-frequency satisfaction uncaptured across N=21,215 clean reviews.
   - *Deep Cause & Finding*: NRC 2012 seed vocabulary prioritized formal written English corpora. Modern TripAdvisor reviewers rely heavily on colloquial high-arousal superlatives (*great, awesome, fantastic*), causing widespread generic lexicon failure in Web 2.0 online review contexts and highlighting the necessity of domain-specific codebooks."""

cause2_cn_formal = """2. **归因 2：NRC 原始种子词缺乏现代网络旅游的高频口语赞誉词 (Web 2.0 口语赞誉缺口)**：
   - **典型词汇**：*great (11,541次)、awesome (2,530次)、fantastic (2,026次)、nice (1,794次)、incredible (1,612次)、fabulous (508次)、incredibly (315次)、phenomenal (200次)、unbeatable (21次)*。
   - **实证验证与词根对比**：归因 2 展现了通用词典在 Web 2.0 用户生成内容（UGC）场景中的系统性失灵。与归因 1（可通过形态学归一化找回）存在本质区别，**即使进行 100% 的词根还原（Lemmatization），`great (11,541次)`、`awesome (2,530次)`、`fantastic (2,026次)`、`nice (1,794次)` 等超级高频赞誉词在 NRC 词典中依然 100% 完全缺失**。这一词汇库缺口导致评论语料中 **20,549 次最高频的满意情感表达未能被传统词典匹配捕捉**。
   - **深层原因与论文学术结论**：NRC 在 2012 年构建时选用的种子词汇偏向传统正式书面语（Formal Written Corpora），而 TripAdvisor 上的现代游客在表达满意时极其倾向于使用高唤起口语赞誉词（*great, awesome, fantastic*）。这一发现揭示了传统通用词典在在线旅游文本分析中的严重适应性失灵，进一步彰显了自建语料库推导代码本（Corpus-Derived Codebook）的学术不可替代性。"""

start_r = readme_text.find("2. **Omission of Modern Online Tourism Colloquial Superlatives")
end_r = readme_text.find("3. **Absence of Low-Altitude Aerial Visual Awe")

if start_r != -1 and end_r != -1:
    readme_text = readme_text[:start_r] + cause2_en_formal + "\n\n" + readme_text[end_r:]
    readme_path.write_text(readme_text, encoding="utf-8")
    print("Cleanly updated Cause 2 in README.md!")

start_cn = cn_text.find("2. **归因 2：NRC 原始种子词缺乏现代网络旅游的高频口语赞誉词")
end_cn = cn_text.find("3. **归因 3：通用词典缺失“低空高空视觉震撼与美学惊叹")

if start_cn != -1 and end_cn != -1:
    cn_text = cn_text[:start_cn] + cause2_cn_formal + "\n\n" + cn_text[end_cn:]
    cn_path.write_text(cn_text, encoding="utf-8")
    print("Cleanly updated Cause 2 in RESEARCH_NOTES_CN.md!")
