#!/usr/bin/env python3
"""Update README.md and RESEARCH_NOTES_CN.md to use strict, formal academic language for Cause 1."""

from pathlib import Path
import subprocess

readme_path = Path("README.md")
cn_path = Path("RESEARCH_NOTES_CN.md")

readme_text = readme_path.read_text(encoding="utf-8")
cn_text = cn_path.read_text(encoding="utf-8")

cause1_formal_en = """1. **Morphological & Participle Derivation Gaps (Pure Morphological Variants)**:
   - **Participle Forms (-ing / -ed)**: e.g., *loved (1,473), impressed (255), inspiring (210), relaxed (159), scared (144), amazed (120), thrilled (113), reassuring (97)*.
   - **Adverbs & Superlatives (-ly, -est, -er)**: e.g., *better (1,585), cheaper (208), perfectly (155), smoother (143), safely (132), smoothest (105), luckily (96)*.
   - **Empirical Validation**: Among the 127 pure morphological variant words, **48.82% (62 words) have base dictionary roots (e.g., *amaze, love, impress, inspire, scare, thrill, good, safe*) already present in NRC**. However, static string matching fails to capture them, omitting **88.7% (15,581 review mentions)** of high-frequency emotional expressions.
   - *Finding*: Generic NRC lexicons lack morphological derivation rules, causing significant classification omissions."""

cause1_formal_cn = """1. **归因 1：纯粹语法形态与分词变体补全不足 (Morphological Variants)**：
   - **分词形式 (-ing / -ed)**：如 *loved (1,473次), impressed (255次), inspiring (210次), relaxed (159次), scared (144次), amazed (120次), thrilled (113次), reassuring (97次)*。
   - **副词与比较级/最高级 (-ly, -est, -er)**：如 *better (1,585次), cheaper (208次), perfectly (155次), smoother (143次), safely (132次), smoothest (105次), luckily (96次)*。
   - **词根验证与实证发现**：在 127 个纯形态变体词中，**48.82%（62 个词）的底层词根（如 *amaze, love, impress, inspire, scare, thrill, good, safe*）实际上在 NRC 词典中已有收录**。然而，由于传统静态匹配缺乏形态学还原规则，导致评论语料中 **88.7%（累计 15,581 次）的高频情感提及未能被有效匹配捕捉**。
   - **论文学术结论**：传统 NRC 词典缺乏形态学归一化机制（Morphological Normalization），引发了显著的词汇提取偏误。本项目引入的 `canonical_lemma` 词根映射协议成功弥合了这一形态学断层。"""

start_r = readme_text.find("1. **Morphological & Participle Derivation Gaps")
end_r = readme_text.find("2. **Omission of Modern Online Tourism Colloquial Superlatives**:")

if start_r != -1 and end_r != -1:
    readme_text = readme_text[:start_r] + cause1_formal_en + "\n\n" + readme_text[end_r:]
    readme_path.write_text(readme_text, encoding="utf-8")
    print("Successfully updated Cause 1 in README.md with formal academic tone!")

start_cn = cn_text.find("1. **归因 1：纯粹语法形态与分词变体")
end_cn = cn_text.find("2. **归因 2：NRC 原始种子词缺乏现代网络旅游的高频口语赞誉词**：")

if start_cn != -1 and end_cn != -1:
    cn_text = cn_text[:start_cn] + cause1_formal_cn + "\n\n" + cn_text[end_cn:]
    cn_path.write_text(cn_text, encoding="utf-8")
    print("Successfully updated Cause 1 in RESEARCH_NOTES_CN.md with formal academic tone!")

# Re-generate Chinese PDF report
res_pdf = subprocess.run(["python3", "scratch/generate_pdf_report.py"], capture_output=True, text=True)
print(res_pdf.stdout.strip())
