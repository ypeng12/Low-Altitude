# 执行摘要

本方案提出一个**三层次**的文本分析框架，用于从低空旅游评论中**结构化提取主题–情绪–机制**信息。第一层（Layer1）聚焦发现语料中的**细粒度情绪本体**：以NRC八大情绪为基准，通过语料驱动方法（如句向量聚类）挖掘出领域特有的情绪（例如敬畏*awe*、释然*relief*、兴奋*excitement*等），构建“8+3”情绪词典。第二层（Layer2）进行**感知对象（Aspect）与情绪对映**：识别评论中的评价对象（如“安全性”“导游”），并标注对应情绪；这相当于典型的细粒度情感分析（Aspect-Based Sentiment Analysis）。第三层（Layer3）则是**情绪-机制-转化**编码：追踪评论中情绪产生与变化的因果路径，例如“初始恐惧→导游解释→释然”，并记录触发事件和参与者。此多阶段流程既融入**定性分析**（开放编码建码本、人工标注）又结合**LLM辅助**标注和机器学习，实现高效可重复。最终产出结构化数据，回答“游客在评价什么，产生了什么情绪，情绪因何而变”的研究问题。方案给出了完整的工程实现细节、评估指标、标注规范和示例输出，确保结果可复现和可解释。

**关键决策点与备选方案**：

| 决策点                 | 备选方案（Alternatives）                                 | 说明与权衡                                                                                                                                                   |
|----------------------|----------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **情绪类别划分**        | NRC 8类；扩展为“8+3”；更细粒度（>11类）；多维连续量 | NRC情绪词典提供8种基础情绪；本领域语料可能存在“敬畏”“释然”“兴奋”等NRC未覆盖情绪。扩展为“8+3”在兼顾可比性的同时更灵活。更多类别可深入捕捉语料特征，但标注难度和稀疏性上升。             |
| **分句/切分策略**      | 整条句；标准句分割；细分子句/短语             | 直接以句为单位简洁，但可能遗漏并列和转折。对转折句需识别“but, however”等，分成两部分标注。也可基于句法/依存分割子句。权衡：粒度越细，上下文信息越少；粒度粗涵盖更多语义。建议结合句号与连词双重切分。 |
| **聚类算法**          | K-Means；HDBSCAN；BERTopic；LDA等            | KMeans简单易实现，但需指定簇数。HDBSCAN基于密度，无需预设类别数，能识别噪声和不规则簇；BERTopic以SBERT句向量+UMAP+HDBSCAN生成主题，可自动提取关键词短语。本方案倾向基于**Transformer句向量**的HDBSCAN/BERTopic聚类，以发现语料驱动情绪类别。 |
| **情绪发现方法**        | 词典查词；主题模型；聚类主题诱导            | 词典方法（NRC/VADER）覆盖面窄且固定，不适合新情绪探索。主题模型（LDA）可生成主题词，但难以与情绪直观对应。基于句嵌入的聚类更能捕捉上下文语义。可尝试多种嵌入（SBERT等）和聚类，对比稳定性。                           |
| **标注方式**          | 完全人工；LLM零/少样本；混合半自动             | 纯人工精度高但代价大；完全LLM易迅速产出，但易出错。结合LLM自动标注+人工校验（人机协作）可兼顾效率和质量。准备用LLM生成候选标注，再人工复核一致性。                          |
| **模型/方法选择**      | 序列标注(BiLSTM-CRF/BERT)；Span提取；分类      | 情绪标签、机制等都可视为序列标注（token级）或阅读理解式span提取任务。SpanBERT专为span任务设计，适合提取事件。分类适用于整体句子情绪。多任务学习可联合预测多字段，或分步pipeline。                                    |
| **混合情绪处理**       | 强制选择单一情绪；允许多标签/共存；增强模型识别 | 许多评论含双情绪（恐惧与敬畏并存）。严格单标签会扭曲信息，需允许**多情绪或双极度表达**。模型可以输出多个关键词/标签，或给出主体情绪+副情绪。在标注时专门记录“混合/共存”案例以便后续分析。                              |
| **模型解释性**        | 黑盒模型；SHAP等解释；人工审查           | 黑盒模型高准确但难解释。引入SHAP等模型解释工具可以理解特征贡献。关键抽取结果需可追溯上下文。建议在模型输出后增加人工审查步骤及可视化（如attention heatmap、SHAP图），提升可信度。                           |
| **输出格式**          | 简单CSV；结构化JSON/Parquet；数据库        | 细粒度信息多字段多层结构，推荐**JSON/Parquet**（可嵌套字段）。也可留备份CSV用于审阅。JSON schema利于存储复杂结构（Aspect-Emotion-Mechanism链）。CSV可备作审查对照。                                      |

