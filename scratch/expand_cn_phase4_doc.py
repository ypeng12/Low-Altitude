#!/usr/bin/env python3
"""Expand Phase 4 in RESEARCH_NOTES_CN.md with exhaustive human adjudication rules, examples, and decision logic."""

from pathlib import Path
import subprocess

cn_path = Path("RESEARCH_NOTES_CN.md")
cn_text = cn_path.read_text(encoding="utf-8")

phase4_full_cn = """
#### 📍 阶段 4：人机协同深度审定、错别字归一化与细粒度筛选法则 (Phase 4 Human-in-the-Loop Fine Adjudication)

在完成了全量 21,215 条评论的词汇挖掘后，我们对初始样本与补齐出来的 **8,726 个候选词汇** 进行了 **100% 逐词人工例句审查 (`example_context`)**。阶段 4 建立了严密的形态归一化机制与 7 大细粒度剔除法则，确保金标准代码本的学术纯洁性：

##### 1️⃣ 错别字归一化与形态变体映射协议 (`canonical_lemma`)
在真实游客在线评论中，约有 0.8% 的文本包含错别字、口语拼写变体或复杂的动词屈折变体。如果直接采用原始字符串匹配，会导致同一核心词汇的词频被严重分散（如 `suprised` 4次 与 `surprised` 1,215次 分离计算）。
我们在代码本中专门增加了 **`canonical_lemma` 独立列**，建立了标准化字典词根双索引映射 (`word` $\rightarrow$ `canonical_lemma`)：

- **错别字变体归一化案例**：
  - `suprised` (4次) $\rightarrow$ `surprised` (感到惊喜惊讶的)
  - `suprise` (5次) $\rightarrow$ `surprise` (惊喜 / 意料之外)
  - `exhilerating` (7次) $\rightarrow$ `exhilarating` (令人兴奋刺激酣畅地)
  - `aprehensive` (3次) $\rightarrow$ `apprehensive` (感到忧虑不安的)
  - `dissapointed` (8次) $\rightarrow$ `disappointed` (感到失望的)
  - `wonderfull` (10次) $\rightarrow$ `wonderful` (精彩绝妙的)
- **形态与数态变体归一化案例**：
  - `worries` (38次) $\rightarrow$ `worry` (担忧 / 挂虑)
  - `surprises` (21次) $\rightarrow$ `surprise` (惊喜)
  - `cherished` (8次) $\rightarrow$ `cherish` (珍视铭记的)
  - `hates` (5次) / `hated` (5次) $\rightarrow$ `hate` (厌恶/讨厌)
  - `dreaded` (4次) / `dreading` (4次) $\rightarrow$ `dread` (感到恐惧的)
  - `scariest` $\rightarrow$ `scary` (最吓人的)

##### 2️⃣ 保留项法则：Master 金标准代码本 (630 个纯正情感实词)
所有保留词汇必须在例句中明确表达游客内部心理情感或对低空观光品质的主观评价：
1. **体验者直接心理情绪状态 ($E_1$ Experiencer Affect)**：游客感受到的内部心理情绪：
   - *恐惧与焦虑类*: *nervous*, *afraid*, *scared*, *terrified*, *worried*, *claustrophobia* (幽闭恐惧), *jitters* (忐忑抖抖), *apprehension*, *phobia* (恐高), *uneasiness*, *dreaded*, *timid*, *unsettled*.
   - *喜悦与兴奋类*: *happy*, *thrilled*, *cheerful*, *exhilarated*, *giddy*, *stoked*, *overjoyed*, *ecstasy*, *loving*, *cherished*.
   - *释怀与舒适类*: *relief*, *comforted*, *peacefulness*, *calming*, *tranquil*.
   - *惊奇与震惊类*: *stunned*, *shocked*, *surprised*, *astonished*, *astounded*.
   - *负面痛苦与遗憾类*: *disappointed*, *underwhelmed*, *guilty*, *hated*, *irritating*, *sickening*, *pity*, *remorse*, *envy*.
2. **刺激物与服务品质评价 ($E_2$ Stimulus / Service Appraisal)**：对观光飞行品质的主观评价（*scary*, *spectacular*, *smooth*, *professional*, *flawless*, *hostile*, *nerve-wracking*, *great*, *amazing*, *good*, *awesome*, *excellent*, *captivating*, *daunting*, *harrowing*）。
3. **美学情绪与高唤起 Awe (Aesthetic Emotion & Awe)**：*breathtakingly* (高空视角屏息惊叹), *sublime* (冰川景致的崇高感), *impressed, wonder, wonders, magnificence, surprises, marvel, marvellous, mesmerizing, awed, wowed*.

##### 3️⃣ 剔除项法则：Master 被剔除词日志 (8,096 个剔除词)
按照 7 大规则严格清除非情感噪声，所有剔除词汇均在 `removed_non_emotion_words_log.xlsx` 中记录了具体剔除原因：

> [!NOTE]
> **关于感叹词、标点符号与表情包的剔除方法论说明**:
> 口语感叹词如 `wow`（在 415 篇评论中出现 476 次）和 `yay`（12 次）在功能上属于**结构化情绪感叹标记**（类似感叹号 `!`、问号 `?` 或表情包 Emoji），而非严谨的词典情感实词（描述内部心理状态 $E_1$ 或服务属性评价 $E_2$ 的名词或形容词）。情绪强度的结构化影响已在 Level 2 特征工程中通过 `exclamation_count`（感叹号数量）、`uppercase_ratio`（大写字母比例）及 VADER 得分独立控制。而规范的动词/过去分词用法如 **`wowed`**（如 *"the pilot wowed us"* 使人赞叹）则完整保留在金标准代码本中。

1. **口语语气感叹词**: `wow` (476次), `yay` (12次)（剔除为语气结构标记，非严谨词典实词；动词用法 `wowed` 完整保留）。
2. **地理实体与机械构件词**: **`grand` (2,534次，剔除为 `Grand Canyon` 大峡谷地名专有名词实体)**、*helicopter*, *plane*, *pilot*, *glacier*, *canyon*, *water*, *talkeetna*, *maui*, *mckinley*.
3. **价格与经济成本评价**: **`expensive` (529次，剔除为客观经济属性评价)**、`overpriced`, `inexpensive`, `pricey`（保持价格词剔除标准的一致性）。
4. **程序服务技能与解说效率**: `knowledgeable` (解说丰富), `informative` (干货满满), `educational` (教育意义), `easy` (流程顺畅), `courteous` (礼貌), `patient` (耐心), `flexible` (灵活), `polite` (礼貌), `timely` (及时迅速).
5. **机械平稳与物理震动**: `choppy` (气流颠簸), `seamlessly` (无缝衔接), `beyond` (程度修饰).
6. **社交礼貌问候**: *thanks*, *thank*, *thanked*, *thankyou*.
7. **中性代词、时间与量词**: *minute*, *hour*, *dollar*, *one*, *first*, *highly*, *took*, *got*, *day*, *time*.

---

### 5. 数学完备性证明与全量划分方程
$$\text{全量审定词汇宇宙 (8,726)} = \text{Master 金标准代码本 (630)} + \text{Master 剔除词日志 (8,096)}$$
$$\text{Master 金标准代码本 (630)} \cap \text{Master 剔除词日志 (8,096)} = 0 \quad (\text{100% 零交集完备划分})$$
"""

# Replace Phase 4 in RESEARCH_NOTES_CN.md
start_mark = "#### 📍 阶段 4：人机协同精准审定与错别字归一化"
if start_mark not in cn_text:
    start_mark = "#### 📍 阶段 4：人机协同深度审定"

start_idx = cn_text.find(start_mark)
end_mark = "### 2. 错别字与形态变体归一化协议"
end_idx = cn_text.find(end_mark)

if start_idx != -1 and end_idx != -1:
    cn_text = cn_text[:start_idx] + phase4_full_cn + "\n" + cn_text[end_idx:]
    cn_path.write_text(cn_text, encoding="utf-8")
    print("Successfully expanded Phase 4 in RESEARCH_NOTES_CN.md!")
else:
    print(f"Warning: start_idx={start_idx}, end_idx={end_idx}")

# Re-generate Chinese PDF report
res_pdf = subprocess.run(["python3", "scratch/generate_pdf_report.py"], capture_output=True, text=True)
print(res_pdf.stdout.strip())
