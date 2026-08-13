#!/usr/bin/env python3
"""Script to update README.md and RESEARCH_NOTES_CN.md with interjection and punctuation methodological rationale."""

from pathlib import Path

readme_path = Path("README.md")
cn_path = Path("RESEARCH_NOTES_CN.md")

readme_note = """
> [!NOTE]
> **Methodological Rationale on Emotive Interjections, Punctuation & Emojis**:
> Although informal emotive interjections such as `wow` (476 mentions across 415 reviews) and `yay` (12 mentions) express high visual arousal, they operate as **expressive structural cues** (analogous to exclamation marks `!`, question marks `?`, or emojis) rather than formal lexical emotion terms (Nouns or Adjectives describing internal states $E_1$ or service appraisals $E_2$).
> To maintain strict lexical purity and prevent blurring the boundary between unigram dictionary entries and structural features, all informal interjections are excluded from the Gold Emotion Lexicon Codebook and logged in the Removed Log. Structural emotional arousal is controlled separately in Level 2 feature engineering via `exclamation_count` and continuous VADER scoring. Formal verbal usages such as **`wowed`** (*"the pilot wowed us"*) remain retained in the Gold Lexicon.
"""

cn_note = """
> [!NOTE]
> **关于感叹词、标点符号与表情包的剔除方法论说明**:
> 尽管口语感叹词如 `wow`（在 415 篇评论中出现 476 次）和 `yay`（12 次）表达了强烈的视觉震撼，但它们在功能上属于**结构化情绪感叹标记**（类似感叹号 `!`、问号 `?` 或表情包 Emoji），而非严谨的词典情感实词（描述内部心理状态 $E_1$ 或服务属性评价 $E_2$ 的名词或形容词）。
> 为保持词典代码本的严格实词纯洁性，防止混淆词典实词与结构化标点特征，所有口语感叹词均统一移入剔除日志。情绪强度的结构化影响已在 Level 2 特征工程中通过 `exclamation_count`（感叹号数量）、大写字母比例及 VADER 得分独立控制。而规范的动词/过去分词用法如 **`wowed`**（如 *"the pilot wowed us"* 使人赞叹）则完整保留在金标准代码本中。
"""

# Update README.md
readme_text = readme_path.read_text(encoding="utf-8")
if "Methodological Rationale on Emotive Interjections" not in readme_text:
    # Insert after section 3 in README
    lines = readme_text.splitlines()
    new_lines = []
    inserted = False
    for l in lines:
        new_lines.append(l)
        if "#### ❌ PURGED (Master Removed Non-Emotion Log" in l and not inserted:
            new_lines.append(readme_note)
            inserted = True
    readme_path.write_text("\n".join(new_lines), encoding="utf-8")
    print("Successfully updated README.md with interjection rationale!")

# Update RESEARCH_NOTES_CN.md
cn_text = cn_path.read_text(encoding="utf-8")
if "关于感叹词、标点符号与表情包的剔除方法论说明" not in cn_text:
    lines = cn_text.splitlines()
    new_lines = []
    inserted = False
    for l in lines:
        new_lines.append(l)
        if "#### ❌ 剔除项 (Master 被剔除词日志" in l and not inserted:
            new_lines.append(cn_note)
            inserted = True
    cn_path.write_text("\n".join(new_lines), encoding="utf-8")
    print("Successfully updated RESEARCH_NOTES_CN.md with interjection rationale!")