## 研究目标与问题

- **Layer1（情绪本体发现）**：在NRC八种基础情绪基础上，利用语料驱动方法发现潜在的细粒度情绪类别（例如**敬畏*Awe**、**释然*Relief**、**兴奋*Excitement**等），构建“8+3”情绪编码体系。研究问题：低空旅游评论中有哪些主要情绪类别？哪些是NRC词典未覆盖的领域特有情绪？如何统计和语义验证新增情绪？  
- **Layer2（Aspect–Emotion映射）**：识别评论中的**评价对象（Aspect）**与对应**情绪状态**。例如评论中提到“导游”、“天气”、“机舱舒适度”等方面，每个方面可能触发不同的情绪。该层问题相当于面向对象的情感分析（ABSA），即“游客针对哪个对象表达了何种情绪”。输出样本字段：`Aspect`，`InitialEmotion`（针对该Aspect的情绪）。  
- **Layer3（Emotion–Mechanism编码）**：跟踪情绪的原因和变化机制。目标是提取评论中情绪**触发事件**、**参与者（Actor）**以及**情绪转化**。研究问题包括：产生某情绪的触发因素是什么？在对比/转折句中，情绪如何转变？例如：“起初感到焦虑→导游解释→最后释然”，可以表达为`Fear（Anxiety）→(Pilot explanation)→Relief`。此层关注因果和对比结构，如“but”/“however”前后情绪的差异。  
- **方法论**：我们采用**定性（开放编码）→Codebook→金标→LLM批量标注→模型训练**的多阶段流程，而非直接机器黑箱。首先人工抽样开放编码构建codebook，然后利用LLM辅助批注生成海量标签，再人工一致性检验保证质量。最终数据可用于统计分析和模型训练。各层之间逻辑串联：**Aspect 提取 → 情绪分类 → 机制提取 → 情绪过渡**，对应研究问题由浅入深，确保每步可审查验证。  

## 数据准备

- **原始字段**：需要的原始字段至少包括：`review_id`（唯一ID），`text`（评论全文），`rating`（评分），`date`，以及可能的`user_id`、`language`、`metadata`等。如TripAdvisor原始导出数据（CSV或JSON）中包含的列。  
- **预处理与清洗**：去除HTML标签/多余空白，统一大写小写，处理表情符号（可转为文本标签）。对于其他语言文本（若有）可翻译或剔除。删除过短或非旅游相关的评论（如过度简短或广告）。保留原始文本中能表现情绪的句子。  
- **句/子句切分**：首先基于标点符号（句号、感叹号、问号）做基础分句。对于存在“but/however/虽然/尽管/尽管如此”等转折连词的句子，应进一步拆分前后子句，以分别标注情绪和机制。如 “I was scared at first, but later I enjoyed the ride.”可分为“I was scared at first.”与“later I enjoyed the ride.”。可采用开源工具（NLTK、spaCy、HanLP等）或正则规则辅助切分。  
- **样本抽样方案**：为了构建codebook和金标集，需要**覆盖多样情绪**的样本。建议分层随机采样：包括高评分且含负面词（*高分潜在正面基调但潜在负面情绪*）和低评分高负面的评论，确保对比。比如优先采样评级4-5星但文本出现“紧张”、“害怕”的评论，以及低分评论中包含“安全”、“惊喜”的内容。这有助捕获情绪转化边界。初步规模可取1000-2000条用于探索和初步编码。

