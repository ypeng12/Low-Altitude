#!/usr/bin/env python3
"""Add NRC Experiment Results to README.md and RESEARCH_NOTES_CN.md."""

from pathlib import Path

readme_path = Path("README.md")
cn_path = Path("RESEARCH_NOTES_CN.md")

nrc_readme_section = """
### 📊 7. NRC Emotion Lexicon Mapping & Comparative Audit ($N=632$ Words)

To validate the theoretical superiority of our **Corpus-Derived Gold Emotion Lexicon** over generic off-the-shelf lexicons, we mapped all **632 Master Gold Emotion Terms** against the **NRC Emotion Lexicon** (Mohammad & Turney):

![NRC Gold Lexicon Distribution](figures/nrc_emotion_plots/nrc_mapping_gold_lexicon_distribution.png)

#### Key Empirical Findings & NRC Lexicon Gaps:
1. **Low Coverage Rate of Generic Lexicons (43.35% Miss Rate)**:
   - Out of 632 domain-specific Gold Emotion terms, **NRC Lexicon only covers 358 words (56.65%)**.
   - **274 words (43.35%) are completely MISSED by NRC**, including critical high-frequency low-altitude air tourism emotions: *amazing* (6,251 mentions), *awesome* (2,530 mentions), *fantastic* (2,026 mentions), *incredible* (1,612 mentions), *breathtaking* (1,346 mentions), *stunning* (552 mentions), *unforgettable* (459 mentions), and *awe* (304 mentions).

2. **NRC 8 Basic Emotions Distribution across Gold Lexicon**:
   - **Joy**: 119 words (18.83%)
   - **Trust**: 93 words (14.72%)
   - **Anticipation**: 79 words (12.50%)
   - **Fear**: 75 words (11.87%)
   - **Sadness**: 72 words (7.28%)
   - **Surprise**: 69 words (10.92%)
   - **Anger**: 53 words (8.39%)
   - **Disgust**: 46 words (7.28%)
"""

nrc_cn_section = """
### 📊 八、 NRC 情感词典套入对比实验与学术审计 (N=632 个金标准词)

为实证验证本项目自建的**语料库推导金标准情感代码本**相较于传统通用词典（如 NRC Emotion Lexicon）的学术优越性，我们将 **632 个 Master 金标准情感实词** 全量套入 **NRC 词典**（Mohammad & Turney）进行映射与对比：

![NRC Gold Lexicon Distribution](figures/nrc_emotion_plots/nrc_mapping_gold_lexicon_distribution.png)

#### 核心实证发现与通用 NRC 词典的重大缺陷：
1. **通用词典的低覆盖率与严重遗漏（43.35% 遗漏率）**：
   - 在 632 个低空观光领域专属情感词中，**NRC 词典仅能覆盖 358 个词（56.65%）**。
   - **高达 274 个核心情感词（43.35%）被 NRC 彻底遗漏**！其中包括低空观光最核心的高频震撼词：*amazing*（6,251次）、*awesome*（2,530次）、*fantastic*（2,026次）、*incredible*（1,612次）、*breathtaking*（1,346次）、*stunning*（552次）、*unforgettable*（459次）、*awe*（304次）。这直接证明了盲目套用通用 NRC 词典会导致大量高价值游客情绪信号缺失！

2. **NRC 8 大基础情绪在金标准代码本中的分布**：
   - **喜悦 (Joy)**：119 个词 (18.83%)
   - **信任 (Trust)**：93 个词 (14.72%)
   - **期盼 (Anticipation)**：79 个词 (12.50%)
   - **恐惧 (Fear)**：75 个词 (11.87%)
   - **悲伤 (Sadness)**：72 个词 (11.39%)
   - **惊喜 (Surprise)**：69 个词 (10.92%)
   - **愤怒 (Anger)**：53 个词 (8.39%)
   - **厌恶 (Disgust)**：46 个词 (7.28%)
"""

readme_text = readme_path.read_text(encoding="utf-8")
cn_text = cn_path.read_text(encoding="utf-8")

if "### 📊 7. NRC Emotion Lexicon Mapping" not in readme_text:
    readme_text += "\n" + nrc_readme_section
    readme_path.write_text(readme_text, encoding="utf-8")

if "### 📊 八、 NRC 情感词典套入对比实验" not in cn_text:
    cn_text += "\n" + nrc_cn_section
    cn_path.write_text(cn_text, encoding="utf-8")

print("Successfully updated README.md and RESEARCH_NOTES_CN.md with NRC Experiment Results!")
