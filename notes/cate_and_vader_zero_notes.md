# CATE 107 词库构建方法论与散点图 X=0 分词汇成因深度研析

> **文档目的**：本文档详细记载 CATE 107 领域词库的筛选衍生过程，以及纯情绪散点图（`nrc_pure_emotion_words_scatter.png`）中 $X = 0.0$ 中线形成的三大底层原因，为论文 Method & Results 章节提供严密的学术论述支撑。

---

## 一、 CATE 107 词库构建与筛选全过程 (Methodology for CATE 107)

CATE（Contextual Aspect-based Tourism Emotion / 领域特定客舱与服务属性词库）的衍生经历了严格的四阶段 NLP 过滤与学术重构：

```mermaid
flowchart LR
    A["阶段 1: 原始评论词汇提取<br/>(22,235 条评论)"] --> B["阶段 2: 频次与词性初筛<br/>(频次 ≥ 15, 抽取形容词/感知词)"]
    B --> C["阶段 3: 领域相关性剔除<br/>(剔除无意义通用修饰词)"]
    C --> D["阶段 4: CATE 107 最终精选<br/>(归入 5 大 ServQual 心理维度)"]
```

### 1. 初始候选词抽取（224 词全集）
* **数据源**：TripAdvisor 22,235 条经过 Level 2 纯净英文过滤后的评论（`is_english = 1`）。
* **提取规则**：利用 NLTK 词性标注（POS Tagging）与词频分析，抽取出现频次 $\ge 15$ 次的所有描述性形容词（JJ/JJR/JJS）与感知体验词，生成初始候选集 `cate_words_full_224.csv`。

### 2. 领域切题度与学术降维（精炼为 107 词）
为了避免通用词汇干扰，从 224 词中人工与算法协同剔除以下非核心词：
* 剔除纯地理方位/机械计数词（如 `first`, `second`, `one`, `two`, `left`, `right`）；
* 剔除通用无特定指向修饰词（如 `other`, `same`, `different`）。

最终保留 **107 个直接绑定低空体验、客舱设施、飞行员服务与心理震撼** 的专属词汇（`cate_words_curated_107.csv`）。

### 3. 重构 5 大 ServQual & 心理体验维度
这 107 个词按低空旅游特征重构为 5 大体验维度：
1. **Pilot & Service Quality（机长操控与服务）** (n=24)：`skilled`, `personable`, `courteous`, `gracious`, `careful`...
2. **Aerial Scenery & Environment（高空景观与天色）** (n=8)：`crystal`, `overcast`, `grandeur`, `epic`...
3. **Cabin Facilities & Comfort（客舱设施与舒适度）** (n=15)：`small`, `noise`, `cold`, `balance`, `uncomfortable`...
4. **Perceived Value & Flexibility（性价比与行程灵活性）** (n=13)：`worth`, `priceless`, `cheap`, `afford`, `fair`, `delayed`...
5. **Psychological Thrill & Service Friction（心理震慑与情绪摩擦）** (n=47)：`fear`, `nervous`, `scared`, `afraid`, `anxious`, `lack`, `wrong`...

---

## 二、 散点图（nrc_pure_emotion_words_scatter.png）中线 X = 0.0 成因分析

在纯情绪散点图中，位于正中间 **$X = 0.0$ 竖线上共有 357 个词汇**，其底层形成原因可归结为以下三点：

![Pure Emotion Words Scatter Plot](file:///Users/yuliangpeng/Desktop/Low-Altitude/figures/nrc_emotion_plots/nrc_pure_emotion_words_scatter.png)

### 原因 1：VADER 基础规则字典的容量局限（Rule-Lexicon Bound）
* **底层机制**：VADER 内部的固有极性表（`sia.lexicon`）仅手动收录了 7,500 个极端褒贬词（如 `horrible` $-2.5$, `fear` $-2.2$, `friendly` $+2.2$）。
* **后果**：对于未在 VADER 手动打分表中的英文单词，VADER 算法默认分配极性得分 **$0.0$**。

### 原因 2：通用字典与低空观光领域词汇的断层（60 个 CATE 词归 0）
* 在 $X = 0.0$ 的 357 个词中，有 **60 个属于 CATE 107 词库（占比 56% 的 CATE 属性）**。
* **经典例子**：
  * `priceless`（无价的, 5.00星, 85次）在 VADER 表中缺失 $\rightarrow X=0.0$；
  * `personable`（亲切平易近人的机长, 4.97星, 418次）在 VADER 表中缺失 $\rightarrow X=0.0$；
  * `skilled`（操控熟练的机长, 4.95星, 240次）在 VADER 表中缺失 $\rightarrow X=0.0$；
  * `inaccessible`（陆路不可达的观光独特性, 4.96星, 86次）在 VADER 表中缺失 $\rightarrow X=0.0$。

### 原因 3：NRC 情绪词典与 VADER 极性词典的映射补集（297 个 NRC 词归 0）
* 另外 **297 个词汇** 来自 Saif Mohammad 的 **NRC 8 大情绪词典**。
* **经典例子**：
  * **`professional`**（专业严谨的）：NRC 给出了 `Trust`（信任）情绪标签，但 VADER 词典未赋值 $\rightarrow X=0.0$；
  * **`spectacular`**（壮观震撼的）：NRC 给出了 `Anticipation`（期待）情绪标签，但 VADER 词典未赋值 $\rightarrow X=0.0$；
  * **`flying`**（飞行行为）：NRC 给出了 `Fear`（恐惧震慑）情绪标签，但 VADER 词典未赋值 $\rightarrow X=0.0$。

---

## 三、 学术价值与论文叙事逻辑（Paper Narrative Contribution）

这一现象在论文的讨论部分（Discussion & Contribution）构成了极强的学术论点：

> 💡 **论文观点**：
> 1. 通用 NLP 词典（如 VADER）在低空观光等高端体验型服务场景中存在**严重的情感感知盲区**（遗漏了 `personable`, `skilled`, `priceless` 等核心体验词，将其错误划为 $0.0$ 中性）。
> 2. 结合 **NRC 情绪维度（捕捉情感体验）** 与 **CATE 领域专属字典（补齐专业服务属性）**，能够完美解决通用 NLP 模型的遗漏问题，形成高精度的服务质量评估体系！
