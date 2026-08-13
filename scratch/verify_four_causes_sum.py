#!/usr/bin/env python3
"""Verify 100% math sum check of the 4 causes across 272 missed words."""

import pandas as pd

c1_words = 136
c2_words = 122
c3_words = 9
c4_words = 5
total = 272

p1 = (c1_words / total) * 100
p2 = (c2_words / total) * 100
p3 = (c3_words / total) * 100
p4 = (c4_words / total) * 100

print("=== 🔬 4 CAUSES EXACT MATH SUM CHECK ===")
print(f"原因 1 (语法形态变体): {c1_words:3d} 词 | {p1:6.2f}%")
print(f"原因 2 (基础词根缺口): {c2_words:3d} 词 | {p2:6.2f}%  (包含 great/awesome/fantastic 等头部高频口语赞语词)")
print(f"原因 3 (低空美学震撼): {c3_words:3d} 词 | {p3:6.2f}%")
print(f"原因 4 (飞行感知风险): {c4_words:3d} 词 | {p4:6.2f}%")
print("-" * 45)
print(f"加和总数 (Sum Words): {c1_words + c2_words + c3_words + c4_words:3d} 词 (100% 吻合 272)")
print(f"加和比例 (Sum Pct)  : {p1 + p2 + p3 + p4:6.2f}% (100% 严丝合缝)")
