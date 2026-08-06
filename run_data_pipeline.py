"""
================================================================================
低空旅游 TripAdvisor 评论数据处理与特征工程 Master 流水线脚本 (run_data_pipeline.py)
================================================================================
本脚本将原有的多个分散处理环节整合为一，包含 6 大核心步骤：
  1. 原始 CSV 文件合并与产品名称 (tour_name) 提取
  2. Level 1 基础清洗 (HTML 换行符清理、评分/日期标准化、出行类型提取)
  3. 多维去重审计 (剔除完全重复与仅空格/换行差异的近重复评论)
  4. 语种识别 (检测法/德/西/中等非英文评论，生成语言标记列)
  5. Level 2 深度特征工程 (地理解析、NLP统计指标、VADER情感分析、9大低空领域特征)
  6. 导出主数据集 (tripadvisor_processed_master.csv) 与人工校验抽样集
================================================================================
"""

import os
import glob
import re
import html
import pandas as pd
import numpy as np
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# 确保 NLTK 的 VADER 词典已下载
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon', quiet=True)

sia = SentimentIntensityAnalyzer()

# ==============================================================================
# 0. 地理位置解析字典 (用于解析游客所在城市、州、国家)
# ==============================================================================
US_STATES_MAP = {
    'ALABAMA': 'AL', 'ALASKA': 'AK', 'ARIZONA': 'AZ', 'ARKANSAS': 'AR', 'CALIFORNIA': 'CA',
    'COLORADO': 'CO', 'CONNECTICUT': 'CT', 'DELAWARE': 'DE', 'FLORIDA': 'FL', 'GEORGIA': 'GA',
    'HAWAII': 'HI', 'IDAHO': 'ID', 'ILLINOIS': 'IL', 'INDIANA': 'IN', 'IOWA': 'IA',
    'KANSAS': 'KS', 'KENTUCKY': 'KY', 'LOUISIANA': 'LA', 'MAINE': 'ME', 'MARYLAND': 'MD',
    'MASSACHUSETTS': 'MA', 'MICHIGAN': 'MI', 'MINNESOTA': 'MN', 'MISSISSIPPI': 'MS', 'MISSOURI': 'MO',
    'MONTANA': 'MT', 'NEBRASKA': 'NE', 'NEVADA': 'NV', 'NEW HAMPSHIRE': 'NH', 'NEW JERSEY': 'NJ',
    'NEW MEXICO': 'NM', 'NEW YORK': 'NY', 'NORTH CAROLINA': 'NC', 'NORTH DAKOTA': 'ND', 'OHIO': 'OH',
    'OKLAHOMA': 'OK', 'OREGON': 'OR', 'PENNSYLVANIA': 'PA', 'RHODE ISLAND': 'RI', 'SOUTH CAROLINA': 'SC',
    'SOUTH DAKOTA': 'SD', 'TENNESSEE': 'TN', 'TEXAS': 'TX', 'UTAH': 'UT', 'VERMONT': 'VT',
    'VIRGINIA': 'VA', 'WASHINGTON': 'WA', 'WEST VIRGINIA': 'WV', 'WISCONSIN': 'WI', 'WYOMING': 'WY',
    'DISTRICT OF COLUMBIA': 'DC', 'WASHINGTON DC': 'DC', 'PUERTO RICO': 'PR'
}
US_CODES = set(US_STATES_MAP.values())
COUNTRY_ALIAS = {
    'USA': 'United States', 'US': 'United States', 'UNITED STATES OF AMERICA': 'United States',
    'UK': 'United Kingdom', 'ENGLAND': 'United Kingdom', 'SCOTLAND': 'United Kingdom', 'WALES': 'United Kingdom',
    'GREAT BRITAIN': 'United Kingdom', 'NZ': 'New Zealand', 'AUS': 'Australia', 'CAN': 'Canada',
    'UAE': 'United Arab Emirates'
}
COMMON_COUNTRIES = {
    'UNITED STATES', 'AUSTRALIA', 'UNITED KINGDOM', 'CANADA', 'NEW ZEALAND', 'GERMANY',
    'FRANCE', 'JAPAN', 'CHINA', 'BRAZIL', 'INDIA', 'ITALY', 'SPAIN', 'MEXICO', 'NETHERLANDS',
    'SWITZERLAND', 'ROMANIA', 'ISRAEL', 'SWEDEN', 'NORWAY', 'DENMARK', 'IRELAND',
    'SOUTH AFRICA', 'SINGAPORE', 'BELGIUM', 'AUSTRIA', 'PHILIPPINES', 'MALAYSIA',
    'THAILAND', 'SOUTH KOREA', 'ARGENTINA', 'CHILE', 'COLOMBIA', 'PORTUGAL', 'GREECE',
    'POLAND', 'CZECH REPUBLIC', 'HUNGARY', 'FINLAND', 'NEW CALEDONIA', 'FIJI'
}


