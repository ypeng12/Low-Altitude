"""
================================================================================
低空旅游角色实体匹配与服务切分模块 (coref_resolver.py)
================================================================================
领域逻辑纠正：
  1. 空中服务组 (In-Flight Crew / Flight Guide): 在低空观光中，飞行员 (Pilot) 与导游 (Guide) 是同一个角色 (飞行员边开飞机边解说)。
     因此将 pilot 与 guide 归为统一的空中飞行组 (flight_crew_mention)。
  2. 地面服务组 (Ground Staff): 前台、登机办理、办公地勤人员 (desk, check-in, staff, office agent) 是独立的地面服务主体，单独切分 (ground_staff_mention)。
  3. 同行家属/同伴 (Companion): 游客家属同伴 (husband, wife, daughter, friend) 独立识别 (companion_mention)。
================================================================================
"""

import re

# 1. 空中飞行与解说组 (Pilot = Guide)
FLIGHT_CREW_TERMS = {
    'pilot', 'captain', 'co-pilot', 'copilot', 'aviator', 'flyer', 
    'guide', 'tour guide', 'narrator', 'docent', 'instructor', 'narration',
    'bruce', 'sarah', 'dan', 'mike', 'dave', 'mark', 'john', 'paul', 'chris', 'steve'
}

# 2. 地面与前台接待组 (Ground Staff)
GROUND_STAFF_TERMS = {
    'staff', 'desk', 'check-in', 'checkin', 'crew', 'host', 'office', 'agent', 
    'lady at desk', 'front desk', 'ground staff', 'reception', 'counter'
}

# 3. 同行家属与乘客组 (Companion Guests)
COMPANION_TERMS = {
    'husband', 'wife', 'daughter', 'son', 'kids', 'children', 'mother', 'father', 
    'mom', 'dad', 'sister', 'brother', 'friend', 'friends', 'partner', 'fiance', 'family'
}

def resolve_review_roles(text):
    """
    基于低空观光行业逻辑的角色实体匹配与代词指代消解函数 (Sentence-level Context Window Coreference Resolver)。
    """
    if not isinstance(text, str) or not text.strip():
        return {
            'flight_crew_mentioned': 0,
            'ground_staff_mentioned': 0,
            'companion_mentioned': 0
        }
    
    text_lower = text.lower()
    # 按照句子结束标点符号及换行拆分为单句
    sentences = [s.strip() for s in re.split(r'[.!?\n]+', text_lower) if s.strip()]
    
    has_flight_crew = 0
    has_ground_staff = 0
    has_companion = 0
    
    # 存储每个单句的显式提及状态 (flight_crew, ground_staff, companion)
    sentence_mentions = []
    
    # 代词词集
    male_pronouns = {'he', 'him', 'his', 'himself'}
    female_pronouns = {'she', 'her', 'hers', 'herself'}
    
    for idx, sentence in enumerate(sentences):
        words = set(re.findall(r'\b[a-z]+\b', sentence))
        
        # 1. 显式领域词库匹配
        fc = 1 if words.intersection(FLIGHT_CREW_TERMS) or 'na pali' in sentence or 'tour guide' in sentence else 0
        gs = 1 if words.intersection(GROUND_STAFF_TERMS) or 'front desk' in sentence or 'check in' in sentence else 0
        cp = 1 if words.intersection(COMPANION_TERMS) else 0
        
        # 2. 检查当前句是否含有代词
        has_male = any(w in words for w in male_pronouns)
        has_female = any(w in words for w in female_pronouns)
        
        # 3. 句级上下文窗口指代消解 (向上检索前 1 句的实体)
        if idx > 0:
            prev_fc, prev_gs, prev_cp = sentence_mentions[idx-1]
            
            # 如果当前句含 he/him 且前句提到了飞行员或同伴，继承其角色指代
            if has_male:
                if prev_fc:
                    fc = 1
                if prev_cp:
                    cp = 1
                    
            # 如果当前句含 she/her 且前句提到了地勤或同伴，继承其角色指代
            if has_female:
                if prev_gs:
                    gs = 1
                if prev_cp:
                    cp = 1
        
        sentence_mentions.append((fc, gs, cp))
        
        if fc: has_flight_crew = 1
        if gs: has_ground_staff = 1
        if cp: has_companion = 1
        
    return {
        'flight_crew_mentioned': has_flight_crew,
        'ground_staff_mentioned': has_ground_staff,
        'companion_mentioned': has_companion
    }

if __name__ == "__main__":
    test_1 = "Pilot Sarah gave an amazing flight narration during the tour."
    test_2 = "The front desk staff was very helpful during check-in."
    test_3 = "My husband loved the view."
    test_4 = "We had a great pilot. He flew us smoothly over the canyon."
    test_5 = "The desk lady welcomed us. She explained everything clearly."
    test_6 = "I went with my daughter. She was so excited about the trip."
    
    print("Test 1 (Flight Crew Sarah):", resolve_review_roles(test_1))
    print("Test 2 (Ground Staff):", resolve_review_roles(test_2))
    print("Test 3 (Companion):", resolve_review_roles(test_3))
    print("Test 4 (Coref he -> pilot):", resolve_review_roles(test_4))
    print("Test 5 (Coref she -> staff):", resolve_review_roles(test_5))
    print("Test 6 (Coref she -> companion daughter):", resolve_review_roles(test_6))

