import pandas as pd
import numpy as np
import re
import os
import sys

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

# Comprehensive dictionary mapping common English emotion/CATE words to Chinese
TRANSLATION_MAP = {
    # CATE & Top Emotion Words
    'worth': '值得/划算',
    'small': '小型的/紧凑的',
    'interesting': '有趣的/引人入胜的',
    'cool': '酷炫的/棒的',
    'extra': '额外的/附加体验',
    'ease': '轻松/平稳自如',
    'personable': '平易近人的/亲切的',
    'completely': '完全地/彻底地',
    'unbelievable': '不可思议的/难以置信的',
    'calm': '平静镇定的/从容的',
    'skilled': '操控熟练的/专业的',
    'choice': '明智的选择/契合的决策',
    'courteous': '礼貌客气的/有礼的',
    'fortunate': '幸运的/有幸体验的',
    'interest': '兴趣/看点',
    'absolute': '绝对的/完美的',
    'organized': '组织良好的/有序的',
    'sense': '心理感知/安全感',
    'superb': '极好的/卓越的',
    'forward': '前向视角/期待视角',
    'cold': '高空微凉/客舱气温',
    'noise': '噪音/降噪耳机',
    'cheap': '实惠划算的/价格亲民的',
    'wrong': '偏差/偏差纠错',
    'strongly': '强烈推荐',
    'standing': '空中悬停/飞行姿态',
    'actual': '真实体验/实际的',
    'polite': '礼貌周到的',
    'working': '设备良好运转的',
    'major': '核心亮点/主要看点',
    'attention': '关照/注重细节',
    'question': '互动解答/解答疑问',
    'overcast': '多云天色的/阴天的',
    'contact': '预订沟通/联系客服',
    'accessible': '便捷易达的',
    'inaccessible': '陆路不可达的/观光独特性',
    'effort': '用心安排/商家付出',
    'spirit': '情绪氛围/精神感悟',
    'fascinating': '令人着迷的/吸睛的',
    'capture': '捕捉照片/定格瞬间',
    'grateful': '感激的/感恩的',
    'advantage': '低空视角优势',
    'priceless': '无价的/珍贵的',
    'afford': '负担得起的/物有所值',
    'balance': '姿态平衡/飞行平稳',
    'delayed': '顺延/因天气延迟',
    'crystal': '晶莹剔透的/水质清澈的',
    'epic': '史诗级的/震撼的',
    'agree': '高度认同/一致赞同',
    'grandeur': '雄伟壮丽的地貌',
    'extraordinary': '非凡卓越的',
    'convenient': '方便快捷的',
    'gracious': '亲切体贴的',
    'hospitality': '热情好客的',
    'culture': '文化与历史解说',
    'fair': '公道合理的/定价公平的',
    'uncomfortable': '身体不适/颠簸反感',
    'lack': '缺乏/美中不足的',
    'careful': '谨慎平稳驾驶的',
    
    # Emotion Shift & Negative Words
    'fear': '恐惧/对飞行的害怕',
    'nervous': '紧张不安的',
    'scared': '害怕恐惧的',
    'afraid': '担忧害怕的',
    'anxious': '焦虑不安的',
    'terrified': '极度恐惧的',
    'frightened': '受惊吓的',
    'horrible': '极差的/糟糕透顶的',
    'terrible': '可怕的/极度不满的',
    'wasted': '浪钱浪费时间的',
    'awful': '极糟糕的',
    'disappointing': '令人失望的',
    'ruined': '毁掉行程的',
    'beware': '当心/谨防陷阱的',
    'waste': '浪费钱财/白费的',
    'refused': '遭拒/退款被拒的',
    'delay': '航班延迟/耽误的',
    'cancel': '取消行程/退订的',
    'maintenance': '故障维保/机械维修的',
    'boring': '枯燥乏味无聊的',
    'worse': '更糟糕的',
    'overpriced': '价格虚高/偏贵的',
    'cramped': '客舱狭窄拥挤的',
    'bad': '差劲的',
    'poor': '服务贫乏劣质的',
    'disgust': '厌恶反感',
    'anger': '愤怒发怒',
    'sadness': '悲伤遗憾',
    
    # Positive Praise & Quality Words
    'spectacular': '壮观震撼的',
    'breathtaking': '令人屏息的/顶级赞叹',
    'unbelievable': '难以置信的/超乎想象的',
    'friendly': '友好的/热情的',
    'professional': '专业严谨的',
    'experienced': '经验丰富的',
    'outstanding': '卓越杰出的',
    'wonderful': '极其美妙的',
    'fantastic': '太棒了/梦幻般的',
    'amazing': '惊艳的/令人惊叹的',
    'awesome': '极其出色的',
    'excellent': '优异卓越的',
    'perfect': '完美的/十全十美的',
    'incredible': '不可思议的',
    'stunning': '绝美的/令人震惊的美',
    'smooth': '平稳顺畅的',
    'safe': '安全有保障的',
    'reassuring': '令人放心的/贴心的',
    'informative': '解说知识丰富的',
    'helpful': '大有帮助的/热心的',
    'patient': '耐心周到的',
    'punctual': '准时守时的',
    'impeccable': '无可挑剔的',
    'exquisite': '精美绝伦的',
    'sensational': '轰动出色的',
    'immaculate': '完美无瑕的',
    'stellar': '顶尖出色的',
    'timely': '及时高效的',
    'leisurely': '悠闲从容的',
    'refreshing': '令人耳目一新的',
    'authentic': '地道真实的',
    'joy': '愉悦喜悦',
    'trust': '信任依赖',
    'anticipation': '期待期盼',
    'surprise': '惊喜惊奇'
}

