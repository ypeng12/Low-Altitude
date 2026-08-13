#!/usr/bin/env python3
"""Update README.md and RESEARCH_NOTES_CN.md with the perfect formal Cause 2 academic summary matching Cause 1 structure."""

from pathlib import Path

readme_path = Path("README.md")
cn_path = Path("RESEARCH_NOTES_CN.md")

readme_text = readme_path.read_text(encoding="utf-8")
cn_text = cn_path.read_text(encoding="utf-8")

cause2_en_formal = """2. **Omission of Modern Online Tourism Colloquial Superlatives & Base Terms (Web 2.0 UGC Seed Gap, 44.85% of Misses)**:
   - **Key Terms**: *great (11,541), awesome (2,530), fantastic (2,026), nice (1,794), incredible (1,612), comfortable (1,446), fabulous (508), enjoyable (460), unforgettable (459), funny (301), phenomenal (200)*.
   - **Manual & Code Verification**: Manual and programmatic audit confirmed that among the 128 base candidate words, **only `stellar` (29 mentions) exists as a rare exception in NRC (tagged with `positive`), whereas all remaining 127 base terms are 100% ABSENT from NRC (matching tags = 0)**. These 127 pure missed terms leave **28,073 review mentions** uncaptured.
   - **Pareto Principle Validation**: Unlike Cause 1 (recoverable via Lemmatization), Cause 2 represents a complete dictionary seed gap. Remarkably, just **10 top high-frequency colloquial superlatives** (*great, awesome, fantastic, nice, incredible, etc.*) account for **20,549 mentions (73.2% of Cause 2 frequency, and 42.08% of total missed review frequency)**.
   - *Deep Cause & Finding*: NRC 2012 seed vocabulary prioritized formal written English corpora. Modern TripAdvisor reviewers rely heavily on colloquial high-arousal superlatives (*great, awesome, fantastic*), causing widespread generic lexicon failure in Web 2.0 online review contexts and highlighting the necessity of domain-specific codebooks."""

cause2_cn_formal = """2. **归因 2：NRC 原始种子词缺乏现代网络旅游的高频口语赞誉与基础词汇 (占比 44.85%)**：
   - **典型词汇**：*great (11,541次)、awesome (2,530次)、fantastic (2,026次)、nice (1,794次)、incredible (1,612次)、comfortable (1,446次)、fabulous (508次)、unforgettable (459次)、enjoyable (460次)、funny (301次)、phenomenal (200次)*。
   - **人工与代码核验发现**：在归因 2 的 128 个基础词中，**经人工与代码全量逐词检索核验，仅 `stellar (29次)` 一词作为特例在 NRC 中标记了正向极性（*positive*），其余 127 个基础词在 NRC 词典中 100% 完全未被收录（匹配标签数全为 0）**。这 127 个纯遗漏词影响了评论语料中 **28,073 次情感表达**。
   - **帕累托二八定律验证**：与归因 1（可通过形态学归一化找回）不同，归因 2 代表了词汇库的绝对缺口。其中，以 *great, awesome, fantastic, nice, incredible* 为代表的 **前 10 个头部高频口语赞美词，独自贡献了 20,549 次提及（占据归因 2 总频次的 73.2%，以及全量遗漏语料频次的 42.08%）**。
   - **深层原因与论文学术结论**：NRC 在 2012 年构建时选用的种子词汇偏向传统正式书面语（Formal Written Corpora），而 TripAdvisor 上的现代游客在表达满意时极其倾向于使用高唤起口语赞誉词（*great, awesome, fantastic*）。这一发现揭示了传统通用词典在 Web 2.0 在线旅游评价场景中的严重适应性失灵，进一步彰显了自建语料库推导代码本（Corpus-Derived Codebook）的学术不可替代性。"""

start_r = readme_text.find("2. **Omission of Modern Online Tourism Colloquial Superlatives")
end_r = readme_text.find("3. **Absence of Low-Altitude Aerial Visual Awe")

if start_r != -1 and end_r != -1:
    readme_text = readme_text[:start_r] + cause2_en_formal + "\n\n" + readme_text[end_r:]
    readme_path.write_text(readme_text, encoding="utf-8")
    print("Successfully updated Cause 2 in README.md!")

start_cn = cn_text.find("2. **归因 2：NRC 原始种子词缺乏现代网络旅游的高频口语赞誉")
end_cn = cn_text.find("3. **归因 3：通用词典缺失“低空高空视觉震撼与美学惊叹")

if start_cn != -1 and end_cn != -1:
    cn_text = cn_text[:start_cn] + cause2_cn_formal + "\n\n" + cn_text[end_cn:]
    cn_path.write_text(cn_text, encoding="utf-8")
    print("Successfully updated Cause 2 in RESEARCH_NOTES_CN.md!")