## 标注方案

- **开放编码→Codebook**：首先由研究者对抽样评论进行**开放编码**（Grounded Theory中的初步编码）。对每条评论按句/子句读取，分别标记出现的情绪、触发事件、Actor、情绪变化等概念，用原话或简短词语标记。多轮迭代后，将类似标签合并形成初始**编码表**。例如将“紧张”、“害怕”归为“焦虑/恐惧”，将“释然”、“平静”归为“安心/平静”。  
- **Codebook**：根据开放编码结果，整理生成**细粒度情绪词典**（初版“8+3”情绪类目，含定义、示例词）和**触发机制列表**。Codebook应明确每个情绪类别的定义、包含词汇、排除词汇，以及机制类别（例如“reassurance/安心”、“scenery reveal/景物震撼”等）。示例：情绪“Awe（敬畏）”可能包含“breathtaking, awe-inspiring”等场景词；“Relief（释然）”包含“at ease, calm”等。机制“Pilot explanation”定义为导游/飞行员做解释的事件。  
- **金标集规模**：可先使用约200–300条评论（含分句）进行全面标注，形成**Gold Standard**集。每条评论标注字段应包括：`aspect`、`initial_emotion`、`trigger`、`actor`、`mechanism`、`final_emotion`、`transition`（格式如“Anxiety→Relief”）和可选的`confidence`（标注者对判断信心）。建议至少2名标注者独立标注后计算Cohen’s κ进行一致性评估（目标κ>0.7）。对于有争议的样本，可进行集体讨论裁定（Adjudication）。整体标注规模可视资源扩大至500+条，以训练模型。  
- **标注界面/Schema**：可使用简单的JSON Schema或网络标注工具（如prod.ly，Label Studio）进行标注。关键字段（英语）示例如下：  

```json
{
  "review_id": "R001",
  "aspect": "Safety",
  "initial_emotion": "Anxiety",
  "trigger": "pilot explanation",
  "actor": "Pilot",
  "mechanism": "Reassurance",
  "final_emotion": "Relief",
  "transition": "Anxiety→Relief",
  "confidence": 0.9
}
```  

- **示例与边界案例**：  

  1. **典型案例**：评论“I was nervous at first, but the pilot explained everything and put me at ease.”标注为  
     - Aspect: Safety；InitialEmotion: Anxiety；Trigger: “pilot explained everything”；Actor: Pilot；Mechanism: Reassurance；FinalEmotion: Relief；Transition:“Anxiety→Relief”。  
  2. **多情绪共存**：评论“虽然一开始很害怕，但看到冰川景色后惊叹不已。”表示Fear和Awe并存，可标注为  
     - Aspect: Scenery；InitialEmotion: Fear；Trigger: “看到冰川景色后”；Actor: Environment；Mechanism: AweElicitation；FinalEmotion: Awe；Transition:“Fear+Anticipation→Awe”。此类边界案例可打标签“mixed”。  
  3. **无明显转折**：评论“The ride was smooth and amazing.”基本全程正面，没有前后对比，可简化标注为单情绪“Amazing/Positive”，或标记Initial=Final=Joy且Mechanism为空。  
  4. **否定与强化**：“I wasn’t scared at all, actually I loved it.” 应标注InitialEmotion: Fear (negated by “wasn’t”)→FinalEmotion: Excitement/Joy，Mechanism:“unexpected enjoyment”。  
  边界案例强调对转折词（but, however, 虽然, 但）和混合情绪（“既..又..”）的特殊处理。  

## LLM辅助标注流程

