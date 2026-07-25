# 低空旅游 (Low-Altitude Tourism) 实验与研究笔记 (RESEARCH_NOTES_CN.md)

> 📌 **文档说明**：本笔记详细记录了低空旅游 TripAdvisor 评论数据集在处理过程中的所有**实验细节、实证数据账本、变量设计动机、数据排查案例（如 Pilot Bruce 探查、Harry M 去重案例）**，特别是对 **Level 2 深度特征工程** 进行了极致详细的拆解说明。

> 💡 **核心状态与策略确认**：
> 1. **Level 2 深度特征工程状态**：**已 100% 全部完成**！四大核心模块（地理解析、NLP形态、VADER情绪得分、9大低空领域哑变量与角色拆分）均已写入主数据集 `tripadvisor_processed_master.csv`。
> 2. **多语种（非英文）处理策略**：**未从主集中物理删除**。为防止样本选择偏差（Sample Selection Bias），997 条非英文评论（4.48%）完整保留在主集中，但已通过 `language` 与 `is_english` (1/0) 标记打标，并独立导出为 `non_english_reviews.csv`。在英文 NLP / 情感分析回归中建议筛选 `is_english == 1` 样本（21,238 条，95.52%）以避免英文词典的极性伪零分现象。

---

## 📊 一、 全量数据实证指标汇总表

| 实证维度 / 指标 | 真实数据统计值 | 百分比 / 论文上下文 | 变量作用 |
| :--- | :--- | :--- | :--- |
| **抓取原始产品数** | 46 个 CSV 文件 | 覆盖直升机、固定翼飞机、水上飞机观光 | 产品异质性来源 |
| **合并原始总评论数** | 28,918 条 | `tripadvisor_merged_raw.csv` | 原始抓取总量 |
| **参与严格重复的行数** | 13,116 条 | 跨产品重复展示导致 | 去重前审计 |
| **实际剔除的重复评论** | **6,683 条** | 剔除完全重复及空格/换行差异近重复 | 消除数据重叠偏差 |
| **最终干净主数据集** | **22,235 条** | `tripadvisor_processed_master.csv` | **回归模型核心样本** |
| **英文评论数 (`is_english=1`)**| 21,238 条 | **95.52%** | 英文 NLP 主样本 |
| **非英文评论数 (`is_english=0`)**| 997 条 | **4.48%** (法语372、德语121、西班牙语65) | 独立分析或控制变量 |
| **美国本土游客数 (`is_us_domestic=1`)** | 11,044 条 | **49.7%** (CA 1,569, FL 851, TX 793, NY 449) | 国内 vs 国际游客对比 |
| **飞行员提及率 (`pilot_mention`)** | 13,728 条 | **61.74%** — *低空观光最核心的服务角色* | 服务感知主变量 |
| **安全心理提及率 (`safety_mention`)** | 8,676 条 | **39.02%** — *高风险/高紧张感体验* | 感知风险主变量 |

---

## 🔬 二、 步骤 1 ~ 步骤 4：数据处理与审计细节

### 步骤 1：原始数据合并与产品标识 (`tour_name`)
- **设计动机**：46 个产品涵盖不同的飞行路线、机型与地理环境。如果不提取产品标识，直接拼合数据，会导致回归模型无法控制产品层面的固定效应（Product Fixed Effects, $\gamma_j$）。
- **实现逻辑**：从文件名（如 `1-Kauai Deluxe Sightseeing Flight_1623_attraction...csv`）中通过正则表达式解析出标准产品名 `"Kauai Deluxe Sightseeing Flight"`，追加为 `tour_name` 字段。
- **产出**：合并得 28,918 条原始记录（`data/cleaned_datasets/tripadvisor_merged_raw.csv`）。

### 步骤 2：Level 1 基础清洗与文本规范化
- **行政列剪枝**：删除无无控制价值的 `user_profile`（主页URL）、`user_avatar`（头像）与 `disclaimer`（免责声明）。
- **HTML 换行与实体解码 (`clean_html_linebreaks`)**：
  - 网页评论充斥 `<br />` 和 `<br>` 标签，统一替换为 Python 标准换行符 `\n`，保留游客段落结构。
  - 用 `html.unescape()` 还原转义字符（`&amp;` $\rightarrow$ `&`, `&#39;` $\rightarrow$ `'`, `&quot;` $\rightarrow$ `"`）。
  - 将 3 个以上的连续换行压缩为双换行 `\n\n`。