# 1. Process CATE 107 Words CSV & Excel
cate_path = 'data/derived_outputs/cate_words_curated_107.csv'
if os.path.exists(cate_path):
    cate_df = pd.read_csv(cate_path)
    
    def get_cate_translation(row):
        word_raw = str(row['CATE 词汇']).strip()
        m = re.match(r'^([a-zA-Z\-]+)', word_raw)
        pure_w = m.group(1).lower() if m else word_raw.lower()
        
        # Check current translation
        if '语义类别' in row and str(row['CATE 词汇']).find('(') != -1:
            # Already formatted like "worth (值得/划算)"
            return row['CATE 词汇']
        elif pure_w in TRANSLATION_MAP:
            return f"{pure_w} ({TRANSLATION_MAP[pure_w]})"
        else:
            return row['CATE 词汇']

    # Update translations in CATE 107
    updated_cate_rows = []
    for idx, row in cate_df.iterrows():
        word_raw = str(row['CATE 词汇']).strip()
        m = re.match(r'^([a-zA-Z\-]+)', word_raw)
        pure_w = m.group(1).lower() if m else word_raw.lower()
        
        cn_trans = TRANSLATION_MAP.get(pure_w, '体验与服务维度词')
        word_formatted = f"{pure_w} ({cn_trans})"
        
        updated_cate_rows.append({
            '序号': row.get('序号', idx+1),
            'CATE 词汇': word_formatted,
            '英文单词 (Pure Word)': pure_w,
            '中文释义 (Translation)': cn_trans,
            '出现频次 (Freq)': row.get('出现频次 (Freq)', 0),
            '平均星级 (Stars)': row.get('平均星级 (Stars)', 0.0),
            'VADER 得分': row.get('VADER 得分', 0.0),
            '语义类别': row.get('语义类别', 'CATE 领域属性')
        })
        
    updated_cate_df = pd.DataFrame(updated_cate_rows)
    
    # Save to CSV and Excel
    updated_cate_df.to_csv('data/derived_outputs/cate_words_curated_107.csv', index=False, encoding='utf-8-sig')
    updated_cate_df.to_excel('data/derived_outputs/cate_words_curated_107_translated.xlsx', index=False)
    print("Updated cate_words_curated_107.csv and created cate_words_curated_107_translated.xlsx!")

# 2. Process Pure Emotion Words Stats (635 Words) CSV & Excel
nrc_path = 'data/derived_outputs/nrc_pure_emotion_words_stats.csv'
if os.path.exists(nrc_path):
    nrc_df = pd.read_csv(nrc_path)
    
    nrc_rows = []
    for idx, row in nrc_df.iterrows():
        w = str(row['word']).strip().lower()
        cn_trans = TRANSLATION_MAP.get(w, '情绪与感知词汇')
        
        nrc_rows.append({
            '序号 (Index)': idx + 1,
            '英文单词 (Word)': w,
            '中文翻译 (Translation)': cn_trans,
            '词汇全称 (Formatted)': f"{w} ({cn_trans})",
            '出现频次 (Frequency)': row['count'],
            '平均游客星级 (Star Rating)': round(row['mean_rating'], 3),
            '固有 VADER 极性 (Intrinsic Polarity)': round(row['intrinsic_polarity'], 3),
            'Plutchik 情绪分类 (Category)': row['category']
        })
        
    translated_nrc_df = pd.DataFrame(nrc_rows)
    
    translated_nrc_df.to_csv('data/derived_outputs/nrc_pure_emotion_words_translated.csv', index=False, encoding='utf-8-sig')
    translated_nrc_df.to_excel('data/derived_outputs/nrc_pure_emotion_words_translated.xlsx', index=False)
    print("Created nrc_pure_emotion_words_translated.csv and nrc_pure_emotion_words_translated.xlsx!")

