"""
================================================================================
低空旅游 TripAdvisor 评论分析与科研绘图 Master 脚本 (run_analysis_and_plots.py)
================================================================================
本脚本读取 run_data_pipeline.py 生成的主数据集 (tripadvisor_processed_master.csv)，
执行以下核心分析与图表绘制：
  1. 生成全球游客分布热力地图 (world_map_reviews.png)
  2. 生成美国本土游客来源州热力地图 (us_map_reviews.png)
  3. 生成低空观光 9 大特征维度提及率柱状图 (low_altitude_feature_distribution.png)
  4. 提取 N-gram 高频词与短语统计表 (high_freq_bigrams.csv / trigrams.csv)
  5. 导出论文用的表格摘要 CSV (国家分布表、美国州分布表)
================================================================================
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import CountVectorizer
import nltk
from nltk.corpus import stopwords

# 设置科研绘图样式
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
plt.rcParams['axes.edgecolor'] = '#cccccc'
plt.rcParams['axes.linewidth'] = 0.8

def main():
    cleaned_dir = os.path.join("data", "cleaned_datasets")
    derived_dir = os.path.join("data", "derived_outputs")
    os.makedirs(cleaned_dir, exist_ok=True)
    os.makedirs(derived_dir, exist_ok=True)
    os.makedirs("figures", exist_ok=True)
    
    input_file = os.path.join(cleaned_dir, "tripadvisor_processed_master.csv")
    if not os.path.exists(input_file):
        input_file = os.path.join("data", "tripadvisor_processed_master.csv")
        if not os.path.exists(input_file):
            input_file = "tripadvisor_processed_master.csv"
            if not os.path.exists(input_file):
                print("提示：找不到主数据集 tripadvisor_processed_master.csv，请先运行 python run_data_pipeline.py！")
                return

    print(f"正在加载主数据集 {input_file}...")
    df = pd.read_csv(input_file)
    print(f"成功加载 {len(df)} 条完整数据。")

    # ==============================================================================
    # 1. 绘制全球与美国游客热力地图 (Plotly Choropleth Maps)
    # ==============================================================================
    try:
        import plotly.express as px
        
        # (1) 全球分布地图
        print("正在绘制图 1：全球游客分布热力地图...")
        country_counts = df[df['user_country'] != 'Unknown']['user_country'].value_counts().reset_index()
        country_counts.columns = ['user_country', 'count']
        
        fig_world = px.choropleth(
            country_counts,
            locations="user_country",
            locationmode="country names",
            color="count",
            hover_name="user_country",
            hover_data=["count"],
            color_continuous_scale="Greens",
            title="Figure 1: Global Distribution of TripAdvisor Low-Altitude Sightseeing Reviews",
            labels={'count': 'Number of Reviews'}
        )
        fig_world.update_layout(
            geo=dict(showframe=False, showcoastlines=True, coastlinecolor="DarkGray", projection_type='equirectangular'),
            font=dict(family="Arial, sans-serif", size=13),
            margin={"r":10,"t":50,"l":10,"b":10}
        )
        world_map_path = os.path.join("figures", "world_map_reviews.png")
        fig_world.write_image(world_map_path, width=1200, height=650, scale=2)
        print(f"已保存: {world_map_path}")

        # (2) 美国本土各州分布地图
        print("正在绘制图 2：美国本土游客来源州分布热力地图...")
        state_counts = df[df['is_us_domestic'] == 1]['user_state'].value_counts().reset_index()
        state_counts.columns = ['user_state', 'count']
        
        fig_us = px.choropleth(
            state_counts,
            locations="user_state",
            locationmode="USA-states",
            color="count",
            hover_name="user_state",
            hover_data=["count"],
            scope="usa",
            color_continuous_scale="Greens",
            title="Figure 2: US Domestic Tourist Origin State Distribution",
            labels={'count': 'Number of Reviews'}
        )
        fig_us.update_layout(
            geo=dict(showframe=False, showcoastlines=True),
            font=dict(family="Arial, sans-serif", size=13),
            margin={"r":10,"t":50,"l":10,"b":10}
        )
        us_map_path = os.path.join("figures", "us_map_reviews.png")
        fig_us.write_image(us_map_path, width=1100, height=650, scale=2)
        print(f"已保存: {us_map_path}")

    except Exception as e:
        print(f"地图绘图提示 (Plotly): {e}")

    # ==============================================================================
    # 2. 绘制低空体验 9 大维度特征提及率柱状图
    # ==============================================================================
    print("正在绘制图 3：低空体验特征维度提及率柱状图...")
    feature_labels = {
        'pilot_mention': 'Pilot & Aviator Mention',
        'safety_mention': 'Safety & Anxiety Perception',
        'price_value_mention': 'Price & Value Perception',
        'weather_mention': 'Weather & Visibility',
        'staff_service_mention': 'Ground Staff & Service',
        'canyon_mention': 'Canyon & Valley Views',
        'special_occasion': 'Special Travel Occasion',
        'helicopter_comparison': 'Helicopter vs Plane Comparison',
        'coast_mention': 'Coast & Ocean Scenery',
        'guide_mention': 'Tour Guide Mention',
        'waterfall_mention': 'Waterfall Mentions'
    }
    feature_cols = [c for c in feature_labels.keys() if c in df.columns]
    rates = df[feature_cols].mean() * 100
    
    summary_df = pd.DataFrame({
        'Feature': [feature_labels[c] for c in feature_cols],
        'Percentage': rates.values
    }).sort_values(by='Percentage', ascending=True)

    fig, ax = plt.subplots(figsize=(10, 6.5), dpi=300)
    bars = ax.barh(summary_df['Feature'], summary_df['Percentage'], color='#2E8B57', edgecolor='#1C5434', height=0.65)

    for bar in bars:
        width = bar.get_width()
        ax.annotate(f'{width:.1f}%',
                    xy=(width, bar.get_y() + bar.get_height() / 2),
                    xytext=(5, 0),
                    textcoords="offset points",
                    ha='left', va='center', fontsize=10, fontweight='bold', color='#1C5434')

    ax.set_title("Prevalence of Low-Altitude Experience Attributes in Reviews (%)", fontsize=14, pad=15, fontweight='bold')
    ax.set_xlabel("Percentage of Reviews Containing Attribute (%)", fontsize=11)
    ax.set_xlim(0, max(summary_df['Percentage']) * 1.15)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()

    feature_dist_path = os.path.join("figures", "low_altitude_feature_distribution.png")
    plt.savefig(feature_dist_path, dpi=300)
    plt.close()
    print(f"已保存: {feature_dist_path}")

    # ==============================================================================
    # 3. 提取高频词与短语统计表 (Bigrams & Trigrams)
    # ==============================================================================
    print("正在提取高频短语 (Bigrams & Trigrams)...")
    full_text = (df['review_title'].fillna('') + ' ' + df['review_text'].fillna('')).str.lower()
    
    try:
        stop_words = list(stopwords.words('english'))
    except:
        stop_words = 'english'

    # (1) Bigrams (双词短语)
    vec_bi = CountVectorizer(ngram_range=(2, 2), stop_words=stop_words, min_df=10)
    X_bi = vec_bi.fit_transform(full_text)
    df_bi = pd.DataFrame({
        'phrase': vec_bi.get_feature_names_out(),
        'total_mentions': np.asarray(X_bi.sum(axis=0)).flatten(),
        'review_count': np.asarray((X_bi > 0).sum(axis=0)).flatten()
    }).sort_values(by='total_mentions', ascending=False)
    df_bi['review_percentage'] = (df_bi['review_count'] / len(df) * 100).round(2)
    df_bi.to_csv(os.path.join(derived_dir, "high_freq_bigrams.csv"), index=False)

    # (2) Trigrams (三词短语)
    vec_tri = CountVectorizer(ngram_range=(3, 3), stop_words=stop_words, min_df=5)
    X_tri = vec_tri.fit_transform(full_text)
    df_tri = pd.DataFrame({
        'phrase': vec_tri.get_feature_names_out(),
        'total_mentions': np.asarray(X_tri.sum(axis=0)).flatten(),
        'review_count': np.asarray((X_tri > 0).sum(axis=0)).flatten()
    }).sort_values(by='total_mentions', ascending=False)
    df_tri['review_percentage'] = (df_tri['review_count'] / len(df) * 100).round(2)
    df_tri.to_csv(os.path.join(derived_dir, "high_freq_trigrams.csv"), index=False)
    print("高频短语词表导出完毕！(data/derived_outputs/high_freq_bigrams.csv / high_freq_trigrams.csv)")

    # ==============================================================================
    # 4. 导出论文表格摘要 CSV
    # ==============================================================================
    # 国家分布前 15 名
    c_summary = df['user_country'].value_counts().head(15).reset_index()
    c_summary.columns = ['Country', 'Review_Count']
    c_summary['Percentage (%)'] = (c_summary['Review_Count'] / len(df) * 100).round(2)
    c_summary.to_csv(os.path.join(derived_dir, "paper_table_country_distribution.csv"), index=False)

    # 美国州分布前 15 名
    s_summary = df[df['is_us_domestic']==1]['user_state'].value_counts().head(15).reset_index()
    s_summary.columns = ['US_State', 'Review_Count']
    s_summary['Percentage_of_US (%)'] = (s_summary['Review_Count'] / df['is_us_domestic'].sum() * 100).round(2)
    s_summary.to_csv(os.path.join(derived_dir, "paper_table_us_state_distribution.csv"), index=False)
    print("论文分布摘要表导出完毕！(data/derived_outputs/paper_table_country_distribution.csv / paper_table_us_state_distribution.csv)")

    print("\n==================================================")
    print(" 所有分析与绘图任务运行完毕！")
    print("==================================================")

if __name__ == "__main__":
    main()