- **Prompt设计**：针对需要标注的每条评论，构造提示引导LLM输出指定字段JSON。**零样本**Prompt可说明字段要求，如：  
  ```
  提示（零样本）：
  请阅读下面的旅游评论，将其转换为如下JSON格式：{"aspect":..., "initial_emotion":..., "trigger":..., "actor":..., "mechanism":..., "final_emotion":..., "transition":...}。
  评论: "I was nervous at first, but the pilot explained everything and put me at ease."
  输出格式示例：{"aspect": "Safety", "initial_emotion": "Anxiety", "trigger": "pilot explained everything", "actor": "Pilot", "mechanism": "Reassurance", "final_emotion": "Relief", "transition": "Anxiety→Relief"}
  请给出上述评论对应的JSON标注结果。
  ```  
  **少样本**Prompt可在开头加入1-2个示例标注对照，帮助模型理解格式。例如：  
  ```
  示例:
  评论: "The scenery was breathtaking and thrilling."
  输出: {"aspect": "Scenery", "initial_emotion": "Anticipation", "trigger": "scenery was breathtaking", "actor": "Environment", "mechanism": "AweInduction", "final_emotion": "Excitement", "transition": "Anticipation→Excitement"}
  现在评论: "I was nervous at first, but the pilot explained everything and put me at ease."
  输出: 
  ```  
- **批量标注策略**：将提示和评论列表组合使用OpenAI Chat API（如GPT-4）生成候选标注。可一次批处理多条，或逐条交互式调用。需设置温度较低保证一致性。建议每条评论生成多次不同回答，然后过滤或融合（取最高置信解析）。  
- **人工校验**：对LLM输出的JSON进行人工抽样验证。主要检查字段完整性（是否漏标Aspect/actor等）、标签正确性、格式合法性。对于高置信的结果，可少数人复审确认；对于LLM感到不确定或冲突的样本，需人工重标注。计算标注者间一致性，例如Cohen’s κ，如果LLM+人工模式下κ足够高，则视为可接受。存在较大差异的样本留作未解决案例，可能需要更多提示或手动标注。  
- **质量控制**：建立审计日志（如LLM输出与最终标注的对比），监控错误类型（如情绪错标、漏标Aspect）。利用**Adjudication**会议统一歧义定义。统计Kappa等指标作为标注质量度量（目标 >0.7）。定期随机抽检确保LLM未系统性偏误。对于极少数LLM错误典型情形（如长句复杂句），可以针对性增加Prompt示例或改进tokenization。

## 情绪发现方法

- **句/文本表示**：使用现代**Transformer-based 句向量模型**将评论或句子编码为向量。推荐使用Sentence-BERT（SBERT）等预训练模型（如`sentence-transformers/all-MiniLM-L6-v2`），因其经siamese架构优化后能生成适合聚类的语义嵌入。也可尝试DeBERTa或RoBERTa生成[CLS]向量。将所有句子向量化作为后续聚类输入。  
- **降维与聚类**：由于句向量维度高，可先用PCA或UMAP降维到50-200维，再聚类。聚类算法上，**HDBSCAN**是一种基于密度的聚类算法，能自动确定簇数并识别噪声点；**BERTopic**则结合SBERT嵌入、UMAP和HDBSCAN，最后用c-TF-IDF提取关键词，便于解释。可实验K-Means（需预设簇数）和HDBSCAN对比：HDBSCAN适合发现不规则簇且对噪声鲁棒；K-Means收敛快但对异常敏感。  
- **情绪簇稳定性分析**：尝试不同参数（如HDBSCAN的`min_cluster_size`）和随机种子进行多次聚类，比对情绪簇的一致性。可采用下采样或bootstrapping算出簇稳定性（例如AMI互信息、簇纯度）指标。若某簇稳定出现且词汇一致性高，则可提炼为候选情绪类别。  
- **代表性短语抽取**：对于每个聚类，提取**簇中心句子**和**高频关键词/短语**（可用c-TF-IDF或Phrase Extraction）。这些短语提示该簇情绪倾向，例如“**so thrilled**”, “**filled with awe**”等。结合语境由研究者或LLM为簇命名（如“Excitement/Awe”）。  
- **新增情绪判定**：统计聚类中出现超过N次（如>50个句子）的独特情绪词，如“Awe-inspiring”、“felt relieved”等，如果这些词高频且语义与现有8类有明显差异，则作为新增类证据。还可查看情绪强度词典（NRC Intensity）或用户评分关联（如这类评论中高评分频率）辅助判断语义合理性。最终仅保留语料中**自然涌现且语义清晰**的新增情绪。