# ==============================================================================
# 辅助函数定义
# ==============================================================================
def clean_published_date(val):
    """【日期清理】将 'Written February 24, 2025' 等文本转为标准 YYYY-MM-DD 格式"""
    if pd.isna(val) or not isinstance(val, str):
        return None
    cleaned = val.replace('Written', '').strip()
    parsed = pd.to_datetime(cleaned, errors='coerce')
    if pd.notna(parsed):
        return parsed.strftime('%Y-%m-%d')
    return None

def clean_html_linebreaks(text):
    """【HTML清理】将 <br /> 替换为标准换行符 \n，并解码 &amp; &#39; 等 HTML 转义字符"""
    if pd.isna(text) or not isinstance(text, str):
        return text
    cleaned = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
    cleaned = html.unescape(cleaned)
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
    return cleaned.strip()

def standardize_trip_type(row):
    """【出行类型标准化】统一为 Couples, Family, Solo, Friends, Business, Unknown 六大类"""
    tt = row.get('trip_type')
    rt = row.get('rating_text')
    if pd.isna(tt) or str(tt).strip() == '' or str(tt).lower() == 'nan':
        if isinstance(rt, str) and '•' in rt:
            parts = rt.split('•')
            if len(parts) > 1:
                tt = parts[1].strip()
    if pd.isna(tt) or not isinstance(tt, str) or str(tt).strip() == '':
        return 'Unknown'
    tt_lower = tt.lower().strip()
    if 'couple' in tt_lower: return 'Couples'
    elif 'family' in tt_lower: return 'Family'
    elif 'solo' in tt_lower: return 'Solo'
    elif 'friend' in tt_lower: return 'Friends'
    elif 'business' in tt_lower: return 'Business'
    else: return 'Unknown'

def parse_location(loc_str):
    """【地理解析】从游客填写的地址中提取 user_city, user_state, user_country 和 is_us_domestic"""
    if not isinstance(loc_str, str) or not loc_str.strip():
        return {'user_city': None, 'user_state': None, 'user_country': 'Unknown', 'is_us_domestic': 0}
    loc_clean = loc_str.strip()
    parts = [p.strip() for p in loc_clean.split(',')]
    city, state, country, is_us = None, None, 'Unknown', 0
    last_part = parts[-1].upper()
    
    if len(parts) == 1:
        if last_part in COUNTRY_ALIAS: country = COUNTRY_ALIAS[last_part]
        elif last_part in COMMON_COUNTRIES: country = last_part.title()
        elif last_part in US_STATES_MAP: state = US_STATES_MAP[last_part]; country = 'United States'; is_us = 1
        elif last_part in US_CODES: state = last_part; country = 'United States'; is_us = 1
        else: city = loc_clean; country = 'Unknown'
    else:
        if last_part in COUNTRY_ALIAS: country = COUNTRY_ALIAS[last_part]
        elif last_part in COMMON_COUNTRIES: country = last_part.title()
        elif last_part in US_CODES: state = last_part; country = 'United States'; is_us = 1
        elif last_part in US_STATES_MAP: state = US_STATES_MAP[last_part]; country = 'United States'; is_us = 1
            
        if country == 'United States' and len(parts) >= 2:
            mid_part = parts[-2].upper()
            if mid_part in US_CODES: state = mid_part
            elif mid_part in US_STATES_MAP: state = US_STATES_MAP[mid_part]
            city = parts[0]
        elif country != 'Unknown':
            city = parts[0]
        else:
            if last_part in US_CODES: state = last_part; country = 'United States'; is_us = 1; city = parts[0]
            elif last_part in US_STATES_MAP: state = US_STATES_MAP[last_part]; country = 'United States'; is_us = 1; city = parts[0]
            else: city = parts[0]; country = parts[-1].title()

    if country == 'United States': is_us = 1
    return {'user_city': city, 'user_state': state, 'user_country': country, 'is_us_domestic': is_us}

