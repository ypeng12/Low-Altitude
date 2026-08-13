#!/usr/bin/env python3
"""Generate a clean, beautiful, publication-ready Chinese PDF report from RESEARCH_NOTES_CN.md."""

from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Register Chinese TrueType Font
pdfmetrics.registerFont(TTFont('STHeiti', '/System/Library/Fonts/STHeiti Light.ttc'))
pdfmetrics.registerFont(TTFont('Songti', '/System/Library/Fonts/Supplemental/Songti.ttc'))

pdf_path = Path('data/derived_outputs/Low_Altitude_Tourism_Research_Notes_CN.pdf')
doc = SimpleDocTemplate(
    str(pdf_path),
    pagesize=letter,
    rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40
)

styles = getSampleStyleSheet()

# Custom Paragraph Styles
title_style = ParagraphStyle(
    'DocTitle',
    parent=styles['Normal'],
    fontName='STHeiti',
    fontSize=20,
    leading=26,
    textColor=colors.HexColor('#1E3A8A'),
    alignment=1, # Center
    spaceAfter=15
)

subtitle_style = ParagraphStyle(
    'DocSubTitle',
    parent=styles['Normal'],
    fontName='STHeiti',
    fontSize=11,
    leading=16,
    textColor=colors.HexColor('#475569'),
    alignment=1,
    spaceAfter=20
)

h1_style = ParagraphStyle(
    'Heading1_CN',
    parent=styles['Normal'],
    fontName='STHeiti',
    fontSize=14,
    leading=20,
    textColor=colors.HexColor('#1E40AF'),
    spaceBefore=15,
    spaceAfter=10,
    keepWithNext=True
)

h2_style = ParagraphStyle(
    'Heading2_CN',
    parent=styles['Normal'],
    fontName='STHeiti',
    fontSize=11,
    leading=16,
    textColor=colors.HexColor('#0F766E'),
    spaceBefore=12,
    spaceAfter=6,
    keepWithNext=True
)

body_style = ParagraphStyle(
    'Body_CN',
    parent=styles['Normal'],
    fontName='STHeiti',
    fontSize=9,
    leading=14,
    textColor=colors.HexColor('#1E293B'),
    spaceAfter=6
)

bullet_style = ParagraphStyle(
    'Bullet_CN',
    parent=styles['Normal'],
    fontName='STHeiti',
    fontSize=9,
    leading=14,
    textColor=colors.HexColor('#334155'),
    leftIndent=12,
    spaceAfter=4
)

alert_style = ParagraphStyle(
    'Alert_CN',
    parent=styles['Normal'],
    fontName='STHeiti',
    fontSize=9.5,
    leading=15,
    textColor=colors.HexColor('#92400E'),
    backColor=colors.HexColor('#FEF3C7'),
    borderColor=colors.HexColor('#F59E0B'),
    borderWidth=1,
    borderPadding=10,
    spaceBefore=10,
    spaceAfter=10
)

table_header_style = ParagraphStyle(
    'TableHeader',
    parent=styles['Normal'],
    fontName='STHeiti',
    fontSize=8.5,
    leading=12,
    textColor=colors.white,
    alignment=1
)

table_body_style = ParagraphStyle(
    'TableBody',
    parent=styles['Normal'],
    fontName='STHeiti',
    fontSize=8,
    leading=11,
    textColor=colors.HexColor('#1E293B')
)

story = []

# Title Banner
story.append(Paragraph("低空观光旅游 TripAdvisor 评论处理与计量特征工程", title_style))
story.append(Paragraph("中文实验研究笔记与方法论报告 (RESEARCH_NOTES_CN.pdf)", subtitle_style))
story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#1E3A8A"), spaceAfter=15))

# Alert Box
story.append(Paragraph("<b>💡 核心结论与状态</b>：全量 21,215 条 Clean English 真实评论已完成三阶段语料库推导。Master 金标准代码本包含 <b>638 个纯正情感词</b>，与 8,088 个剔除词保持 100% 零交集完备划分。", alert_style))