## 情绪与机制提取模型

- **任务定义**：可视作**多字段抽取任务**。可用序列标注（每个token标注对应字段标签）、跨度提取或分类方式：
  - **序列标注**：为每个token标注BIO类别（Aspect/Trigger/Actor/Emotion等），适合实体提取式。模型如BERT+CRF、BiLSTM-CRF或基于Transformers的token-classifier。需自定义标签集（例如`B-Aspect, I-Aspect, B-Trigger,...`）。  
  - **跨度提取**：将Trigger、Actor等设为span预测任务（类似问答），可用SpanBERT或BERT QA模型，对输入问题“找到Trigger”进行预测。SpanBERT通过预训练更擅长预测连续文本块。  
  - **分类**：如果已知道Aspect词汇（如词典给定），则对每个句子分类情绪和转移类型；但Aspect提取仍需要NER型处理。  
  多任务学习也可采用，将上述任务共享Transformer底层，例如联合训练Aspect分类与情绪分类。注意避免任务冲突，交替或对每层加权loss。  

- **候选模型**：  
  - *BERT*（Devlin et al. 2019）为基础，可选中文模型（如bert-base-chinese）或英文（bert-base-uncased）。  
  - *DeBERTa*（Peng He et al. 2020）为BERT改进版，使用解耦注意力和增强掩码解码器，效果优于RoBERTa。适用情绪分类等。  
  - *SpanBERT*（Joshi et al. 2019）专为span任务设计，通过随机遮盖文本块提升span理解。适用于触发事件抽取。  
  - *SpanBERT或RoBERTa_mention*：专注实体与关系，可用于Mechanism抽取。  
  - *大型LLM*：GPT-4等可以用于提示抽取，但成本高、不易大规模运行，适合作少样本辅助标注或最终校验。  
  根据标注任务属性选择：如事件触发、Actor可用SpanBERT；情绪分类可以用DeBERTa或BERT序列分类。

- **Loss设计**：如果多任务，可结合交叉熵损失。如Aspect识别和Trigger识别分别计算Loss。可加权调整难易。若类别不平衡（某些情绪少），加权loss或数据采样平衡。标注置信度可以用于soft labeling。  
- **混合情绪**：采用多标签分类或并列Span标注。例如允许同一文本标记多个`Emotion`标签（co-existing）。模型可以输出Top-2情绪分数，人工判定是否“mixed”。对含转折的句子，模型应预测两端情绪，如“恐惧”和“敬畏”。可通过添加标签“MixedEmotion”或预测关系边来表示。  

## 情绪转化检测

- **对比/转折识别**：首先通过**关键词（但, 然而, although, despite, after, finally 等）**和依存句法标记检测语义转折点。可以使用正则或语言模型（如spaCy）找出句中承接词和句子结构。  
- **前后情绪对齐**：对于包含转折的句子，分别提取前文（source）和后文（target）的情绪字段（或者句子级情绪）。在已标注数据中，一般通过观察已提取的`initial_emotion`和`final_emotion`构建转化对。  
- **转换矩阵**：自动统计数据集中**source→target**频率矩阵。例如统计“Fear→Relief”、“Anxiety→Excitement”等高频对。对角线上的未转换（如“Fear→Fear”）也统计，用于发现常见不变模式。  
- **自动规则+学习**：可初步用关键词规则（含转折词+情绪字词）标记一些转换实例，生成训练集。随后可训练监督模型（例如分类前后情绪对）来发现更多模式。  
- **置信度与不确定样本**：对每个自动识别的转换赋予置信度（例如LLM生成时的概率，或模型软max差值）。低置信的实例或无法确定的混合案例（如并列结构“又...又...”）留存为待人工审核或后续标注。避免对难判样本强行贴标签。  

