import pandas as pd
import numpy as np
import re
from sklearn.feature_extraction.text import CountVectorizer
import nltk
from nltk.corpus import stopwords

# Ensure NLTK stopwords are available
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

def main():
    input_file = "tripadvisor_level1_cleaned.csv"
    print(f"Loading dataset from {input_file}...")
    df = pd.read_csv(input_file)
    print(f"Loaded {len(df)} cleaned review records.")

    # Combine title and review text
    df['full_text'] = (df['review_title'].fillna('') + ' ' + df['review_text'].fillna('')).str.lower()

    # Base English Stopwords
    stop_words = list(stopwords.words('english'))
    # Custom domain generic stop words (optional, to reveal meaningful domain phrases)
    custom_domain_stops = [
        'flight', 'tour', 'trip', 'time', 'us', 'get', 'got', 'would', 'also', 
        'one', 'took', 'see', 'saw', 'go', 'went', 'back', 'make', 'made', 'really',
        'great', 'good', 'amazing', 'awesome', 'wonderful', 'highly', 'recommend',
        'recommended', 'definitely', 'experience', 'day', 'way', 'took', 'like'
    ]
    extended_stop_words = list(set(stop_words + custom_domain_stops))

    print("\n" + "="*50)
    print("1. EXTRACTING HIGH-FREQUENCY BIGRAMS (2-Word Phrases)")
    print("="*50)

    vec_bigram = CountVectorizer(
        ngram_range=(2, 2),
        stop_words=stop_words,
        min_df=10
    )
    X_bi = vec_bigram.fit_transform(df['full_text'])
    bi_counts = np.asarray(X_bi.sum(axis=0)).flatten()
    bi_feature_names = vec_bigram.get_feature_names_out()

    # Calculate review occurrence count (binary presence per review)
    X_bi_bin = (X_bi > 0).astype(int)
    bi_doc_counts = np.asarray(X_bi_bin.sum(axis=0)).flatten()

    df_bigram = pd.DataFrame({
        'phrase': bi_feature_names,
        'total_mentions': bi_counts,
        'review_count': bi_doc_counts,
        'review_percentage': (bi_doc_counts / len(df) * 100).round(2)
    }).sort_values(by='total_mentions', ascending=False)

    df_bigram.to_csv("high_freq_bigrams.csv", index=False)
    print("Top 20 Bigrams (With standard stopwords removed):")
    print(df_bigram.head(20).to_string(index=False))

    print("\n" + "="*50)
    print("2. EXTRACTING HIGH-FREQUENCY TRIGRAMS (3-Word Phrases)")
    print("="*50)

    vec_trigram = CountVectorizer(
        ngram_range=(3, 3),
        stop_words=stop_words,
        min_df=5
    )
    X_tri = vec_trigram.fit_transform(df['full_text'])
    tri_counts = np.asarray(X_tri.sum(axis=0)).flatten()
    tri_feature_names = vec_trigram.get_feature_names_out()

    X_tri_bin = (X_tri > 0).astype(int)
    tri_doc_counts = np.asarray(X_tri_bin.sum(axis=0)).flatten()

    df_trigram = pd.DataFrame({
        'phrase': tri_feature_names,
        'total_mentions': tri_counts,
        'review_count': tri_doc_counts,
        'review_percentage': (tri_doc_counts / len(df) * 100).round(2)
    }).sort_values(by='total_mentions', ascending=False)

    df_trigram.to_csv("high_freq_trigrams.csv", index=False)
    print("Top 20 Trigrams:")
    print(df_trigram.head(20).to_string(index=False))

    print("\n" + "="*50)
    print("3. EXTRACTING DOMAIN SUBSTANTIVE KEYWORDS (Extended Stopwords Filtered)")
    print("="*50)

    vec_substantive = CountVectorizer(
        ngram_range=(1, 2),
        stop_words=extended_stop_words,
        min_df=10
    )
    X_sub = vec_substantive.fit_transform(df['full_text'])
    sub_counts = np.asarray(X_sub.sum(axis=0)).flatten()
    sub_feature_names = vec_substantive.get_feature_names_out()

    X_sub_bin = (X_sub > 0).astype(int)
    sub_doc_counts = np.asarray(X_sub_bin.sum(axis=0)).flatten()

    df_substantive = pd.DataFrame({
        'word_or_phrase': sub_feature_names,
        'total_mentions': sub_counts,
        'review_count': sub_doc_counts,
        'review_percentage': (sub_doc_counts / len(df) * 100).round(2)
    }).sort_values(by='total_mentions', ascending=False)

    df_substantive.to_csv("high_freq_substantive_keywords.csv", index=False)
    print("Top 25 Domain Substantive Keywords/Phrases:")
    print(df_substantive.head(25).to_string(index=False))

if __name__ == "__main__":
    main()