# Section 1
story.append(Paragraph("一、 语料库推导情感代码本：三阶段推导方法论", h1_style))
story.append(Paragraph("为避免盲目套用通用的标准情感词典（如 NRC、VADER 或 LIWC），本项目开发了一套针对低空观光旅游（Low-Altitude Air Tourism）的三阶段语料库推导与人机协同审定方法论：", body_style))

story.append(Paragraph("• <b>Stage 1: 500 条探索性抽样 (Discovery Sample)</b>：分层随机抽样 (Seed 42)，跨 46 个产品与星级均衡抽样，提炼出 372 个核心情感词。", bullet_style))
story.append(Paragraph("• <b>Stage 2: 2,000 条金标准扩充 (Gold Expansion)</b>：分层随机抽样 (Seed 100，含 1,814 条新评论)，扩充 173 个新情感词。前 2,500 条样本构建了 545 个情感词的初始代码本。", bullet_style))
story.append(Paragraph("• <b>Stage Final: 18,901 条全量补齐 (Corpus Completion)</b>：扫描剩余未抽样评论，提取 4,213 个候选词，通过 JSON 规则与人机协同审定，合成 <b>638 个 Master 金标准情感词</b>！", bullet_style))

# Mathematical Addition Table
story.append(Spacer(1, 8))
story.append(Paragraph("<b>金标准情感词典递进相加公式与阶段关系表：</b>", h2_style))

data_math = [
    [Paragraph("阶段名称", table_header_style), Paragraph("抽样评论规模", table_header_style), Paragraph("新增情感词数", table_header_style), Paragraph("累计金标准情感词总数", table_header_style)],
    [Paragraph("Stage 1 探索性抽样", table_body_style), Paragraph("500 条", table_body_style), Paragraph("372 个词", table_body_style), Paragraph("372 个词", table_body_style)],
    [Paragraph("Stage 2 金标准扩充", table_body_style), Paragraph("2,000 条 (1,814 新)", table_body_style), Paragraph("173 个词", table_body_style), Paragraph("545 个词 (2,500 样本宇宙)", table_body_style)],
    [Paragraph("Stage Final 全量补齐", table_body_style), Paragraph("18,901 条未抽样", table_body_style), Paragraph("65 个词", table_body_style), Paragraph("608 个词", table_body_style)],
    [Paragraph("用户高频词拉回校准", table_body_style), Paragraph("全量 21,215 语料库", table_body_style), Paragraph("30 个词", table_body_style), Paragraph("<b>638 个 Master 终极词</b>", table_body_style)]
]

t_math = Table(data_math, colWidths=[130, 110, 110, 150])
t_math.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E40AF')),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')])
]))
story.append(t_math)

story.append(Spacer(1, 12))
story.append(Paragraph("二、 错别字与形态变体归一化协议 (canonical_lemma)", h1_style))
story.append(Paragraph("实证统计显示，约 0.8% 的真实游客评论包含拼写错误或形态变形。Master 代码本构建了 canonical_lemma 双索引映射：", body_style))

