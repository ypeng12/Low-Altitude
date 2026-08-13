#!/usr/bin/env python3
"""Update README.md and RESEARCH_NOTES_CN.md to document deep Cause 2 empirical findings."""

from pathlib import Path
import subprocess

readme_path = Path("README.md")
cn_path = Path("RESEARCH_NOTES_CN.md")

readme_text = readme_path.read_text(encoding="utf-8")
cn_text = cn_path.read_text(encoding="utf-8")

cause2_en_formal = """2. **Omission of Modern Online Tourism Colloquial Superlatives (Web 2.0 UGC Gap)**:
   - **Key Terms**: *great (11,541), awesome (2,530), fantastic (2,026), nice (1,794), incredible (1,612), fabulous (508), incredibly (315), phenomenal (200), unbeatable (21)*.
   - **Empirical Validation**: Unlike Cause 1 (which recovers roots via Lemmatization), **even after 100% Lemmatization root mapping, top colloquial terms such as `great` (11,541), `awesome` (2,530), `fantastic` (2,026), and `nice` (1,794) remain 100% ABSENT from NRC**. This omission impacts **20,578 review mentions** across N=21,215 reviews.
   - *Deep Cause*: NRC 2012 seed vocabulary prioritized formal written English. Modern TripAdvisor reviewers rely heavily on colloquial high-arousal superlatives (*great, awesome, fantastic*), causing widespread generic lexicon failure in Web 2.0 online review contexts."""

cause2_cn_formal = """2. **归因 2：NRC 原始种子词缺乏现代网络旅游的高频口语赞誉词 (Web 2.0 口语赞誉缺口)**：
   - **典型词汇**：*great (11,541次)、awesome (2,530次)、fantastic (2,026次)、nice (1,794次)、incredible (1,612次)、fabulous (508次)、incredibly (315次)、phenomenal (200次)*。
   - **实证验证与词根对比**：与归因 1（可通过词根还原找回）存在本质区别，**即使进行 100% 的词根还原（Lemmatization），`great (11,541次)`、`awesome (2,530次)`、`fantastic (2,026次)`、`nice (1,794次)` 等超级高频赞誉词在 NRC 词库中依然 100% 完全不存在**！该缺口直接影响了评论语料中 **20,578 次最高频的满意情感表达**。
   - **深层原因与学术结论**：NRC 选词偏向传统正式书面语（Formal Written English），而 TripAdvisor 上的现代游客在表达满意时极其倾向于使用现代口语高唤起赞誉词（*great, awesome, fantastic*），揭示了传统通用词典在现代 Web 2.0 用户生成内容（UGC）场景中的大规模失灵。"""

start_r = readme_text.find("2. **Omission of Modern Online Tourism Colloquial Superlatives")
end_r = readme_text.find("3. **Absence of Low-Altitude Aerial Visual Awe")

if start_r != -1 and end_r != -1:
    readme_text = readme_text[:start_r] + cause2_en_formal + "\n\n" + readme_text[end_r:]
    readme_path.write_text(readme_text, encoding="utf-8")
    print("Successfully updated Cause 2 in README.md!")

start_cn = cn_text.find("2. **归因 2：NRC 原始种子词缺乏现代网络旅游的高频口语赞誉词")
end_cn = cn_text.find("3. **归因 3：通用词典缺失“低空高空视觉震撼与美学惊叹")

if start_cn != -1 and end_cn != -1:
    cn_text = cn_text[:start_cn] + cause2_cn_formal + "\n\n" + cn_text[end_cn:]
    cn_path.write_text(cn_text, encoding="utf-8")
    print("Successfully updated Cause 2 in RESEARCH_NOTES_CN.md!")

res_pdf = subprocess.run(["python3", "scratch/generate_pdf_report.py"], capture_output=True, text=True)
print(res_pdf.stdout.strip())
