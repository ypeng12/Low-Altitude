# idea1 / idea2 合并后的正式研究设计

## 方法定位

两份想法可以合并为一个“发现—编码—转化”框架，但论文中不宜把它写成已经标准化的方法名。建议正式表述为：

> A human-validated LLM-assisted multi-stage qualitative–computational text analysis integrating corpus-driven emotion discovery, aspect–emotion–mechanism coding, and emotion transformation detection.

中文：

> 采用经人工验证的 LLM 辅助多阶段质性—计算文本分析，综合开展语料驱动的情绪发现、感知对象—情绪—机制编码与情绪转化检测。

本研究识别的是评论文本中游客叙述的机制与变化，不把它表述为统计因果效应。

## 三项任务应当分开

### 1. 语料驱动的 8+3 候选发现

- NRC8 始终保留为可比较的基线。
- 新增情绪必须先由无监督聚类、稳定性、代表短语和原句证据支持，再参考其他 taxonomy。
- 当前 LLM 初审候选为 `scenic awe`、`flight apprehension`、`provider-directed gratitude`。
- 三者尚未成为最终 +3；需要两名人工编码者独立审查 119 个簇并裁决。
- `relief/reassurance` 暂时保留在 Transition 任务，因为它主要表现为“先前焦虑被化解后的终点”，静态聚类证据弱于转化证据。
- `excitement` 在泛化好评、fun/cool、野生动物、冰川等簇中分散，现阶段不能因研究预期而强行选入。
- `worth it` 稳定且高频，但应编码为价值评价或 reappraisal mechanism，不是离散情绪。

### 2. Aspect–Emotion–Mechanism（AEM）

AEM 的记录单位是有证据的文本 span，而不是整条评论的单一标签。建议字段：

`review_id, sentence, aspect, initial_emotion, trigger_span, actor, mechanism, final_emotion, mixed_emotion, confidence, annotation_status`

其中：

- Aspect 回答“游客在评价什么”；
- Emotion 回答“游客表达了什么经历性情绪”；
- Trigger/Actor/Mechanism 回答“文本把这种情绪归因于什么事件、谁的行为、怎样的调节或解释过程”；
- 机制字段必须有原文 trigger span，不能仅由 LLM 自由概括；
- Aspect 或机制不清楚时允许 `uncertain`，不强制标签。

### 3. Emotion Transition

Transition 是独立任务，记录单位为 source span 与 target span 之间的有向关系：

`review_id, sentence, source_span, source_emotion, transition_marker, target_span, target_emotion, transformation_type, actor, mechanism, confidence`

先高召回抽取显式 discourse 候选，再对 `target_embedding - source_embedding` 聚类，自动发现重复转化方向。`but/however` 等规则只负责候选召回，不负责最终结论。

当前语料已自动形成的强模式包括：

- price concern → value satisfaction：expensive/pricey → worth it；
- flight apprehension → relief：担忧晕机或小飞机 → no problems / felt safe；
- flight apprehension → pilot reassurance → relief；
- discomfort/annoyance → scenic awe：噪声、颠簸或时长限制 → breathtaking/awe-inspiring views；
- anticipation → weather constraint → disappointment；
- disappointment → alternative scenery → scenic awe；
- missed glacier landing → outcome reappraisal → joy；
- joy → negative qualification → disappointment/annoyance。

这些都是 LLM 辅助的簇级初审，不是 Gold 标签。

## 正确的验证顺序

1. 两名编码者独立完成 Module 1 cluster review，裁决最终 +3。
2. 使用 300 条盲标候选分别完成 AEM 和 Transition；实例级 LLM 标签对编码者不可见。
3. 先计算字段级一致性，再裁决。类别字段可用 Cohen's κ；多标签字段报告 micro/macro F1 或 Krippendorff's alpha；exact span 同时报告 exact match 和 token-overlap F1。
4. 冻结 codebook 与 Gold Standard 后，才让 LLM 批量编码剩余语料。
5. LLM 输出必须保存原始响应、prompt/model/version、解析错误、与 Gold 的差异、人工修订和不确定样本。
6. 只有通过 Gold 评估的字段才进入论文统计；低置信或模型分歧样本继续保留人工队列。

## 当前阶段明确不做

- 不做 rating prediction；
- 不做因果推断或把文本机制当作因果效应；
- 不做 SHAP；
- 不做 econometrics；
- 不训练多任务模型；
- 不把 provisional matrix 当最终发现；
- 不把 300 条候选称为 Gold Standard，直到人工双标和裁决完成。