- **示例流程图（Mermaid）**：以下是一个情绪转化示例的流程图：  
```mermaid
flowchart LR
    Fear[恐惧 (Anxiety/Fear)] -->|Pilot解释| Relief[释然 (Relief)]
    Disappointment[失望 (Disappointment)] -->|公司补偿/安抚| Satisfaction[满意 (Satisfaction)]
    Fear -->|观景/震撼| Awe[敬畏 (Awe)]
    ```  

## 评估方案

- **数据划分**：将数据划分为训练集/验证集/测试集（例如70/15/15）。尤其金标集需留出测试用。对于情绪发现（无监督）可用全部数据；对于有监督模型，验证集用于调参。确保各集情绪分布均衡。  
- **评估指标**：  
  - **字段准确度**：Precision/Recall/F1用于评估**情绪和机制标签**。若做序列标注，则以每个token或span为单位计算F1（例如实体识别常用）。  
  - **Span IoU**：评价抽取的触发事件/Actor/Mechanism等span与人工标注的重叠度（交并比）。IoU≥0.5可算命中。  
  - **Transition准确度**：预测的初始→最终情绪对比真实对的准确率。  
  - **聚类纯度**：对于Layer1，无监督聚类结果可用簇纯度或NMI评估（与人工归类的情绪标签对比）。还可做人工检验：每个簇抽样验证主题一致性。  
  - **标注一致性**：人工标注时计算Cohen’s κ；自动标注后也可用部分金标计算其与人工标注的一致度。  
- **基线与消融**：使用传统情感工具作为基线，如**VADER**或**NRC词典统计**查看能标注出的情绪粒度；ABSA模型（如开源Aspect模型）比较 Aspect-情绪对识别。消融实验可移除LLM辅助（纯人工或纯模型标注）比较效果差异；或比较有无新增3类情绪的效果。  
- **评估报告**：最终给出各项指标（精确率、召回率、F1、IoU）以及转换矩阵和簇分析结果，对比基线说明改进。如有时间可用人群注释评估模型输出的合理性。

## 工程实现

- **代码目录结构**：建议如下模块化布局：  
  ```
  project-root/
  ├─ data/                  # 原始和处理后数据
  ├─ notebooks/             # 分析探索笔记本
  ├─ src/
  │   ├─ preprocess.py      # 数据清洗、句子切分
  │   ├─ embeddings.py      # 句向量生成与缓存
  │   ├─ clustering.py      # 聚类与情绪发现
  │   ├─ annotation.py      # LLM调用及格式化
  │   ├─ train_model.py     # 训练序列标注/分类模型
  │   ├─ extract_transition.py # 转换检测算法
  │   └─ utils.py           # 公用函数（加载数据、评估函数）
  ├─ models/                # 保存预训练模型和权重
  ├─ outputs/               # 结果输出（CSV/JSON）与日志
  ├─ config.yaml            # 路径和参数配置
  ├─ requirements.txt       # 依赖列表（transformers、sklearn、hdbscan等）
  └─ README.md
  ```  
- **依赖环境**：Python 3.8+，主要库包括：`transformers`（HuggingFace）、`sentence-transformers`、`torch`、`hdbscan`、`umap-learn`、`scikit-learn`、`pandas`、`numpy`、`openai`（如果用API）等。  
- **随机种子**：全局设置随机种子（NumPy、PyTorch、torch.manual_seed）保证结果可重复。  
- **Embedding缓存**：生成句向量耗时，可一次批量生成并保存（如pickle或Torch的`.pt`文件）。下次运行直接加载，避免重复计算。示例伪代码：  
  ```python
  from sentence_transformers import SentenceTransformer
  model = SentenceTransformer('all-MiniLM-L6-v2')
  if not cached:
      embeddings = model.encode(sentences, show_progress_bar=True)
      np.save('embeddings.npy', embeddings)
  else:
      embeddings = np.load('embeddings.npy')
  ```  