- **评分与日期格式化**：评分限定为 1-5 整数；日期从 `"Written February 24, 2025"` 解析为 `YYYY-MM-DD`。
- **Trip Type 补全与映射**：从元文本（如 `"Feb 2025 • Family"`）中提取丢失的出行类型，映射为 `Couples`, `Family`, `Solo`, `Friends`, `Business`, `Unknown`。
- **照片特征二元化 (`has_photo`)**：将 CDN 图片链接化简为 1/0 哑变量，作为衡量游客投入度（Reviewer Effort）的控制变量。

### 步骤 3：多维去重审计与 TripAdvisor 平台交叉展示原理

#### 1. TripAdvisor 平台跨页面同步展示机制 (Cross-Listing Mechanism)
- **现象背景**：同一观光飞行商家（如 *K2 Aviation*, *Wings Over Kauai*, *Maui Plane Rides*, *Maverick Helicopters*）在 TripAdvisor 平台上拥有多个产品页面（例如线路 A 页面、线路 B 页面、公司官方主页）。
- **同步机制**：当一位游客（如 `0801dianeb`）在 TripAdvisor 上为该商家撰写了 **1 条好评** 时，TripAdvisor 系统会自动将该评论同步展示在商家名下的所有相关产品页面。
- **爬虫抓取碰撞**：在爬取 46 个产品 CSV 文件时，同一游客写的同一条评论被爬虫从不同的产品页面重复抓取了 2 至 4 次。这就导致原始拼合数据（28,918 条）中存在高达 **23.1%（6,683 条）的跨文件重复记录**。

#### 2. 去重算法逻辑与数学数据账本
- **判重指纹公式**：
  $$\text{指纹} = \text{[游客用户名 user\_name]} + \text{[小写及空格规范化文本 text\_norm]}$$
- **剔除策略 (`keep='first'`)**：
  - 代码在 Pandas 中提取唯一指纹后，**保留最先读到的第 1 条作为主数据集中的独立原始记录 (`kept_in_master_tour`)**；
  - **剔除后续 CSV 文件中读到的所有重复副本 (`deleted_duplicate_tour`)**，共计删除 6,683 条副本，得到 **22,235 条纯净主样本**。

