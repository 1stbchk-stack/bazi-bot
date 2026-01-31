#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試用例配置 - 用於驗證算法一致性
最後更新: 2026年1月30日
"""

# ========== 管理員測試案例 ==========
ADMIN_TEST_CASES = [
    {
        'bazi_data1': {'year': 1985, 'month': 10, 'day': 24, 'hour': 10, 'minute': 0, 'longitude': 114.17, 'gender': '男'},
        'bazi_data2': {'year': 1988, 'month': 2, 'day': 15, 'hour': 14, 'minute': 0, 'longitude': 114.17, 'gender': '女'},
        'expected_range': (78, 82),
        'description': '測試救命優先：女方木旺救男方燥土',
        'expected_model': '供求型'
    },
    {
        'bazi_data1': {'year': 1990, 'month': 5, 'day': 12, 'hour': 8, 'minute': 30, 'longitude': 114.17, 'gender': '男'},
        'bazi_data2': {'year': 1992, 'month': 8, 'day': 20, 'hour': 16, 'minute': 0, 'longitude': 114.17, 'gender': '女'},
        'expected_range': (68, 72),
        'description': '測試現實保底：地支微沖但無致命傷',
        'expected_model': '平衡型'
    },
    {
        'bazi_data1': {'year': 1982, 'month': 3, 'day': 5, 'hour': 12, 'minute': 0, 'longitude': 114.17, 'gender': '男'},
        'bazi_data2': {'year': 1984, 'month': 12, 'day': 12, 'hour': 22, 'minute': 0, 'longitude': 114.17, 'gender': '女'},
        'expected_range': (82, 86),
        'description': '測試神煞加持：本身極夾，加上天乙貴人保底',
        'expected_model': '平衡型'
    },
    {
        'bazi_data1': {'year': 1995, 'month': 11, 'day': 30, 'hour': 4, 'minute': 0, 'longitude': 114.17, 'gender': '男'},
        'bazi_data2': {'year': 1993, 'month': 4, 'day': 5, 'hour': 10, 'minute': 0, 'longitude': 114.17, 'gender': '女'},
        'expected_range': (58, 62),
        'description': '測試不對稱性：男對女極迷戀，女對男極大壓',
        'expected_model': '供求型'
    },
    {
        'bazi_data1': {'year': 1980, 'month': 7, 'day': 15, 'hour': 18, 'minute': 0, 'longitude': 114.17, 'gender': '男'},
        'bazi_data2': {'year': 1980, 'month': 1, 'day': 10, 'hour': 2, 'minute': 0, 'longitude': 114.17, 'gender': '女'},
        'expected_range': (40, 48),
        'description': '測試致命風險：三刑帶沖，應觸發強制終止線≤45分',
        'expected_model': '相欠型'
    },
    {
        'bazi_data1': {'year': 1988, 'month': 8, 'day': 8, 'hour': 8, 'minute': 0, 'longitude': 114.17, 'gender': '男'},
        'bazi_data2': {'year': 1991, 'month': 6, 'day': 22, 'hour': 14, 'minute': 0, 'longitude': 114.17, 'gender': '女'},
        'expected_range': (75, 80),
        'description': '測試專業化解：傷官配印，算法應識別化解邏輯',
        'expected_model': '平衡型'
    },
    {
        'bazi_data1': {'year': 1998, 'month': 12, 'day': 1, 'hour': 20, 'minute': 0, 'longitude': 114.17, 'gender': '男'},
        'bazi_data2': {'year': 2000, 'month': 3, 'day': 15, 'hour': 9, 'minute': 0, 'longitude': 114.17, 'gender': '女'},
        'expected_range': (70, 75),
        'description': '測試普通人模型：五行平穩但無大亮點',
        'expected_model': '平衡型'
    },
    {
        'bazi_data1': {'year': 1975, 'month': 4, 'day': 20, 'hour': 12, 'minute': 0, 'longitude': 114.17, 'gender': '男'},
        'bazi_data2': {'year': 1990, 'month': 10, 'day': 5, 'hour': 16, 'minute': 0, 'longitude': 114.17, 'gender': '女'},
        'expected_range': (62, 67),
        'description': '測試年齡校正：年齡差距大，分數應受壓但受能量救應補償',
        'expected_model': '供求型'
    },
    {
        'bazi_data1': {'year': 1993, 'month': 9, 'day': 9, 'hour': 9, 'minute': 0, 'longitude': 114.17, 'gender': '男'},
        'bazi_data2': {'year': 1993, 'month': 12, 'day': 25, 'hour': 21, 'minute': 0, 'longitude': 114.17, 'gender': '女'},
        'expected_range': (82, 86),
        'description': '測試能量對接：金水相生且喜用同步',
        'expected_model': '平衡型'
    },
    {
        'bazi_data1': {'year': 1987, 'month': 2, 'day': 2, 'hour': 2, 'minute': 0, 'longitude': 114.17, 'gender': '男'},
        'bazi_data2': {'year': 1989, 'month': 11, 'day': 11, 'hour': 11, 'minute': 0, 'longitude': 114.17, 'gender': '女'},
        'expected_range': (65, 70),
        'description': '測試人格風險上限：多項中度風險，需驗證扣分是否鎖死',
        'expected_model': '混合型'
    },
    {
        'bazi_data1': {'year': 1990, 'month': 6, 'day': 15, 'hour': 12, 'minute': 0, 'longitude': 120.0, 'gender': '男'},
        'bazi_data2': {'year': 1992, 'month': 3, 'day': 20, 'hour': 12, 'minute': 0, 'longitude': 114.17, 'gender': '女'},
        'expected_range': (70, 76),
        'description': '測試真太陽時：不同經度時間校正',
        'expected_model': '平衡型'
    },
    {
        'bazi_data1': {'year': 1985, 'month': 10, 'day': 24, 'hour': 23, 'minute': 30, 'longitude': 114.17, 'gender': '男'},
        'bazi_data2': {'year': 1988, 'month': 2, 'day': 15, 'hour': 22, 'minute': 30, 'longitude': 114.17, 'gender': '女'},
        'expected_range': (75, 81),
        'description': '測試23:00換日規則：23:30應算翌日',
        'expected_model': '平衡型'
    },
    {
        'bazi_data1': {'year': 1990, 'month': 1, 'day': 1, 'hour': 0, 'minute': 0, 'longitude': 114.17, 'gender': '男'},
        'bazi_data2': {'year': 1992, 'month': 6, 'day': 15, 'hour': 12, 'minute': 0, 'longitude': 114.17, 'gender': '女'},
        'expected_range': (68, 74),
        'description': '測試神煞保底：有紅鸞但其他條件普通',
        'expected_model': '平衡型'
    },
    {
        'bazi_data1': {'year': 1988, 'month': 8, 'day': 8, 'hour': 8, 'minute': 8, 'longitude': 114.17, 'gender': '男'},
        'bazi_data2': {'year': 1990, 'month': 10, 'day': 10, 'hour': 10, 'minute': 10, 'longitude': 114.17, 'gender': '女'},
        'expected_range': (72, 78),
        'description': '測試輸入哈希：相同八字多次計算應完全一致',
        'expected_model': '平衡型'
    },
    {
        'bazi_data1': {'year': 1995, 'month': 5, 'day': 20, 'hour': 14, 'minute': 0, 'longitude': 114.17, 'gender': '男'},
        'bazi_data2': {'year': 1997, 'month': 8, 'day': 15, 'hour': 10, 'minute': 0, 'longitude': 114.17, 'gender': '女'},
        'expected_range': (80, 85),
        'description': '測試天合地合：天干五合地支六合',
        'expected_model': '平衡型'
    },
    {
        'bazi_data1': {'year': 1989, 'month': 11, 'day': 11, 'hour': 11, 'minute': 11, 'longitude': 114.17, 'gender': '男'},
        'bazi_data2': {'year': 1992, 'month': 2, 'day': 2, 'hour': 2, 'minute': 2, 'longitude': 114.17, 'gender': '女'},
        'expected_range': (55, 62),
        'description': '測試沖剋嚴重：地支多沖無化解',
        'expected_model': '相欠型'
    },
    {
        'bazi_data1': {'year': 2000, 'month': 1, 'day': 1, 'hour': 0, 'minute': 0, 'longitude': 114.17, 'gender': '男'},
        'bazi_data2': {'year': 2001, 'month': 6, 'day': 15, 'hour': 12, 'minute': 0, 'longitude': 114.17, 'gender': '女'},
        'expected_range': (85, 90),
        'description': '測試年輕組合：五行流通順暢',
        'expected_model': '平衡型'
    },
    {
        'bazi_data1': {'year': 1978, 'month': 9, 'day': 18, 'hour': 18, 'minute': 0, 'longitude': 114.17, 'gender': '男'},
        'bazi_data2': {'year': 1982, 'month': 3, 'day': 8, 'hour': 8, 'minute': 0, 'longitude': 114.17, 'gender': '女'},
        'expected_range': (60, 66),
        'description': '測試中年組合：穩定但有沖剋',
        'expected_model': '混合型'
    },
    {
        'bazi_data1': {'year': 1994, 'month': 7, 'day': 7, 'hour': 7, 'minute': 0, 'longitude': 114.17, 'gender': '男'},
        'bazi_data2': {'year': 1996, 'month': 12, 'day': 24, 'hour': 18, 'minute': 0, 'longitude': 114.17, 'gender': '女'},
        'expected_range': (88, 92),
        'description': '測試極品組合：天合地合帶貴人',
        'expected_model': '平衡型'
    }
]

# ========== 一致性測試案例 ==========
CONSISTENCY_TEST_CASES = [
    {
        'name': '相同八字一致性測試',
        'bazi_data': {'year': 1990, 'month': 6, 'day': 15, 'hour': 12, 'minute': 0, 'longitude': 114.17, 'gender': '男'},
        'expected_hash': '預期哈希值',
        'description': '同一八字在不同功能中應產生相同結果'
    },
    {
        'name': '時辰邊界測試',
        'bazi_data': {'year': 1990, 'month': 6, 'day': 15, 'hour': 23, 'minute': 30, 'longitude': 114.17, 'gender': '男'},
        'expected_day': '翌日日柱',
        'description': '23:00後應算翌日日柱'
    },
    {
        'name': '真太陽時校正測試',
        'bazi_data': {'year': 1990, 'month': 6, 'day': 15, 'hour': 12, 'minute': 0, 'longitude': 120.0, 'gender': '男'},
        'expected_hour_pillar': '校正後時柱',
        'description': '不同經度應有不同真太陽時'
    }
]

# ========== 邊界測試案例 ==========
BOUNDARY_TEST_CASES = [
    {
        'name': '最小年份測試',
        'bazi_data': {'year': 1900, 'month': 1, 'day': 1, 'hour': 0, 'minute': 0, 'longitude': 114.17, 'gender': '男'},
        'description': '測試最小支持年份'
    },
    {
        'name': '最大年份測試',
        'bazi_data': {'year': 2025, 'month': 12, 'day': 31, 'hour': 23, 'minute': 59, 'longitude': 114.17, 'gender': '女'},
        'description': '測試最大支持年份'
    },
    {
        'name': '閏年測試',
        'bazi_data': {'year': 2000, 'month': 2, 'day': 29, 'hour': 12, 'minute': 0, 'longitude': 114.17, 'gender': '男'},
        'description': '測試閏年日期處理'
    },
    {
        'name': '時辰邊界測試',
        'bazi_data': {'year': 1990, 'month': 6, 'day': 15, 'hour': 0, 'minute': 0, 'longitude': 114.17, 'gender': '女'},
        'description': '測試子時開始'
    },
    {
        'name': '分鐘缺失測試',
        'bazi_data': {'year': 1990, 'month': 6, 'day': 15, 'hour': 12, 'longitude': 114.17, 'gender': '男'},
        'description': '測試分鐘缺失時的默認處理'
    }
]

# ========== 性能測試案例 ==========
PERFORMANCE_TEST_CASES = [
    {
        'name': '批量配對測試',
        'count': 100,
        'description': '測試100次配對的性能表現'
    },
    {
        'name': '搜索功能測試',
        'year_range': (1990, 2000),
        'description': '測試10年範圍搜索的性能'
    },
    {
        'name': '數據庫查詢測試',
        'query_count': 1000,
        'description': '測試數據庫查詢性能'
    }
]