data_typo = [
    [Paragraph("评论原始词 (word)", table_header_style), Paragraph("归一化标准词根 (canonical_lemma)", table_header_style), Paragraph("细分情感维度 (emotion_category)", table_header_style), Paragraph("中文直接翻译", table_header_style), Paragraph("21,215 全量词频", table_header_style)],
    [Paragraph("suprised", table_body_style), Paragraph("surprised", table_body_style), Paragraph("Surprise", table_body_style), Paragraph("感到惊喜惊讶的 (错别字变体)", table_body_style), Paragraph("4", table_body_style)],
    [Paragraph("suprise", table_body_style), Paragraph("surprise", table_body_style), Paragraph("Surprise", table_body_style), Paragraph("惊喜 / 意料之外 (错别字变体)", table_body_style), Paragraph("5", table_body_style)],
    [Paragraph("exhilerating", table_body_style), Paragraph("exhilarating", table_body_style), Paragraph("Excitement", table_body_style), Paragraph("令人兴奋刺激酣畅地 (错别字变体)", table_body_style), Paragraph("7", table_body_style)],
    [Paragraph("aprehensive", table_body_style), Paragraph("apprehensive", table_body_style), Paragraph("Anxiety / Fear", table_body_style), Paragraph("感到忧虑不安的 (错别字变体)", table_body_style), Paragraph("3", table_body_style)],
    [Paragraph("dissapointed", table_body_style), Paragraph("disappointed", table_body_style), Paragraph("Disappointment", table_body_style), Paragraph("感到失望的 (错别字变体)", table_body_style), Paragraph("8", table_body_style)],
    [Paragraph("worries", table_body_style), Paragraph("worry", table_body_style), Paragraph("Anxiety / Worry", table_body_style), Paragraph("担忧 / 挂虑", table_body_style), Paragraph("24", table_body_style)],
    [Paragraph("worrying", table_body_style), Paragraph("worry", table_body_style), Paragraph("Anxiety / Worry", table_body_style), Paragraph("令人担心的", table_body_style), Paragraph("37", table_body_style)]
]

t_typo = Table(data_typo, colWidths=[90, 110, 100, 130, 70])
t_typo.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F766E')),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F0FDFA')])
]))
story.append(t_typo)

story.append(Spacer(1, 12))
story.append(Paragraph("三、 核心研究发现与数据洞察", h1_style))
story.append(Paragraph("<b>1. 风险-安全-惊险缓解机制 (Risk-Safety-Thrill Mitigation Dynamics)</b>：描述心理风险与紧张的词汇（nervous, fear, scared, jitters, claustrophobia）在 39.02% 的评论中出现。当评论中同时出现风险词与飞行员安全词（safe, smooth, reassuring, calming）时，游客给出 5 星好评的概率高达 94.2%！", bullet_style))
story.append(Paragraph("<b>2. 高空视觉美学情绪的主导地位 (Dominance of Aerial Aesthetic Emotions)</b>：高唤起视觉震撼词（breathtakingly, spectacular, sublime, captivating, wowed, mesmerized）在飞行评论中的出现频率是地面游览的 4.2 倍，是驱动极高满意度与口碑推荐的最关键因子。", bullet_style))

story.append(Spacer(1, 12))
story.append(Paragraph("四、 全量产出文件目录指南", h1_style))

data_files = [
    [Paragraph("产物名称", table_header_style), Paragraph("文件格式", table_header_style), Paragraph("记录条数", table_header_style), Paragraph("描述与使用建议", table_header_style)],
    [Paragraph("Master 金标准情感代码本", table_body_style), Paragraph("Excel / CSV", table_body_style), Paragraph("638 个词", table_body_style), Paragraph("核心主代码本 (含 canonical_lemma 与细分类)", table_body_style)],
    [Paragraph("Master 被剔除词日志", table_body_style), Paragraph("Excel / CSV", table_body_style), Paragraph("8,088 个词", table_body_style), Paragraph("核心主审计日志 (含所有人名地名与中性词)", table_body_style)],
    [Paragraph("Stage 1 探索性情感词表", table_body_style), Paragraph("Excel / CSV", table_body_style), Paragraph("372 个词", table_body_style), Paragraph("Stage 1 (N=500) 提炼出的情感词", table_body_style)],
    [Paragraph("Stage 2 扩充情感词表", table_body_style), Paragraph("Excel / CSV", table_body_style), Paragraph("173 个词", table_body_style), Paragraph("Stage 2 (N=2,000) 扩充出的情感词", table_body_style)],
    [Paragraph("Stage Final 新增情感词表", table_body_style), Paragraph("Excel / CSV", table_body_style), Paragraph("65 个词", table_body_style), Paragraph("Stage Final (N=18,901) 补齐出的新情感词", table_body_style)]
]

t_files = Table(data_files, colWidths=[130, 80, 70, 220])
t_files.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4338CA')),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#EEF2FF')])
]))
story.append(t_files)

doc.build(story)
print(f'Successfully generated Chinese PDF report at: {pdf_path}')
