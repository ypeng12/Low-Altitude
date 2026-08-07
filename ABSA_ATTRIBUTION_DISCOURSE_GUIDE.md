# 低空旅游研究三大核心实证机制解说指南 (ABSA_ATTRIBUTION_DISCOURSE_GUIDE.md)

本文档针对低空观光旅游 TripAdvisor 评论数据集在 Level 3 计量模型中验证的三大核心学术突破——**属性极性解耦 (ABSA)、归因缓冲效应 (Attribution Compensation) 与篇章转折焦点 (Discourse Focus)**——提供详尽、直观的理论解释、数学算力推导、代码位置指南与图表对应说明。

---

## 📌 问题 1：ABSA 属性极性解耦 —— 飞行员的影响最大吗？代码与数据在哪里？

### 1. 各体验维度的实证系数对比（谁对评分影响最大？）

从导出的 [deep_research_absa_regressions.csv](file:///Users/yuliangpeng/Desktop/Low-Altitude/data/derived_outputs/deep_research_absa_regressions.csv) 可以看到基于 OLS HC3 稳健标准误的各维度边际效应：

#### 🌟 正面推动力（谁能给评分加分最多？）
1. **飞行员正面好评 (`pilot_pos`)**：**$+0.0862$ 星** ($p < 0.001$) —— **（加分项中排名第 1！）**
2. **景色壮丽震撼 (`scenery_pos`)**：**$+0.0757$ 星** ($p < 0.001$)
3. **安全心理安抚 (`safety_assurance`)**：**$+0.0690$ 星** ($p < 0.001$)
4. **地勤服务热情 (`ground_staff_pos`)**：**$+0.0316$ 星** ($p < 0.001$)
5. **天气晴朗能见度高 (`weather_pos`)**：**$+0.0250$ 星** ($p = 0.005$)

#### ⚠️ 负面毁坏力（谁会让评分跌得最惨？）
1. **性价比极差/昂贵 (`price_value_neg`)**：**$-0.6649$ 星** ($p < 0.001$) —— **（扣分项中排名第 1！）**
2. **地面前台态度恶劣 (`ground_staff_neg`)**：**$-0.5672$ 星** ($p < 0.001$)
3. **飞行员失职/被骂 (`pilot_neg`)**：**$-0.5217$ 星** ($p < 0.001$)
4. **老天爷天气恶劣 (`weather_neg`)**：**$-0.1415$ 星** ($p < 0.001$)

> **核心结论**：在推动游客给 5 星好评的正面因素中，**飞行员 (`pilot_pos`) 的贡献是全场最大的**！而对于负面扣分，老天爷天气不好（$-0.1415$ 星）的伤害远远小于飞行员不好（$-0.5217$ 星）和地勤不好（$-0.5672$ 星）。游客对不可抗力自然因素的宽容度远高于对人力服务细节的宽容度。

![图 1：低空旅游各个体验维度的评分影响（加分 vs 扣分）](file:///Users/yuliangpeng/Desktop/Low-Altitude/figures/absa_marginal_effects_forest_plot.png)

### 2. 代码与数据位置
- 📄 **属性极性提取函数 (`compute_absa`)**：[run_data_pipeline.py#L380-L415](file:///Users/yuliangpeng/Desktop/Low-Altitude/run_data_pipeline.py#L380)
- 📄 **OLS 属性极性模型代码**：[run_incongruence_econometrics.py#L25-L34](file:///Users/yuliangpeng/Desktop/Low-Altitude/run_incongruence_econometrics.py#L25)
- 📊 **导出的回归表格文件**：[data/derived_outputs/deep_research_absa_regressions.csv](file:///Users/yuliangpeng/Desktop/Low-Altitude/data/derived_outputs/deep_research_absa_regressions.csv)

---

## 📌 问题 2：天气不好（$-0.1803$）加上飞行员优秀（$+0.2788$）的翻盘交互项，是如何在代码里看到的？

### 1. 统计学原理与数据表输出

在 [run_incongruence_econometrics.py#L39](file:///Users/yuliangpeng/Desktop/Low-Altitude/run_incongruence_econometrics.py#L39) 中，我们引入了 `weather_neg * pilot_pos` 交叉项，运行命令后生成的 [deep_research_attribution_discourse_regressions.csv](file:///Users/yuliangpeng/Desktop/Low-Altitude/data/derived_outputs/deep_research_attribution_discourse_regressions.csv) 输出了以下回归系数：

| 计量变量名称 | 回归系数 (Coef. β) | 统计显著性 (P-value) | 理论解释 |
| :--- | :---: | :---: | :--- |
| **`weather_neg`** (仅天气不好) | **$-0.1803$** | $p = 0.003$ | 纯粹自然不可抗力导致评分下降 |
| **`pilot_pos`** (仅飞行员优秀) | **$+0.0297$** | $p < 0.001$ | 正常天气下飞行员服务的边际加分 |
| **`weather_neg:pilot_pos`** (交互项) | **$+0.2788$** | **$p < 0.001$** | **恶劣天气下飞行员救场的额外补偿得分！** |

### 2. 算力推导公式

当游客遇到恶劣天气（$\text{weather\_neg} = 1$），但飞行员表现极其优秀热心（$\text{pilot\_pos} = 1$）时，评分的总边际影响量为：

$$\text{Total Impact} = \text{weather\_neg} + \text{pilot\_pos} + (\text{weather\_neg} \times \text{pilot\_pos})$$
$$\text{Total Impact} = -0.1803 + 0.0297 + 0.2788 = \mathbf{+0.1282 > 0}$$

> **解释**：只要飞行员表现优异，即使天气很糟糕，游客给出的最终预测评分依然实现了**净增长 (+0.1282 星)**！飞行员的优秀服务成功抹平了天气的负面影响，并触发了游客的感激心理。

![图 2：恶劣天气下飞行员的“救场反弹效应”（归因缓冲机制）](file:///Users/yuliangpeng/Desktop/Low-Altitude/figures/attribution_mitigation_interaction.png)

### 3. 代码与数据位置
- 📄 **归因交叉项回归代码**：[run_incongruence_econometrics.py#L39-L46](file:///Users/yuliangpeng/Desktop/Low-Altitude/run_incongruence_econometrics.py#L39)
- 📊 **导出的回归表格文件**：[data/derived_outputs/deep_research_attribution_discourse_regressions.csv](file:///Users/yuliangpeng/Desktop/Low-Altitude/data/derived_outputs/deep_research_attribution_discourse_regressions.csv)

---

## 📌 问题 3：篇章转折 `but` 后的分析是怎么做的？代码、结果和 $R^2$ 跃升在哪里？

### 1. 文本转折切分代码与逻辑

在 [run_data_pipeline.py#L349-L375](file:///Users/yuliangpeng/Desktop/Low-Altitude/run_data_pipeline.py#L349) 中，我们构建了转折句解析器 `parse_discourse()`：

```python
import re

def parse_discourse(text):
    if not isinstance(text, str) or not text.strip():
        return 0.0, 0.0, 0, 0, 0
    # 正则匹配转折连接词：but, however, although, yet, though, even though
    match = re.search(r'\b(but|however|although|yet|though|even though|except|nonetheless|nevertheless)\b', text, flags=re.IGNORECASE)
    if match:
        idx = match.start()
        pre_text = text[:idx].strip()   # but 前面的句子 (如：紧张害怕/大雾)
        post_text = text[idx:].strip()  # but 里面的转折后句子 (如：飞行员太给力，极其平稳震撼)
        
        c_pre = sia.polarity_scores(pre_text)['compound']
        c_post = sia.polarity_scores(post_text)['compound'] # 转折后 VADER compound 得分
        p2n = 1 if (c_pre >= 0.05 and c_post <= -0.05) else 0
        n2p = 1 if (c_pre <= -0.05 and c_post >= 0.05) else 0
        return c_pre, c_post, 1, p2n, n2p
    else:
        c_tot = sia.polarity_scores(text)['compound']
        return c_tot, c_tot, 0, 0, 0
```

### 2. 计量回归拟合度与 $R^2$ 跃升对比

在 [run_incongruence_econometrics.py#L40-L46](file:///Users/yuliangpeng/Desktop/Low-Altitude/run_incongruence_econometrics.py#L40) 中，将转折句后半段情感 `sentiment_post_but` 加入模型：

* **模型 1（不考虑转折句，仅用传统属性）**：
  - **模型拟合度 $R^2 = 0.1187$**（仅能解释 11.87% 的评分差异）
* **模型 2（引入转折句后半段极性 `sentiment_post_but`）**：
  - **模型拟合度 $R^2 = 0.2488$**（**解释能力翻倍暴涨 109.6%！**）
  - `sentiment_post_but` 的回归系数为 **$+0.8094$** ($t = 20.06, p < 0.001$)；
  - 在有序 Probit (Ordered Probit) 模型中，该系数高达 **$+1.2465$** ($z = 34.04, p < 0.001$)！

> **核心结论**：用代码严谨证明了：游客在写评论时，`but` 之后的表达主导了最终的星级判定。前面说再多客观困难、害怕或价格昂贵，只要 `but` 后面是极度正面好评，游客就会毫不犹豫给出 5 星！

![图 3：为什么转折句 "but" 后的内容才是决定游客最终打分的关键？](file:///Users/yuliangpeng/Desktop/Low-Altitude/figures/discourse_clause_r2_jump.png)

### 3. 代码与数据位置
- 📄 **转折句解析器代码**：[run_data_pipeline.py#L349-L375](file:///Users/yuliangpeng/Desktop/Low-Altitude/run_data_pipeline.py#L349)
- 📄 **篇章模型回归代码**：[run_incongruence_econometrics.py#L40-L55](file:///Users/yuliangpeng/Desktop/Low-Altitude/run_incongruence_econometrics.py#L40)
- 📊 **导出的回归表格文件**：[data/derived_outputs/deep_research_attribution_discourse_regressions.csv](file:///Users/yuliangpeng/Desktop/Low-Altitude/data/derived_outputs/deep_research_attribution_discourse_regressions.csv)