def detect_language(text):
    """【语种检测】准确判定评论语言 (English / French / German / Spanish / Chinese 等)"""
    if not isinstance(text, str) or len(text.strip()) == 0:
        return 'English'
    if re.search(r'[\u4e00-\u9fff]', text): return 'Chinese'
    if re.search(r'[\u3040-\u30ff]', text): return 'Japanese'
    if re.search(r'[\uac00-\ud7af]', text): return 'Korean'
    if re.search(r'[\u0400-\u04ff]', text): return 'Russian'
    
    tokens = set(re.findall(r'\b[a-z\u00c0-\u024f]+\b', text.lower()))
    if len(tokens) == 0:
        return 'English'
        
    try:
        from nltk.corpus import stopwords
        english_stops = set(stopwords.words('english'))
        german_stops = set(stopwords.words('german'))
        french_stops = set(stopwords.words('french'))
        spanish_stops = set(stopwords.words('spanish'))
        italian_stops = set(stopwords.words('italian'))
    except Exception:
        english_stops = {'the', 'and', 'is', 'was', 'in', 'to', 'of', 'it', 'for', 'with', 'on', 'that', 'this', 'we', 'my'}
        german_stops = {'der', 'die', 'das', 'und', 'ist', 'mit', 'sehr', 'schön', 'war'}
        french_stops = {'le', 'la', 'les', 'du', 'et', 'est', 'très', 'pour', 'une', 'des'}
        spanish_stops = {'el', 'la', 'los', 'las', 'que', 'muy', 'excelente', 'con', 'para'}
        italian_stops = {'il', 'che', 'molto', 'bello', 'per', 'con', 'vista'}

    en_cnt = len(tokens.intersection(english_stops))
    de_cnt = len(tokens.intersection(german_stops))
    fr_cnt = len(tokens.intersection(french_stops))
    es_cnt = len(tokens.intersection(spanish_stops))
    it_cnt = len(tokens.intersection(italian_stops))
    
    de_triggers = {'der', 'die', 'das', 'und', 'ist', 'mit', 'sehr', 'schön', 'war', 'fliegen', 'ausflug', 'rundflug', 'erlebnis', 'wir', 'uns', 'den', 'dem'}
    es_triggers = {'el', 'la', 'los', 'las', 'que', 'muy', 'excelente', 'con', 'para', 'sin', 'una', 'del', 'por', 'sobre', 'inolvidable'}
    fr_triggers = {'le', 'la', 'les', 'du', 'et', 'est', 'très', 'pour', 'une', 'des', 'avec', 'vol', 'magnifique', 'dans', 'plus'}
    
    de_trig_cnt = len(tokens.intersection(de_triggers))
    es_trig_cnt = len(tokens.intersection(es_triggers))
    fr_trig_cnt = len(tokens.intersection(fr_triggers))
    
    if de_cnt > en_cnt or de_trig_cnt >= 2:
        return 'German'
    if es_cnt > en_cnt or es_trig_cnt >= 2:
        return 'Spanish'
    if fr_cnt > en_cnt or fr_trig_cnt >= 2:
        return 'French'
    if it_cnt > en_cnt:
        return 'Italian'
        
    if en_cnt == 0 and len(tokens) >= 5:
        return 'Other Non-English'
        
    return 'English'