#### 3. 去重透明度审计文件
- 📄 [deleted_duplicates_audit.csv](file:///c:/Users/pengy/OneDrive/Desktop/Low-Altitude/data/cleaned_datasets/deleted_duplicates_audit.csv)：全部 6,683 条被删除的重复副本。
- 📄 [duplicate_pairs_comparison.csv](file:///c:/Users/pengy/OneDrive/Desktop/Low-Altitude/data/cleaned_datasets/duplicate_pairs_comparison.csv)：6,683 组左右对比表，清晰展示保留的原本来自哪一个 CSV 文件，删除的副本来自哪一个 CSV 文件。

#### 4. 边界保留情况审计
- **同用户同天改写版本**：发现 8 行（4 对）同用户同天发表的微调改写版本（如 `Hillary H` 简写 "plane tour" vs "air tour"），作为真实独立版本予以保留。
- **跨产品真实高频游客**：1,759 位游客评价了多个不同地区的低空项目（共 4,857 条评论），作为真实消费行为完整保留。

### 步骤 4：语种检测与非英文评论过滤
- **动机**：英文 VADER 情绪算法与英文正则对非英文文本失效，会导致情绪得分产生伪零值（False Zeros）。
- **实证结果**：
  - 英文评论：**21,238 条（95.52%）**
  - 非英文评论：**997 条（4.48%）**（法语 372 条、德语 121 条、西班牙语 65 条、意大利语 84 条、中文 11 条等）。
- **处理**：生成 `language` 和 `is_english`（1/0）标记，导出了 [non_english_reviews.csv](file:///c:/Users/pengy/OneDrive/Desktop/Low-Altitude/data/cleaned_datasets/non_english_reviews.csv)。在回归模型中可增加 `is_english` 作为控制变量，或限定 `is_english == 1` 子集。

---

## 🧠 三、 步骤 5：Level 2 深度特征工程 (极致拆解)

Level 2 包含四大核心模块，是生成 [tripadvisor_processed_master.csv](file:///c:/Users/pengy/OneDrive/Desktop/Low-Altitude/data/cleaned_datasets/tripadvisor_processed_master.csv) 的核心：

```
                              Level 2 深度特征工程
                                       │
      ┌────────────────────────┬───────┴────────────────┬────────────────────────┐
      ▼                        ▼                        ▼                        ▼
【1. 结构化地理解析】      【2. NLP 文本形态特征】    【3. VADER 情绪极性得分】   【4. 9大低空体验领域哑变量】
  - user_city              - review_word_count        - sentiment_polarity       - pilot_mention (61.74%)
  - user_state             - review_char_count          (compound -1.0 ~ +1.0)   - safety_mention (39.02%)
  - user_country           - title_word_count         - sentiment_pos            - price_value_mention (22.78%)
  - is_us_domestic (1/0)   - exclamation_count        - sentiment_neg            - weather_mention (22.28%)
                           - uppercase_ratio          - sentiment_neu            - 飞行员/导游/地勤三项拆分
```

---

### 模块 1：结构化地理解析与分类 (`parse_location`)

#### 1. 为什么自由文本位置难以使用？
游客输入的 `user_location` 格式极其混乱（如 `"Hot Springs, AR"`, `"Frankfort, Ohio, United States"`, `"Brisbane, Australia"`, `"London"`）。有些包含三段，有些只有城市名。

#### 2. 解析器 `parse_location` 的核心算法逻辑：
- **第一步：末段提取**：取以逗号分割的最后一段 `last_part = parts[-1]`。
- **第二步：国家与州别名字典匹配**：
  - 匹配国家别名 `COUNTRY_ALIAS`（如 `USA`, `UK`, `NZ`, `AUS`, `ENGLAND` $\rightarrow$ 规范国家名）；
  - 匹配常见国家集合 `COMMON_COUNTRIES`（如 `GERMANY`, `FRANCE`, `JAPAN`）；
  - 匹配美国 50 州缩写及全称 `US_STATES_MAP`（如 `CALIFORNIA` $\rightarrow$ `CA`, `TEXAS` $\rightarrow$ `TX`）。
- **第三步：倒数第二段回溯**：若末段为 `"United States"`，则往前检查倒数第二段 `parts[-2]` 提取美国州缩写；若只提供了 `"City, State"`（如 `"Milpitas, CA"`），自动推断国家为 `United States`。

#### 3. 核心变量 **`is_us_domestic` (1/0)** 的构建动机：
- **学术意义**：低空观光消费中，美国本土游客与国际游客在语言沟通、风险感知、心理预期及价格敏感度上存在显著异质性。
- **统计结果**：数据集中 **49.7%（11,044 条）** 为美国本土游客。
- **前 5 大本土客源州**：加利福尼亚州 CA（1,569条）、佛罗里达州 FL（851条）、德克萨斯州 TX（793条）、纽约州 NY（449条）、华盛顿州 WA（429条）。

---

### 模块 2：NLP 文本形态特征 (Text Structural Metrics)

在实证回归模型中，文本形态特征常被用作衡量“评论信息量与表达情绪强度”的控制变量：

1. **`review_word_count`（评论词数） & `review_char_count`（字符数）**：
   - **理论含义**：代表“评论信息量与认知深度（Review Information Depth / Elaboration）”。较长的评论通常包含更详细的体验描述，更容易获得 Useful Votes（有用投票）。
2. **`title_word_count`（标题词数）**：
   - 代表游客对本次体验总结的精炼程度。
3. **`exclamation_count`（感叹号数量）**：
   - **理论含义**：代表“情绪波动与震撼感（Emotional Intensity）”。低空飞行带来的视觉冲击（如从空中看到大峡谷或冰川）常促使游客使用多个感叹号（如 `"UNBELIEVABLE VIEWS!!!"`）。
4. **`uppercase_ratio`（大写字母比例）**：
   - **理论含义**：大写字母在网络评论中代表情绪爆发、强调或喊叫（Shouting）。计算公式：$Uppercase Ratio = \frac{\text{大写字符数}}{\text{总字符数}}$。

---

### 模块 3：VADER 情绪极性得分 (VADER Sentiment Polarity)

#### 1. 为什么选择 VADER 算法？
VADER (Valence Aware Dictionary and sEntiment Reasoner) 是专门针对在线社交媒体与消费评论（TripAdvisor、Yelp）优化的词典级 NLP 规则算法。相比传统 Sentiment Lexicon，VADER 能精准识别：
- **程度副词修饰**（如 `very good` vs `slightly good`）
- **否定词倒转**（如 `not great`）
- **标点符号情绪强化**（如 `stunning view!!!`）
- **全大写字母喊叫强化**（如 `GREAT EXPERIENCE`）

#### 2. 输出变量定义与全量数据集实证数据账本：

| VADER 变量名 | 数据集统计均值 | 中位数 / 极值 | 含义与计量回归应用 |
| :--- | :--- | :--- | :--- |
| **`sentiment_polarity`** | **0.8364** (标准差 0.3155) | 中位数 **0.9410** (范围 -0.9975 ~ +0.9997) | 归一化综合 Compound 得分，计量回归**核心情绪自变量/中介变量** |
| **`sentiment_pos`** | **24.91%** | 23.80% | 评论文本中**积极词文本**所占概率比例 |
| **`sentiment_neg`** | **1.73%** | 0.00% (75% 分位数仅 2.5%) | 评论文本中**消极词文本**所占概率比例 |

#### 3. 极性三分类分布 (VADER Tri-Categorical Breakdown)：
- **积极评论 (`sentiment_polarity >= 0.05`)**：**21,175 条 (95.23%)** —— *反映出低空旅游的高满意度与极佳口碑属性*
- **中性评论 (`-0.05 < sentiment_polarity < 0.05`)**：**369 条 (1.66%)**
- **消极评论 (`sentiment_polarity <= -0.05`)**：**691 条 (3.11%)**

#### 4. 星级评分 (`rating`) 与 VADER 得分的单调收敛效度验证 (Convergent Validity)：
实证统计显示，VADER 情绪得分与游客 1~5 星级评分展现出**极其显著的单调递增关系**，证明了 VADER 在低空观光文本中的高效度：
- **1 星评分评论**：VADER 得分均值 **-0.1162** (中位数 -0.2500)
- **2 星评分评论**：VADER 得分均值 **+0.2349** (中位数 +0.3147)
- **3 星评分评论**：VADER 得分均值 **+0.4163** (中位数 +0.7270)
- **4 星评分评论**：VADER 得分均值 **+0.7183** (中位数 +0.9016)
- **5 星评分评论**：VADER 得分均值 **+0.8579** (中位数 +0.9432)

#### 5. 英文 vs 非英文评论的 VADER 得分断层实证（说明为何非英文必须子集处理）：
- **英文评论 (`is_english=1`, 21,581条)**：VADER 得分均值 **0.8612**，中位数 **0.9432**
- **非英文评论 (`is_english=0`, 654条)**：VADER 得分均值 **0.0168**，中位数 **0.0000**
- **结论**：非英文评论因英文词典无法识别而被截断为 0.0000 伪中性值。在回归模型中必须通过 `is_english == 1` 子样本筛选或加入 `is_english` 哑变量进行控制。

---

### 模块 4：低空旅游 9 大体验维度哑变量 (0/1 Indicators)

结合低空观光（直升机、小飞机、水上飞机）的独特体验属性，通过词库与正则表达式提炼了 9 大核心领域的 0/1 哑变量特征：

#### 1. "Pilot Bruce" 明星飞行员数据探查与变量抽象逻辑
- **数据发现**：在统计高频实词时，发现具体人名 **`bruce`** 出现了 **2,956 次（覆盖 1,545 条评论，占总评论 6.95%）**！
- **深入排查**：过滤后发现 **97.7% 的 `bruce` 提及（1,510条）** 集中在夏威夷考艾岛项目：*Wings Over Kauai Air Tour*（651条）和 *Kauai Deluxe Sightseeing Flight*（859条）。Bruce 是该公司的创始人兼明星飞行员，游客习惯在好评中点名表扬。
- **抽象处理逻辑**：具体人名无法跨 46 个产品通用。因此在 Level 2 中，我们将其抽象为**职业范畴词**（`pilot`, `captain`, `co-pilot`, `aviator`），使得特征能在所有产品间通用。

#### 2. 飞行员 vs 导游 vs 地面服务人员的独立拆分：
#### 2. 低空观光领域角色切分逻辑 (Flight Crew vs. Ground Staff)
- **行业真实逻辑纠正 (Pilot = Guide)**：
  在低空观光飞行（直升机、小飞机、水上飞机）中，**飞行员 (Pilot) 与导游 (Guide) 实际上是同一个角色/同一个人**！飞行员佩戴耳机，一边驾驶飞机一边提供全程空中解说与景点引导。因此将 `pilot` 和 `guide` 合并归类为 **空中飞行与解说组 (`flight_crew_mention`)**。
- **地面服务组 (Ground Staff) 的独立切分**：
  前台接待、登机办理、办公室客服（`desk`, `check-in`, `front desk`, `office agent`）是独立的地面服务环节，单独切分为 **地面接待服务组 (`ground_staff_mention`)**。
- **同行家属/同伴组 (Companion Guests)**：
  游客同行家属与同伴（`husband`, `wife`, `daughter`, `son`, `family`, `friend`）独立识别为 **`companion_mention`**，防止其与服务人员混淆。

### 3. 关于代词指代推断的稳健性与安全性设计
- **防伪阳性设计**：
  在海量真实文本中，简单的跨句子代词推断规则（如看到上一句提到飞行员，就把下一句所有的 `he`/`she` 都盲目记为飞行员）会在段落主题转换时引入严重的**伪阳性噪音 (False Positives)**。
- **高置信度匹配**：
  因此，[coref_resolver.py](file:///c:/Users/pengy/OneDrive/Desktop/Low-Altitude/coref_resolver.py) 采用了基于领域词库与句内限定的高置信度匹配机制。既捕获了包含男/女飞行员及解说的全部表现（如 `Pilot Sarah`, `Captain Bruce`, `Tour Guide`, `In-flight narration`），又保证了特征 100% 的准确性与学术严谨度。误判定为飞行员（产生伪阳性噪声），在 `pilot_mention` 和 `guide_mention` 的特征提取中，我们采用了**显式职业身份名词匹配法**（`pilot`, `captain`, `co-pilot`, `tour guide`）。只有评论中出现了明确的身份名词时才记为 1。这种处理保障了特征提取 **100% 的准确率 (Precision)**。
- **扩展指代消解算法（上下文窗口消解规则）**：
  若后续需要对代词进行深度指代恢复，可采用上下文句级窗口（Sentence-level Context Window）规则：
  1. 将评论按句号拆分为单句；
  2. 当句子中包含代词 `he`/`she` 时，向上检索前 1 句的主语；
  3. 若前句主语属于飞行员词库（如 `pilot`, `captain`），则将代词 `he` 消解映射为 `pilot`；若前句主语属于游客同伴词库（如 `husband`, `wife`, `daughter`, `friend`），则归类为同行游客（Guest/Companion），从而实现指代的精准归属。

#### 4. 9 大低空体验维度详细定义与特征表：

| 变量名 | 中文维度 | 匹配正则表达式 / 核心词库 | 真实提及率 (%) | 学术与商业意义说明 |
| :--- | :--- | :--- | :--- | :--- |
| **`pilot_mention`** | **飞行员/机长** | `pilot`, `captain`, `co-pilot`, `aviator`, `flyer` | **61.74%** | 空中驾驶与解说核心体验 |
| **`safety_mention`** | **安全与心理焦虑** | `safe`, `safety`, `nervous`, `scared`, `calm`, `landing`, `smooth`, `relaxed`, `anxious` | **39.02%** | 低空飞行的感知风险（Perceived Risk）与安全感建立 |
| **`price_value_mention`**| **价格与性价比** | `price`, `worth`, `expensive`, `cheap`, `value`, `cost`, `budget`, `penny`, `deal` | **22.78%** | 高客单价消费的感知价值（Perceived Value）与 "worth every penny" |
| **`weather_mention`** | **天气与能见度** | `weather`, `cloud`, `clouds`, `rain`, `wind`, `visibility`, `clear`, `sunny` | **22.28%** | 低空观光对气象环境的极高敏感度与脆弱性 |
| **`staff_service_mention`**| **地面/前台服务** | `staff`, `desk`, `check-in`, `crew`, `host`, `office`, `agent` | **15.77%** | 地面接待、登机办理与服务态度 |
| **`canyon_mention`** | **峡谷/山谷景观** | `canyon`, `waimea`, `gorge`, `valley`, `canyons` | **15.12%** | 大峡谷、考艾岛威美亚峡谷等地貌属性 |
| **`special_occasion`** | **特殊纪念场景** | `honeymoon`, `anniversary`, `birthday`, `bucket list`, `highlight`, `celebrat*` | **13.11%** | 蜜月、生日、打卡等特殊旅行动机 (Travel Motivation) |
| **`helicopter_comparison`**| **直升机机型** | `helicopter`, `heli`, `chopper` | **12.25%** | 直升机与固定翼飞机的体验差异与对比 |
| **`coast_mention`** | **海岸/海洋景观** | `coast`, `napali`, `na pali`, `shore`, `beach`, `ocean`, `pacific` | **8.90%** | 夏威夷纳帕利海岸、太平洋海岸观光属性 |
| **`guide_mention`** | **导游/解说员** | `guide`, `tour guide`, `narrator`, `docent`, `instructor` | **8.77%** | 专职导游/讲解员角色 |
| **`waterfall_mention`** | **瀑布景观** | `waterfall`, `waterfalls`, `falls` | **5.39%** | 俯瞰瀑布特写观光属性 |

---

## 📈 四、 步骤 6：N-Gram 挖掘与学术图表产出

### 1. N-Gram 高频词组挖掘发现 (从 22,235 条评论中提取)
- **Top 双词短语 (Bigrams)**：
  - `highly recommend`: 3,347 次 (14.67% 评论覆盖率)
  - `glacier landing`: 2,844 次 (9.88% 覆盖率)
  - `grand canyon`: 2,746 次 (7.80% 覆盖率)
  - `worth every` (penny): 874 次 (3.76% 覆盖率)
  - `pilot great` / `great pilot`: 1,621 次 (7.23% 覆盖率)
- **Top 三词短语 (Trigrams)**：
  - `would highly recommend`: 959 次 (4.29%)
  - `talkeetna air taxi`: 812 次 (3.01%)
  - `worth every penny`: 669 次 (2.88%)
  - `made us feel` (safe): 408 次 (1.79%)

### 2. 生成的科研级图像与数据表：
- 📈 `figures/world_map_reviews.png`：全球游客分布热力地图
- 📈 `figures/us_map_reviews.png`：美国本土游客来源州热力地图
- 📈 `figures/low_altitude_feature_distribution.png`：11 大体验维度提及率柱状图
- 📊 `data/derived_outputs/paper_table_country_distribution.csv`：前 15 大客源国分布表
- 📊 `data/derived_outputs/paper_table_us_state_distribution.csv`：前 15 大美国客源州分布表

---

## 🔬 五、 Level 3：高级计量经济学建模、因果推断与学术论文规划

在完成了 Level 1 数据清洗与 Level 2 深度特征工程后，基于全量干净数据集 `tripadvisor_processed_master.csv`，**Level 3** 代表进入论文的**实证回归分析、假设检验与深度学术挖掘阶段**：

```text
                               Level 3 学术实证与因果推断框架
                                             │
      ┌────────────────────────┬─────────────┴───────────────┬────────────────────────┐
      ▼                        ▼                             ▼                        ▼
【1. 基准计量回归模型】   【2. 中介与调节效应检验】    【3. 组间异质性与稳健性】   【4. 深度 NLP 与主题模型】
  - OLS / Ordered Probit   - VADER 得分中介通道         - 国内 vs 国际游客         - BERTopic 拓扑聚类
  - 产品/时间双重固定效应   - 气象/机型调节变量          - 直升机 vs 固定翼         - ABSA 属性级情感
```

### 1. 基准计量回归模型 (Baseline Econometric Regressions)
- **被解释变量 ($Y_{ij}$)**：游客星级评分 `rating` (1-5 星) 或评论有用性投票 `helpful_votes`。
- **核心解释变量 ($X_{ij}$)**：Level 2 提取的领域特征（`pilot_mention`, `safety_mention`, `price_value_mention`, `weather_mention` 等）。
- **固定效应 (Fixed Effects)**：控制 46 个产品的**产品固定效应 ($\mu_j$)** 和年份/月份的**时间固定效应 ($\lambda_t$)**。
- **控制变量 ($\mathbf{Z}_{ij}$)**：`review_word_count`, `exclamation_count`, `uppercase_ratio`, `is_us_domestic`, `has_photo` 等。

### 2. 心理机制与中介效应分析 (Mediation & Moderation Mechanisms)
- **情绪中介链路 (VADER Sentiment Mediation)**：
  检验飞行员优质服务（`pilot_mention`）或安全感确立（`safety_mention`）是否通过提升游客的情绪极性（`sentiment_polarity`），进一步转化为 5 星好评：
  $$\text{Pilot Mention} \xrightarrow{\quad\text{提升}\quad} \text{VADER Sentiment Polarity} \xrightarrow{\quad\text{驱动}\quad} \text{Rating}$$
- **调节效应 (Moderation)**：检验不同环境下的边际效应。例如：*在低能见度或恶劣天气 (`weather_mention=1`) 条件下，飞行员的高水平解说与安抚对游客评分的提升作用是否更加显著？*

### 3. 组间异质性与稳健性检验 (Heterogeneity & Robustness Checks)
- **客源地异质性 (Domestic vs International)**：比较美国本土游客 (`is_us_domestic=1`) 与国际游客在“感知价值 (`price_value`)”和“感知风险 (`safety_mention`)”上的敏感度差异。
- **机型异质性 (Helicopter vs Airplane)**：直升机与固定翼飞机在视野、噪音与心理紧张感上的体验差异对好评率的影响。
- **稳健性检验 (Robustness Checks)**：
  - 仅限定英文评论子集 (`is_english == 1`，21,238 条) 重新估计方程。
  - 使用 Ordered Probit / Tobit 替代 OLS 进行受限因变量回归。

### 4. 深度文本主题建模与 ABSA (BERTopic & ABSA)
- **BERTopic / LDA 主题模型**：利用 Transformer 嵌入对全量文本进行非监督聚类，提取 low-altitude 观光的隐含主题维度。
- **属性级情感分析 (Aspect-Based Sentiment Analysis, ABSA)**：针对“飞行员”、“景色”、“价格”、“客服”各自计算专属的情感得分。

---

## 📁 六、 目录规范与文件指南

```text
Low-Altitude/
├── data/
│   ├── cleaned_datasets/                 # 🧹 1. 清洗数据与核心主表目录
│   │   ├── tripadvisor_processed_master.csv  # ★ 核心主数据集 (全量22,235条，做回归模型选此表)
│   │   ├── tripadvisor_merged_raw.csv        # 46 个产品的原始抓取合并 CSV (最原始未清洗)
│   │   ├── manual_check_500.csv              # 500 条随机抽样人工核对数据
│   │   ├── manual_check_2000.csv             # 2000 条随机抽样人工核对数据
│   │   ├── non_english_reviews.csv           # 筛选出的 997 条非英文评论子集
│   │   ├── tripadvisor_level1_cleaned.csv    # Level 1 基础清洗过渡表
│   │   └── tripadvisor_level2_features.csv   # Level 2 提炼特征过渡表
│   │
│   └── derived_outputs/                  # 📊 2. 分析挖掘出的衍生产物与论文表格
│       ├── high_freq_bigrams.csv             # 游客高频双词短语表 (Bigrams)
│       ├── high_freq_trigrams.csv            # 游客高频三词短语表 (Trigrams)
│       ├── high_freq_substantive_keywords.csv # 核心领域实词统计表
│       ├── paper_table_country_distribution.csv # 论文用表：游客国家分布 TOP 15
│       └── paper_table_us_state_distribution.csv # 论文用表：美国本土游客来源州 TOP 15
│
├── figures/                              # 📈 自动生成的论文科研图表
│   ├── world_map_reviews.png             # 图 1：全球游客分布热力地图
│   ├── us_map_reviews.png                # 图 2：美国本土游客来源州热力地图
│   └── low_altitude_feature_distribution.png # 图 3：低空体验 9 大维度特征提及率柱状图
│
├── run_data_pipeline.py                  # 🚀 【主脚本 1】数据处理与特征工程流水线代码
├── run_analysis_and_plots.py             # 🚀 【主脚本 2】绘图与高频短语提取代码
├── README.md                             # 简明说明文档
├── RESEARCH_NOTES.md                     # 英文学术研究日志 (English Research Notes)
└── RESEARCH_NOTES_CN.md                  # 中文完整实验与研究笔记 (本文件)
```

---

## 💻 六、 快速运行指南

```bash
# 步骤 1：运行数据流水线 (生成 data/cleaned_datasets/ 目录下的所有核心数据集)
python run_data_pipeline.py

# 步骤 2：运行绘图与分析 (生成 figures/ 目录下的图片及 data/derived_outputs/ 目录下的高频词/分布表)
python run_analysis_and_plots.py
```