- **关键函数示例**：  
  - **嵌入生成**：  
    ```python
    def encode_sentences(sent_list, model_name='all-mpnet-base-v2'):
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer(model_name)
        return model.encode(sent_list, show_progress_bar=True)
    ```  
  - **LLM批注调用**（OpenAI API示例）：  
    ```python
    import openai
    openai.api_key = 'YOUR_KEY'
    def annotate_with_gpt(review_text, prompt_template):
        prompt = prompt_template.replace("{text}", review_text)
        response = openai.ChatCompletion.create(
            model="gpt-4", 
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        return response.choices[0].message.content
    ```  
  - **聚类与关键词提取**（BERTopic示例）：  
    ```python
    from bertopic import BERTopic
    topic_model = BERTopic(embedding_model="paraphrase-MiniLM-L6-v2")
    topics, probs = topic_model.fit_transform(documents)
    # 查看主题词
    for i in range(5):
        print(f"Topic {i}:", topic_model.get_topic(i))
    ```  
  - **情绪抽取模型训练**：使用`transformers`加载BERT类模型进行token分类，关键示例：  
    ```python
    from transformers import BertTokenizerFast, BertForTokenClassification, Trainer, TrainingArguments

    tokenizer = BertTokenizerFast.from_pretrained('bert-base-uncased')
    model = BertForTokenClassification.from_pretrained('bert-base-uncased', num_labels=num_labels)
    # 构造Trainer训练模型（略）
    ```  

- **单元测试与日志**：为关键函数编写单元测试，如“给定一句话是否正确切分子句”、“标签输出格式是否符合JSON Schema”。记录每步输出至日志文件，确保中间结果可追溯。  
- **输出格式**：最终结构化结果保存为JSON或Parquet，每条记录包含所有字段。并导出CSV供快速查看。例如示例CSV列：`review_id, aspect, initial_emotion, trigger, actor, mechanism, final_emotion, transition, confidence`。  

## 运行计划与时间表

按照阶段划分，结合人力估计（假设1人/天含思考与编码）：  

1. **数据准备（5天）**：收集/清洗低空旅游评论（1天），句子/子句切分（1天），样本抽样（1天），构建初步情绪词典（2天）。  
2. **开放编码与Codebook（7天）**：开放编码抽样评论（3天），整理合并标签（2天），制定情绪与机制Codebook（2天）。  
3. **Gold标准标注（10天）**：组织多名标注者训练后标注样本（7天），计算一致性并调整（3天）。  
4. **LLM辅助批注（5天）**：设计Prompt并批量生成候选标注（2天），人工校验与修正（3天）。  
5. **情绪发现与聚类（7天）**：训练句向量（1天），不同算法聚类实验（KMeans/HDBSCAN/BERTopic）（3天），聚类稳定性与主题提取（2天），确定新增情绪类（1天）。  
6. **模型训练与优化（10天）**：实现序列标注/Span提取模型，训练调参（7天），对结果做初步评估（3天）。  
7. **Emotion Transition检测（5天）**：开发对比连词检测与情绪匹配算法（3天），输出转换矩阵与示例（2天）。  
8. **评估与报告（5天）**：完成定量评估、消融分析（3天），撰写报告与可视化（2天）。  
9. **整合与复现准备（3天）**：整理代码仓库、README、环境文件，准备交付物（数据、模型、文档）。  

**总计约50人日**，具体可并行部分任务（如标注可多人协作），时间可适当压缩。  

## 风险与伦理

- **LLM错误与偏见**：LLM可能产生不一致或虚构输出，需要人工校验。对话模型也可能带有性别/文化偏见，需要关注标注内容是否公平、低空旅游场景中中立。通过多样化提示和增加对抗样本检测偏差。  
- **隐私**：遵守数据使用规范，评论若含个人信息（极少见），需删除。标注时注意隐私合规。  
- **标注一致性**：情绪和机制标注有主观性。通过详细Codebook、培训标注者、交叉标注和κ统计等控制一致性。对模糊案例允许标记“uncertain”并留审议。  
- **可解释性**：避免全黑箱。引入人为介入和可视化（如SHAP解释模型决策）提升透明度。尤其情绪与机制类型的解释，确保可由专家复查。  

