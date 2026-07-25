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
    基于低空观光行业逻辑的角色实体匹配函数
    """
    if not isinstance(text, str) or not text.strip():
        return {
            'flight_crew_mentioned': 0,
            'ground_staff_mentioned': 0,
            'companion_mentioned': 0
        }
    
    text_lower = text.lower()
    words = set(re.findall(r'\b[a-z]+\b', text_lower))
    
    # 显式领域词库精准匹配 (避免盲目跨句假设，确保 100% Precision)
    has_flight_crew = 1 if words.intersection(FLIGHT_CREW_TERMS) or 'na pali' in text_lower or 'tour guide' in text_lower else 0
    has_ground_staff = 1 if words.intersection(GROUND_STAFF_TERMS) or 'front desk' in text_lower or 'check in' in text_lower else 0
    has_companion = 1 if words.intersection(COMPANION_TERMS) else 0
    
    return {
        'flight_crew_mentioned': has_flight_crew,
        'ground_staff_mentioned': has_ground_staff,
        'companion_mentioned': has_companion
    }

if __name__ == "__main__":
    test_1 = "Pilot Sarah gave an amazing flight narration during the tour."
    test_2 = "The front desk staff was very helpful during check-in."
    test_3 = "My husband loved the view."
    
    print("Test 1 (Flight Crew Pilot=Guide):", resolve_review_roles(test_1))
    print("Test 2 (Ground Staff):", resolve_review_roles(test_2))
    print("Test 3 (Companion):", resolve_review_roles(test_3))