# ==============================================================================
# 流水线主入口
# ==============================================================================
def main():
    print("\n" + "="*70)
    print("【步骤 1】合并 46 个 TripAdvisor 原始抓取 CSV 文件")
    print("="*70)
    
    raw_dir = "02-07-2025-TripAdvisor"
    csv_files = glob.glob(os.path.join(raw_dir, "*.csv"))
    print(f"找到 {len(csv_files)} 个原始产品 CSV 文件。")

    df_list = []
    for file_path in csv_files:
        try:
            temp_df = pd.read_csv(file_path)
            # 从文件名中提取产品名称 (tour_name)
            filename = os.path.basename(file_path)
            match = re.match(r'^\d+-(.*?)_\d+_attraction', filename)
            tour_name = match.group(1).replace('_', ' ') if match else filename.split('.')[0]
            temp_df['tour_name'] = tour_name
            df_list.append(temp_df)
        except Exception as e:
            print(f"读取文件 {file_path} 出错: {e}")

    df_raw = pd.concat(df_list, ignore_index=True)
    # 标准化列名
    df_raw.columns = df_raw.columns.str.strip().str.lower().str.replace(' ', '_')
    print(f"原始数据合并完毕！共 {len(df_raw)} 条评论。")

    print("\n" + "="*70)
    print("【步骤 2】Level 1 基础清洗 (去除无用列、清理 HTML、格式化日期与评分)")
    print("="*70)
    
    # 2.1 剔除无用行政列
    cols_to_drop = ['user_profile', 'user_avatar', 'disclaimer']
    df_clean = df_raw.drop(columns=[c for c in cols_to_drop if c in df_raw.columns])
    
    # 2.2 删除核心列 (review_text 或 rating) 缺失的行
    df_clean = df_clean.dropna(subset=['review_text', 'rating']).copy()
    
    # 2.3 清理 HTML 换行符与转义字符
    df_clean['review_text'] = df_clean['review_text'].apply(clean_html_linebreaks)
    if 'review_title' in df_clean.columns:
        df_clean['review_title'] = df_clean['review_title'].apply(clean_html_linebreaks)
        
    # 2.4 标准化评分 (1-5 整数)
    df_clean['rating'] = pd.to_numeric(df_clean['rating'], errors='coerce')
    df_clean = df_clean.dropna(subset=['rating'])
    df_clean['rating'] = df_clean['rating'].astype(int)
    df_clean = df_clean[(df_clean['rating'] >= 1) & (df_clean['rating'] <= 5)]
    
    # 2.5 日期标准化 (YYYY-MM-DD)
    df_clean['published_date'] = df_clean['published_date'].apply(clean_published_date)
    
    # 2.6 标准化 Trip Type
    df_clean['trip_type'] = df_clean.apply(standardize_trip_type, axis=1)
    
    # 2.7 是否附带照片特征 (has_photo)
    if 'photos' in df_clean.columns:
        df_clean['has_photo'] = df_clean['photos'].apply(lambda x: 1 if pd.notna(x) and str(x).strip() != '' else 0)
        df_clean = df_clean.drop(columns=['photos'])

    print("\n" + "="*70)
    print("【步骤 3】去重审计 (去除严格重复与近重复评论)")
    print("="*70)
    
    temp_user = df_clean['user_name'].fillna('anonymous_user')
    temp_norm_text = df_clean['review_text'].astype(str).str.lower().str.replace(r'\s+', ' ', regex=True).str.strip()
    norm_mask = pd.Series(list(zip(temp_user, temp_norm_text)), index=df_clean.index).duplicated(keep='first')
    
    removed_count = norm_mask.sum()
    df_dedup = df_clean.loc[~norm_mask].copy()
    print(f"去重完成！剔除重复评论 {removed_count} 条，剩余 Clean 评论 {len(df_dedup)} 条。")

    print("\n" + "="*70)
    print("【步骤 4】语种识别 (Language Identification)")
    print("="*70)
    
    df_dedup['review_text'] = df_dedup['review_text'].fillna('')
    df_dedup['review_title'] = df_dedup['review_title'].fillna('')
    full_text_str = df_dedup['review_title'] + ' ' + df_dedup['review_text']
    
    df_dedup['language'] = full_text_str.apply(detect_language)
    df_dedup['is_english'] = (df_dedup['language'] == 'English').astype(int)
    print(f"语种检测完成：英文评论 {(df_dedup['is_english']==1).sum()} 条 ({(df_dedup['is_english'].mean()*100):.2f}%)，非英文评论 {(df_dedup['is_english']==0).sum()} 条。")

    print("\n" + "="*70)
    print("【步骤 5】Level 2 深度特征工程 (地理解析、NLP指标、VADER情感得分、低空特征)")
    print("="*70)
    
    # 5.1 地理位置解析
    print("正在解析游客所在城市、州与国家...")
    loc_records = df_dedup['user_location'].fillna('').apply(parse_location).tolist()
    loc_df = pd.DataFrame(loc_records, index=df_dedup.index)
    df_dedup['user_city'] = loc_df['user_city']
    df_dedup['user_state'] = loc_df['user_state']
    df_dedup['user_country'] = loc_df['user_country']
    df_dedup['is_us_domestic'] = loc_df['is_us_domestic']

    # 5.2 NLP 文本统计特征
    print("正在计算文本长度、词数、感叹号及大写比例...")
    df_dedup['review_word_count'] = df_dedup['review_text'].apply(lambda x: len(x.split()))
    df_dedup['review_char_count'] = df_dedup['review_text'].apply(len)
    df_dedup['title_word_count'] = df_dedup['review_title'].apply(lambda x: len(x.split()))
    df_dedup['exclamation_count'] = df_dedup['review_text'].apply(lambda x: x.count('!'))
    df_dedup['uppercase_ratio'] = df_dedup['review_text'].apply(
        lambda x: (sum(1 for c in x if c.isupper()) / len(x)) if len(x) > 0 else 0.0
    )

    # 5.3 VADER 情感分析
    print("正在计算 VADER 情绪得分 (sentiment_polarity)...")
    sentiments = df_dedup['review_text'].apply(lambda x: sia.polarity_scores(x) if x else {'compound': 0.0, 'pos': 0.0, 'neg': 0.0, 'neu': 1.0})
    df_dedup['sentiment_polarity'] = [s['compound'] for s in sentiments]
    df_dedup['sentiment_pos'] = [s['pos'] for s in sentiments]
    df_dedup['sentiment_neg'] = [s['neg'] for s in sentiments]

    # 5.4 低空旅游领域 9 大维度特征抽取 (匹配 0/1 哑变量)
    print("正在提取低空观光领域专属体验特征 (0/1 指标)...")
    full_text_lower = full_text_str.str.lower()
    
    # (1) 安全与心理感知
    df_dedup['safety_mention'] = full_text_lower.str.contains(r'\b(safe|safety|nervous|calm|scared|frightened|smooth|landing|reassured|comfort|comfortable|ease|relax|reassure|anxious|anxiety)\b', regex=True).astype(int)
    # (2) 机型对比 (直升机 vs 飞机)
    df_dedup['helicopter_comparison'] = full_text_lower.str.contains(r'\b(helicopter|heli|chopper)\b', regex=True).astype(int)
    # (3) 价格与性价比
    df_dedup['price_value_mention'] = full_text_lower.str.contains(r'\b(economical|cheap|expensive|price|priced|worth|dime|penny|value|cost|budget|affordable|deal)\b', regex=True).astype(int)
    # (4) 四类景观要素
    df_dedup['coast_mention'] = full_text_lower.str.contains(r'\b(coast|napali|na pali|shore|beach|ocean|sea|pacific)\b', regex=True).astype(int)
    df_dedup['canyon_mention'] = full_text_lower.str.contains(r'\b(canyon|waimea|gorge|valley|canyons)\b', regex=True).astype(int)
    df_dedup['waterfall_mention'] = full_text_lower.str.contains(r'\b(waterfall|waterfalls|falls|fall)\b', regex=True).astype(int)
    df_dedup['wildlife_mention'] = full_text_lower.str.contains(r'\b(whale|whales|dolphin|wildlife|turtle|turtles)\b', regex=True).astype(int)
    # (5) 天气与能见度
    df_dedup['weather_mention'] = full_text_lower.str.contains(r'\b(weather|cloud|clouds|cloudy|rain|rainy|wind|windy|headwind|visibility|clear|sun|sunny|rainbow)\b', regex=True).astype(int)
    # (6) 飞行服务切分: 空中飞行解说组 (Flight Crew: Pilot=Guide) vs 地面服务组 (Ground Staff) vs 同行家属 (Companion)
    print("正在通过 coref_resolver 执行低空领域服务角色实体提取 (空中飞行解说 vs 地面接待)...")
    from coref_resolver import resolve_review_roles
    
    role_results = full_text_str.apply(resolve_review_roles).tolist()
    role_df = pd.DataFrame(role_results, index=df_dedup.index)
    
    df_dedup['flight_crew_mention'] = role_df['flight_crew_mentioned']  # 空中飞行与解说组 (Pilot & Tour Guide)
    df_dedup['ground_staff_mention'] = role_df['ground_staff_mentioned'] # 地面与前台接待组 (Desk, Check-in, Office)
    df_dedup['companion_mention'] = role_df['companion_mentioned']       # 同行家属/同伴 (Husband, Wife, Family)
    
    # 兼容性保留
    df_dedup['pilot_mention'] = df_dedup['flight_crew_mention']
    df_dedup['staff_service_mention'] = df_dedup['ground_staff_mention']
    df_dedup['guide_mention'] = full_text_lower.str.contains(r'\b(guide|tour guide|narrator)\b', regex=True).astype(int)
    df_dedup['pilot_service_mention'] = ((df_dedup['flight_crew_mention'] == 1) | (df_dedup['ground_staff_mention'] == 1)).astype(int)
    
    # (7) 纪念场景 (蜜月/生日/Bucket list)
    df_dedup['special_occasion'] = full_text_lower.str.contains(r'\b(honeymoon|anniversary|birthday|bucket list|highlight|50th|celebrat\w*|special occasion)\b', regex=True).astype(int)
    # 机型分类
    tour_lower = df_dedup['tour_name'].fillna('').str.lower()
    df_dedup['aircraft_type'] = np.where(
        tour_lower.str.contains('helicopter|heli'), 'Helicopter',
        np.where(tour_lower.str.contains('plane|wings|flight|air'), 'Airplane', 'Other/Unspecified')
    )

    print("\n" + "="*70)
    print("【步骤 6】导出清洗数据集与校验文件至 data/cleaned_datasets/ 目录")
    print("="*70)
    
    out_dir = os.path.join("data", "cleaned_datasets")
    os.makedirs(out_dir, exist_ok=True)
    master_output = os.path.join(out_dir, "tripadvisor_processed_master.csv")
    df_dedup.to_csv(master_output, index=False, encoding='utf-8-sig')
    print(f"主数据集保存成功！ -> {master_output} ({len(df_dedup)} 行)")

    # 导出抽样集、非英文集及被剔除的重复评论集供人工检查
    out_dir = os.path.join("data", "cleaned_datasets")
    df_dedup.sample(n=min(500, len(df_dedup)), random_state=42).to_csv(os.path.join(out_dir, "manual_check_500.csv"), index=False, encoding='utf-8-sig')
    df_dedup.sample(n=min(2000, len(df_dedup)), random_state=42).to_csv(os.path.join(out_dir, "manual_check_2000.csv"), index=False, encoding='utf-8-sig')
    df_dedup[df_dedup['is_english']==0].to_csv(os.path.join(out_dir, "non_english_reviews.csv"), index=False, encoding='utf-8-sig')
    
    # 导出全部 6,683 条被剔除的重复评论审计表及一一对比映射表
    df_clean.loc[norm_mask].to_csv(os.path.join(out_dir, "deleted_duplicates_audit.csv"), index=False, encoding='utf-8-sig')
    
    # 构造左右对比表 (保留记录 vs 删除副本)
    dup_mask_all = df_clean.duplicated(subset=['user_name', 'review_text'], keep=False)
    df_dups_all = df_clean[dup_mask_all].copy()
    
    comparison_list = []
    temp_user_arr = df_dups_all['user_name'].fillna('anonymous_user')
    temp_norm_text_arr = df_dups_all['review_text'].astype(str).str.lower().str.replace(r'\s+', ' ', regex=True).str.strip()
    
    for (u, t), group in df_dups_all.groupby([temp_user_arr, temp_norm_text_arr]):
        kept_row = group.iloc[0]
        for i in range(1, len(group)):
            deleted_row = group.iloc[i]
            comparison_list.append({
                'user_name': u,
                'kept_in_master_tour': kept_row.get('tour_name', ''),
                'deleted_duplicate_tour': deleted_row.get('tour_name', ''),
                'kept_review_title': kept_row.get('review_title', ''),
                'deleted_review_title': deleted_row.get('review_title', ''),
                'review_text_snippet': str(kept_row.get('review_text', ''))[:150]
            })
            
    pd.DataFrame(comparison_list).to_csv(os.path.join(out_dir, "duplicate_pairs_comparison.csv"), index=False, encoding='utf-8-sig')
    print("抽样校验与对比 CSV (manual_check, non_english, deleted_duplicates_audit, duplicate_pairs_comparison) 已更新！")

    print("\n==================================================")
    print(" Master 数据流水线运行完毕！所有处理与特征均完成。")
    print("==================================================")

if __name__ == "__main__":
    main()
