import sys
import pandas as pd

# Set output encoding to UTF-8 for console printing
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

RAW_FILE = 'tripadvisor_merged_raw.csv'
CLEAN_FILE = 'tripadvisor_level1_cleaned.csv'

def audit_duplicates():
    print("==================================================")
    print("      TRIPADVISOR DATASET DUPLICATE AUDIT         ")
    print("==================================================")
    
    # Load datasets
    df_raw = pd.read_csv(RAW_FILE)
    df_clean = pd.read_csv(CLEAN_FILE)
    
    print(f"1. Raw merged dataset total rows: {len(df_raw)}")
    print(f"   Level 1 cleaned dataset total rows: {len(df_clean)}")
    print(f"   Total rows removed during Level 1: {len(df_raw) - len(df_clean)}")
    
    print("\n--------------------------------------------------")
    print(" 1. 严格完全重复 (Exact Duplicates)")
    print("--------------------------------------------------")
    dup_raw_exact = df_raw.duplicated(subset=['user_name', 'review_text'], keep=False).sum()
    dup_clean_exact = df_clean.duplicated(subset=['user_name', 'review_text'], keep=False).sum()
    print(f"   - Raw 数据集中严格相同 (user_name + review_text) 的重复行数: {dup_raw_exact}")
    print(f"   - Level 1 清洗后数据集中严格相同 (user_name + review_text) 的重复行数: {dup_clean_exact}")
    
    print("\n--------------------------------------------------")
    print(" 2. 空格/换行微小差异的近重复 (Near-Duplicates)")
    print("--------------------------------------------------")
    df_clean['text_norm'] = df_clean['review_text'].astype(str).str.lower().str.replace(r'\s+', ' ', regex=True).str.strip()
    dup_norm = df_clean[df_clean.duplicated(subset=['text_norm'], keep=False)]
    print(f"   - 忽略文本内部连续空格/换行差异后的近重复行数: {len(dup_norm)}")
    if len(dup_norm) > 0:
        for norm_t, g in dup_norm.groupby('text_norm'):
            print(f"     发现近重复 ({len(g)} 条):")
            for _, r in g.iterrows():
                print(f"       User: {r['user_name']} | Date: {r['published_date']} | Tour: {r['tour_name']}")
    else:
        print("     所有连续空格导致的近重复均已在 Level 1 清洗阶段成功剔除！")

    print("\n--------------------------------------------------")
    print(" 3. 同一游客同天发表的改写/修改版评论 (Same User/Date Rewrites)")
    print("--------------------------------------------------")
    dup_user_title_date = df_clean[df_clean.duplicated(subset=['user_name', 'review_title', 'published_date'], keep=False)]
    print(f"   - 同一游客在同一天对同一标题发表的改写评论行数: {len(dup_user_title_date)}")
    if len(dup_user_title_date) > 0:
        for (user, title, date), g in dup_user_title_date.groupby(['user_name', 'review_title', 'published_date']):
            print(f"\n     游客: '{user}' | 日期: '{date}' | 标题: '{title}' ({len(g)} 条版本):")
            for _, r in g.iterrows():
                print(f"       - Tour: {r['tour_name']}")
                print(f"         Text: {r['review_text'][:120]!r}...")

    print("\n--------------------------------------------------")
    print(" 4. 同一游客对不同项目的多条评价 (Multiple Reviews by Same User)")
    print("--------------------------------------------------")
    user_counts = df_clean['user_name'].value_counts()
    multi_users = user_counts[user_counts > 1]
    multi_reviews_total_rows = df_clean[df_clean['user_name'].isin(multi_users.index)].shape[0]
    print(f"   - 发表超过1条评论的独立 Username 数量: {len(multi_users)}")
    print(f"   - 这些高频游客贡献的总评论行数: {multi_reviews_total_rows}")
    print("     前 5 名高频评价游客示例:")
    for uname, cnt in multi_users.head(5).items():
        print(f"       - 游客 '{uname}': 共发表 {cnt} 条评论")

    print("\n==================================================")
    print("                 审计完成！                       ")
    print("==================================================")

if __name__ == '__main__':
    audit_duplicates()