## 输出物

- **代码仓库**：完整Python代码、依赖说明（requirements.txt）、配置文件、README（包含运行指南）。  
- **数据集**：原始收集数据（若允许共享），清洗后样本，以及Gold标注JSON/CSV。  
- **模型检查点**：训练好的情绪抽取模型（BERT/SpanBERT等权重），可在附录说明加载方式。  
- **评估报告**：包含实验结果、指标汇总、消融分析。  
- **可视化**：情绪聚类可视化图（如UMAP散点图或词云）、转换矩阵热图（Emotion Transition Matrix）、示例流程图（如上Mermaid示例图）。  

以上内容形成可复现的项目成果，满足从代码到文档的完整交付。  

## 示例与Prompt模板

- **示例JSON输出**（字段说明同上）如：  
  ```json
  {
    "review_id": "R045",
    "aspect": "Safety",
    "initial_emotion": "Anxiety",
    "trigger": "weather delay",
    "actor": "Weather",
    "mechanism": "Expectation Disruption",
    "final_emotion": "Disappointment",
    "transition": "Anxiety→Disappointment",
    "confidence": 0.85
  }
  ```  
- **标注示例**（文本→字段）：  

  1. 文本：“I was anxious until the pilot explained the procedure.”  
     标注：Aspect=Safety，InitialEmotion=Anxiety，Trigger=“pilot explained the procedure”，Actor=Pilot，Mechanism=Reassurance，FinalEmotion=Relief，Transition=“Anxiety→Relief”。  

  2. 文本：“The flight was scary at first; later the scenery amazed me.”  
     标注：Aspect=Scenery，InitialEmotion=Fear，Trigger=“scenery amazed me”，Actor=Environment，Mechanism=AweInduction，FinalEmotion=Awe，Transition=“Fear→Awe”。（混合情绪示例）  

  3. 文本：“价格有点高，但整体体验很值。”  
     标注：Aspect=Price，InitialEmotion=Disappointment，Trigger=“整体体验很值”，Actor=Overall Experience，Mechanism=价值重估，FinalEmotion=Satisfaction，Transition=“Disappointment→Satisfaction”。  

- **Emotion Transition Mermaid图示例**：见上文**情绪转化检测**部分提供的流程图。

- **LLM提示模板**：  

  - *Zero-shot 示例*：  
    ```
    任务：从旅游评论中提取目标对象(Aspect)、初始情绪(InitialEmotion)、触发事件(Trigger)、行为者(Actor)、机制(Mechanism)、最终情绪(FinalEmotion)及情绪转移(Transition)，输出JSON。
    评论: "{text}"
    请严格按照格式{"aspect":..., "initial_emotion":..., "trigger":..., "actor":..., "mechanism":..., "final_emotion":..., "transition":...}返回结果。
    ```  

  - *Few-shot 示例*：  
    ```
    以下是几个示例，帮助理解输出格式：
    评论: "We were terrified when the helicopter hit turbulence, but the pilot soothed our nerves."
    输出: {"aspect": "Safety", "initial_emotion": "Fear", "trigger": "pilot soothed our nerves", "actor": "Pilot", "mechanism": "Reassurance", "final_emotion": "Calm", "transition": "Fear→Calm"}

    评论: "The ride had some scary moments, yet in the end it was absolutely exhilarating."
    输出: {"aspect": "Thrill", "initial_emotion": "Fear", "trigger": "the end it was absolutely exhilarating", "actor": "Overall Experience", "mechanism": "Threat Reappraisal", "final_emotion": "Excitement", "transition": "Fear→Excitement"}

    现在评论: "{text}"
    输出:
    ```  

以上提示模板可直接用于调用LLM批量生成标注。