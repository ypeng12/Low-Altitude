# 低空旅游 (Low-Altitude Tourism) TripAdvisor 游客评论数据处理与特征工程流水线

> 📖 **项目文档指南 (Document Matrix)**：
> - 📘 **中文完整研究与实验笔记**：查看 [RESEARCH_NOTES_CN.md](file:///c:/Users/pengy/OneDrive/Desktop/Low-Altitude/RESEARCH_NOTES_CN.md) （包含 Level 2 极致拆解、地理解析、情绪分、Pilot Bruce 探查及 9 大维度哑变量全景）
> - 📝 **English Research Notes**: See [RESEARCH_NOTES.md](file:///c:/Users/pengy/OneDrive/Desktop/Low-Altitude/RESEARCH_NOTES.md) (Detailed English lab-note documentation with empirical metrics)
> - 📄 **简明运行说明书**：查看当前 [README.md](file:///c:/Users/pengy/OneDrive/Desktop/Low-Altitude/README.md) （包含结构图、目录指南及运行指令）

本项目对从 TripAdvisor 抓取的 **46 个低空观光飞行产品**（涵盖直升机观光、小飞机飞行、水上飞机观光等）的 28,000+ 条原始游客评论，进行系统化的**数据清洗、去重审计、语种识别、地理解析、NLP 情绪量化及低空体验领域特征工程**。

项目旨在构建符合学术规范（如 *Tourism Management*、*Journal of Travel Research*）的数据库，为下游的计量经济学模型（Econometric Modeling）、情感回归及消费者行为分析提供高质量自变量与控制变量。

---

## 目录索引
1. [项目整体架构与数据流向](#1-项目整体架构与数据流向)
2. [数据处理每一个步骤、核心思考与实现逻辑](#2-数据处理每一个步骤核心思考与实现逻辑)
   - [步骤 1：原始数据合并与 tour_name 提取](#步骤-1原始数据合并与-tour_name-提取)
   - [步骤 2：Level 1 基础清洗与文本标准化](#步骤-2level-1-基础清洗与文本标准化)
   - [步骤 3：多维去重审计与数据一致性校验](#步骤-3多维去重审计与数据一致性校验)
   - [步骤 4：语种识别与非英文评论过滤](#步骤-4语种识别与非英文评论过滤)
   - [步骤 5：Level 2 深度特征工程 (地理解析/NLP/VADER/领域哑变量)](#步骤-5level-2-深度特征工程-地理解析nlpvader领域哑变量)
   - [步骤 6：高频词挖掘与科研绘图](#步骤-6高频词挖掘与科研绘图)
3. [项目文件与目录分布指南](#3-项目文件与目录分布指南)
4. [代码结构与运行指南](#4-代码结构与运行指南)

---

## 1. 项目整体架构与数据流向

整个 Processing Pipeline 将原始文本数据逐步转化为结构化特征数据库，流程如下：

```
[46个原始单产品CSV] 
       │
       ▼ (步骤1: 文件合并与 tour_name 提取)
[tripadvisor_merged_raw.csv] (28,918条)
       │
       ▼ (步骤2: Level 1 基础清洗 - HTML清理/评分与日期格式化/照片二元化)
[基础清洗暂存表]
       │
       ▼ (步骤3: 文本去重审计 - 剔除严格完全重复与空格差异近重复)
[22,235条 Clean 评论]
       │
       ▼ (步骤4: 语种识别 - 检测英文/法/德/西/中等分类)
[带有 language 与 is_english 标记的数据]
       │
       ▼ (步骤5: Level 2 深度特征工程 - 地理解析 + NLP字数 + VADER情绪分 + 9大低空领域特征)
[data/cleaned_datasets/tripadvisor_processed_master.csv] ★ (主数据集)
       │
       ├──► [步骤6: 科研图表生成] ──► figures/ (地图与提及率柱状图)
       └──► [步骤6: 高频词挖掘]   ──► data/derived_outputs/ (Bigrams/Trigrams/国家与州分布表)
```

---

## 2. 数据处理每一个步骤、核心思考与实现逻辑

### 步骤 1：原始数据合并与 `tour_name` 提取

* **【现实痛点与思考】**：
  抓取时每一个低空观光产品是单独存为一个 CSV 文件（如 `1-Kauai Deluxe Sightseeing Flight_1623_attraction...csv`）。如果简单拼在一起，后续无法区分某条评论属于哪一个具体飞行项目，丢失了产品层面的固定效应（Product Fixed Effects）。
* **【做法与代码思路】**：
  使用 `glob` 扫描 `02-07-2025-TripAdvisor/` 下所有 46 个文件。利用正则表达式从文件名中截取出规范的产品名称（如 `"Kauai Deluxe Sightseeing Flight"`），作为新列 `tour_name` 附加到每一条评论记录中，最后合并为 `tripadvisor_merged_raw.csv`。

---

### 步骤 2：Level 1 基础清洗与文本标准化

* **【清洗目标与思考】**：
  网页抓取的原始数据中充斥着 HTML 乱码、无用行政信息列、格式不统一的日期和缺失值。需要保障数据的基本完整性和可读性。
* **【具体清洗细节与实现】**：
  1. **无用行政列删除**：删去 `user_profile`（个人主页 URL）、`user_avatar`（头像链接）及 `disclaimer`（免责声明），减少内存占用。
  2. **核心缺失值过滤**：强制要求 `review_text`（评论正文）和 `rating`（评分）不能为空，剔除无效记录。
  3. **HTML 标签清洗与实体解码 (`clean_html_linebreaks`)**：
     - 将网页中的换行标签 `<br />`、`<br>` 统一替换为标准 Python 换行符 `\n`，保留游客段落结构。
     - 使用 `html.unescape()` 将转义字符还原（如 `&amp;` $\rightarrow$ `&`，`&#39;` $\rightarrow$ `'`，`&quot;` $\rightarrow$ `"`）。
     - 将连续 3 个以上的冗余换行符压缩为双换行 `\n\n`。
  4. **评分标准化**：将 rating 统一转为 `1, 2, 3, 4, 5` 整数分值，过滤超出 1–5 范围的异常值。
  5. **日期标准化 (`clean_published_date`)**：将网页抓取的文本字符串（如 `"Written February 24, 2025"`）清洗并解析为国际标准格式 `YYYY-MM-DD`（如 `2025-02-24`）。
  6. **出行类型分类与补全 (`standardize_trip_type`)**：
     - 若抓取字段 `trip_type` 缺失，尝试从元文本 `rating_text`（如 `"Feb 2025 • Family"`）中二次提取。
     - 归一化映射为 6 大标准类别：`Couples`（情侣/夫妻）、`Family`（家庭）、`Solo`（单人）、`Friends`（朋友）、`Business`（商务）、`Unknown`（未知）。
  7. **照片特征二元化 (`has_photo`)**：将冗长的 CDN 图片链接转为二元标记 `has_photo`（1 表示游客上传了照片，0 表示未上传），作为衡量游客投入度与评论可信度的控制变量。

---

### 步骤 3：多维去重审计与数据一致性校验

* **【现实痛点与思考】**：
  抓取过程中由于页面交叉推荐，不同产品 CSV 之间存在大量重复评论。如果简单做全列去重，可能会漏掉“仅仅多打了一个空格”的近重复评论。
* **【多层级审计逻辑】**：
  1. **严格完全重复审计**：对 `(user_name + review_text)` 完全一致的行进行识别。在原始 28,918 条数据中，发现有 13,116 行参与了严格重复。
  2. **空格/大小写规范化去重（Whitespace-Normalized De-duplication）**：
     - 将评论转化为小写，并利用正则 `\s+` 将多个连续空格/换行压缩为一个统一空格。
     - 识别出像 `Harry M` 这种因网页格式差异导致评论中多包含一个空格的“近重复评论”（Near-Duplicates）。
     - 执行去重后，成功剔除了 **6,683 条重复评论**，保留了 **22,235 条干净的独立评论**。
  3. **高频游客多产品评价保留依据**：
     - 审计发现有 1,759 位活跃游客对不同产品发表了 4,857 条评论。由于这是真实消费者体验不同低空项目（如既坐了直升机又坐了水上飞机）的真实行为，在计量经济学中予以完整保留。

---

### 步骤 4：语种识别与非英文评论过滤

* **【为什么需要识别语种？】**：
  TripAdvisor 是全球性平台，存在部分非英文评论（如法文、德文、中文）。但常用的 VADER 情感分析算法和英文关键词正则表达式对非英文文本失效。如果直接带入计算，会导致情感分误判为 0。
* **【识别方法与结果】**：
  - 集成 `langdetect` 库与正则表达式特征词匹配，检测全量评论语种。
  - **统计结果**：
    - **英文评论**：**21,238 条（占比 95.52%）**；
    - **非英文评论**：**997 条（占比 4.48%）**，主要涵盖法语（372条）、德语（121条）、西班牙语（65条）、中文（31条）等。
  - 在数据集里生成 `language` 列和 `is_english`（1/0）二元标识，方便后续做模型控制或筛选。

---

### 步骤 5：Level 2 深度特征工程 (地理解析/NLP/VADER/领域哑变量)

此步骤是整个流水线的核心，提取用于计量经济学回归的变量：

#### 1. 结构化地理解析与分类 (`parse_location`)
- **思考**：游客填写的地址自由度极高（如 `"Hot Springs, AR"`, `"Brisbane, Australia"`, `"London"`），无法直接用于模型。
- **做法**：设计基于规则的逆向解析逻辑：
  - 提取 `user_city`（城市）、`user_state`（美国州缩写，如 CA, FL, HI）、`user_country`（国家）。
  - 构造 **`is_us_domestic`（1/0）**：判断是否为美国国内游客（1表示美国本土，0表示国际游客），用于分析客源地行为差异。

#### 2. NLP 文本统计特征 (Text Metrics)
- **`review_word_count` / `review_char_count`**：评论词数与字符数，衡量“评论详细程度与信息量”。
- **`exclamation_count`**：感叹号数量，反映游客情绪爆发强烈程度。
- **`uppercase_ratio`**：大写字母比例（如 "AMAZING EXPERIENCE!"），反映强烈情绪表达。

#### 3. VADER 情感极性得分 (Sentiment Scoring)
- **原理**：调用学术界广泛使用的 NLTK VADER 情绪分析器。
- **产出**：输出连续型情绪极性分 `sentiment_polarity`（-1.0 到 +1.0，表示整体态度正负向），以及 `sentiment_pos` / `sentiment_neg` 分值。

#### 4. 低空旅游 9 大体验维度特征抽取 (Domain-Specific Indicators)
结合低空观光行业属性，通过词根与正则表达式提炼 9 大二元哑变量（1表示提及，0表示未提及）：

| 特征变量名 | 中文维度 | 匹配词库与正则逻辑 | 数据集提及率 |
| :--- | :--- | :--- | :--- |
| **`pilot_mention`** | **飞行员/机长** *(独立拆分)* | `pilot`, `captain`, `co-pilot`, `aviator`, `flyer` | **61.74%** |
| **`guide_mention`** | **导游/解说员** *(独立拆分)* | `guide`, `tour guide`, `narrator`, `docent`, `instructor` | **8.77%** |
| **`staff_service_mention`** | **地面/前台服务** *(独立拆分)* | `staff`, `desk`, `check-in`, `crew`, `host`, `office`, `agent` | **15.77%** |
| **`safety_mention`** | **安全与心理焦虑** | `safe`, `safety`, `nervous`, `scared`, `calm`, `landing`, `smooth`, `relaxed` | **39.02%** |
| **`price_value_mention`** | **价格与性价比感知** | `price`, `worth`, `expensive`, `cheap`, `value`, `cost`, `budget`, `penny` | **22.78%** |
| **`weather_mention`** | **天气与能见度** | `weather`, `cloud`, `rain`, `wind`, `visibility`, `sunny`, `clear` | **22.28%** |
| **`canyon_mention`** | **峡谷地貌景观** | `canyon`, `waimea`, `gorge`, `valley` | **15.12%** |
| **`special_occasion`** | **特殊纪念场景** | `honeymoon`, `anniversary`, `birthday`, `bucket list`, `highlight` | **13.11%** |
| **`helicopter_comparison`**| **直升机机型对比** | `helicopter`, `heli`, `chopper` | **12.25%** |
| **`coast_mention`** | **海岸/海洋景观** | `coast`, `napali`, `shore`, `beach`, `ocean`, `pacific` | **8.90%** |
| **`waterfall_mention`** | **瀑布景观** | `waterfall`, `falls` | **5.39%** |

---

### 步骤 6：高频词挖掘与科研绘图

通过 `run_analysis_and_plots.py` 实现后处理分析与产出：
1. **N-gram 高频词组提取**：使用 CountVectorizer 提取双词短语 (Bigrams，如 `glacier landing`) 和三词短语 (Trigrams，如 `would highly recommend`)，衡量游客最关注的表达。
2. **科研绘图**：自动生成全球游客热力图 (`world_map_reviews.png`)、美国来源州热力图 (`us_map_reviews.png`) 及低空体验特征提及率柱状图 (`low_altitude_feature_distribution.png`)。

---

## 3. 项目文件与目录分布指南

所有 CSV 数据集与图表产出均已分类归档：

```text
Low-Altitude/
├── data/
│   ├── cleaned_datasets/                 # 🧹 1. 清洗数据与核心主表目录
│   │   ├── tripadvisor_processed_master.csv  # ★ 核心主数据集 (全量22,235条，做回归模型选此表)
│   │   ├── deleted_duplicates_audit.csv      # ★ 被剔除的重复评论审计表
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
├── 02-07-2025-TripAdvisor/               # 📁 46 个原始 scraped 单产品 CSV 文件夹
│
├── run_data_pipeline.py                  # 🚀 【主脚本 1】数据处理与特征工程流水线代码
├── run_analysis_and_plots.py             # 🚀 【主脚本 2】绘图与高频短语提取代码
└── README.md                             # 本说明文档
```

---

## 4. 代码结构与运行指南

代码全量整合为 **2 个结构清晰的主脚本**，点开代码即可看到详细的中文步骤注释：

1. **数据处理与特征工程流水线**：[run_data_pipeline.py](file:///c:/Users/pengy/OneDrive/Desktop/Low-Altitude/run_data_pipeline.py)
   - 顺序执行：合并 $\rightarrow$ 清洗 $\rightarrow$ 去重 $\rightarrow$ 语种识别 $\rightarrow$ 地理/NLP/VADER/低空特征提取 $\rightarrow$ 自动导出至 `data/cleaned_datasets/`。
2. **绘图与分析挖掘脚本**：[run_analysis_and_plots.py](file:///c:/Users/pengy/OneDrive/Desktop/Low-Altitude/run_analysis_and_plots.py)
   - 顺序执行：读取主表 $\rightarrow$ 绘制热力地图/柱状图至 `figures/` $\rightarrow$ 导出 N-gram 短语与论文摘要表至 `data/derived_outputs/`。

### 💻 运行命令：

```bash
# 步骤 1：运行数据流水线 (生成 data/cleaned_datasets/ 目录下的所有核心数据集)
python run_data_pipeline.py

# 步骤 2：运行绘图与分析 (生成 figures/ 目录下的图片及 data/derived_outputs/ 目录下的高频词/分布表)
python run_analysis_and_plots.py
```
