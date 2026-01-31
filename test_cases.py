#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試用例配置 - 更新版，兼容new_calculator.py
用於驗證算法一致性
最後更新: 2026年2月1日
"""

# ========== 1.1 管理員測試案例開始 ==========
# 20組八字測試案例，用於驗證算法準確性
# 格式更新為兼容new_calculator.py接口
ADMIN_TEST_CASES = [
    {
        'bazi_data1': {
            'year': 1985, 'month': 10, 'day': 24, 'hour': 10,
            'minute': 0, 'longitude': 114.17, 'gender': '男',
            'hour_confidence': 'high'
        },
        'bazi_data2': {
            'year': 1988, 'month': 2, 'day': 15, 'hour': 14,
            'minute': 0, 'longitude': 114.17, 'gender': '女',
            'hour_confidence': 'high'
        },
        'expected_range': (78, 82),
        'description': '測試救命優先：女方木旺救男方燥土',
        'expected_model': '供求型'
    },
    {
        'bazi_data1': {
            'year': 1990, 'month': 5, 'day': 12, 'hour': 8,
            'minute': 30, 'longitude': 114.17, 'gender': '男',
            'hour_confidence': 'high'
        },
        'bazi_data2': {
            'year': 1992, 'month': 8, 'day': 20, 'hour': 16,
            'minute': 0, 'longitude': 114.17, 'gender': '女',
            'hour_confidence': 'high'
        },
        'expected_range': (68, 72),
        'description': '測試現實保底：地支微沖但無致命傷',
        'expected_model': '平衡型'
    },
    {
        'bazi_data1': {
            'year': 1982, 'month': 3, 'day': 5, 'hour': 12,
            'minute': 0, 'longitude': 114.17, 'gender': '男',
            'hour_confidence': 'high'
        },
        'bazi_data2': {
            'year': 1984, 'month': 12, 'day': 12, 'hour': 22,
            'minute': 0, 'longitude': 114.17, 'gender': '女',
            'hour_confidence': 'high'
        },
        'expected_range': (82, 86),
        'description': '測試神煞加持：本身極夾，加上天乙貴人保底',
        'expected_model': '平衡型'
    },
    {
        'bazi_data1': {
            'year': 1995, 'month': 11, 'day': 30, 'hour': 4,
            'minute': 0, 'longitude': 114.17, 'gender': '男',
            'hour_confidence': 'high'
        },
        'bazi_data2': {
            'year': 1993, 'month': 4, 'day': 5, 'hour': 10,
            'minute': 0, 'longitude': 114.17, 'gender': '女',
            'hour_confidence': 'high'
        },
        'expected_range': (58, 62),
        'description': '測試不對稱性：男對女極迷戀，女對男極大壓',
        'expected_model': '供求型'
    },
    {
        'bazi_data1': {
            'year': 1980, 'month': 7, 'day': 15, 'hour': 18,
            'minute': 0, 'longitude': 114.17, 'gender': '男',
            'hour_confidence': 'high'
        },
        'bazi_data2': {
            'year': 1980, 'month': 1, 'day': 10, 'hour': 2,
            'minute': 0, 'longitude': 114.17, 'gender': '女',
            'hour_confidence': 'high'
        },
        'expected_range': (40, 48),
        'description': '測試致命風險：三刑帶沖，應觸發強制終止線≤45分',
        'expected_model': '相欠型'
    },
    {
        'bazi_data1': {
            'year': 1988, 'month': 8, 'day': 8, 'hour': 8,
            'minute': 0, 'longitude': 114.17, 'gender': '男',
            'hour_confidence': 'high'
        },
        'bazi_data2': {
            'year': 1991, 'month': 6, 'day': 22, 'hour': 14,
            'minute': 0, 'longitude': 114.17, 'gender': '女',
            'hour_confidence': 'high'
        },
        'expected_range': (75, 80),
        'description': '測試專業化解：傷官配印，算法應識別化解邏輯',
        'expected_model': '平衡型'
    },
    {
        'bazi_data1': {
            'year': 1998, 'month': 12, 'day': 1, 'hour': 20,
            'minute': 0, 'longitude': 114.17, 'gender': '男',
            'hour_confidence': 'high'
        },
        'bazi_data2': {
            'year': 2000, 'month': 3, 'day': 15, 'hour': 9,
            'minute': 0, 'longitude': 114.17, 'gender': '女',
            'hour_confidence': 'high'
        },
        'expected_range': (70, 75),
        'description': '測試普通人模型：五行平穩但無大亮點',
        'expected_model': '平衡型'
    },
    {
        'bazi_data1': {
            'year': 1975, 'month': 4, 'day': 20, 'hour': 12,
            'minute': 0, 'longitude': 114.17, 'gender': '男',
            'hour_confidence': 'high'
        },
        'bazi_data2': {
            'year': 1990, 'month': 10, 'day': 5, 'hour': 16,
            'minute': 0, 'longitude': 114.17, 'gender': '女',
            'hour_confidence': 'high'
        },
        'expected_range': (62, 67),
        'description': '測試年齡校正：年齡差距大，分數應受壓但受能量救應補償',
        'expected_model': '供求型'
    },
    {
        'bazi_data1': {
            'year': 1993, 'month': 9, 'day': 9, 'hour': 9,
            'minute': 0, 'longitude': 114.17, 'gender': '男',
            'hour_confidence': 'high'
        },
        'bazi_data2': {
            'year': 1993, 'month': 12, 'day': 25, 'hour': 21,
            'minute': 0, 'longitude': 114.17, 'gender': '女',
            'hour_confidence': 'high'
        },
        'expected_range': (82, 86),
        'description': '測試能量對接：金水相生且喜用同步',
        'expected_model': '平衡型'
    },
    {
        'bazi_data1': {
            'year': 1987, 'month': 2, 'day': 2, 'hour': 2,
            'minute': 0, 'longitude': 114.17, 'gender': '男',
            'hour_confidence': 'high'
        },
        'bazi_data2': {
            'year': 1989, 'month': 11, 'day': 11, 'hour': 11,
            'minute': 0, 'longitude': 114.17, 'gender': '女',
            'hour_confidence': 'high'
        },
        'expected_range': (65, 70),
        'description': '測試人格風險上限：多項中度風險，需驗證扣分是否鎖死',
        'expected_model': '混合型'
    },
    {
        'bazi_data1': {
            'year': 1990, 'month': 6, 'day': 15, 'hour': 12,
            'minute': 0, 'longitude': 120.0, 'gender': '男',
            'hour_confidence': 'high'
        },
        'bazi_data2': {
            'year': 1992, 'month': 3, 'day': 20, 'hour': 12,
            'minute': 0, 'longitude': 114.17, 'gender': '女',
            'hour_confidence': 'high'
        },
        'expected_range': (70, 76),
        'description': '測試真太陽時：不同經度時間校正',
        'expected_model': '平衡型'
    },
    {
        'bazi_data1': {
            'year': 1985, 'month': 10, 'day': 24, 'hour': 23,
            'minute': 30, 'longitude': 114.17, 'gender': '男',
            'hour_confidence': 'high'
        },
        'bazi_data2': {
            'year': 1988, 'month': 2, 'day': 15, 'hour': 22,
            'minute': 30, 'longitude': 114.17, 'gender': '女',
            'hour_confidence': 'high'
        },
        'expected_range': (75, 81),
        'description': '測試23:00換日規則：23:30應算翌日',
        'expected_model': '平衡型'
    },
    {
        'bazi_data1': {
            'year': 1990, 'month': 1, 'day': 1, 'hour': 0,
            'minute': 0, 'longitude': 114.17, 'gender': '男',
            'hour_confidence': 'high'
        },
        'bazi_data2': {
            'year': 1992, 'month': 6, 'day': 15, 'hour': 12,
            'minute': 0, 'longitude': 114.17, 'gender': '女',
            'hour_confidence': 'high'
        },
        'expected_range': (68, 74),
        'description': '測試神煞保底：有紅鸞但其他條件普通',
        'expected_model': '平衡型'
    },
    {
        'bazi_data1': {
            'year': 1988, 'month': 8, 'day': 8, 'hour': 8,
            'minute': 8, 'longitude': 114.17, 'gender': '男',
            'hour_confidence': 'high'
        },
        'bazi_data2': {
            'year': 1990, 'month': 10, 'day': 10, 'hour': 10,
            'minute': 10, 'longitude': 114.17, 'gender': '女',
            'hour_confidence': 'high'
        },
        'expected_range': (72, 78),
        'description': '測試輸入哈希：相同八字多次計算應完全一致',
        'expected_model': '平衡型'
    },
    {
        'bazi_data1': {
            'year': 1995, 'month': 5, 'day': 20, 'hour': 14,
            'minute': 0, 'longitude': 114.17, 'gender': '男',
            'hour_confidence': 'high'
        },
        'bazi_data2': {
            'year': 1997, 'month': 8, 'day': 15, 'hour': 10,
            'minute': 0, 'longitude': 114.17, 'gender': '女',
            'hour_confidence': 'high'
        },
        'expected_range': (80, 85),
        'description': '測試天合地合：天干五合地支六合',
        'expected_model': '平衡型'
    },
    {
        'bazi_data1': {
            'year': 1989, 'month': 11, 'day': 11, 'hour': 11,
            'minute': 11, 'longitude': 114.17, 'gender': '男',
            'hour_confidence': 'high'
        },
        'bazi_data2': {
            'year': 1992, 'month': 2, 'day': 2, 'hour': 2,
            'minute': 2, 'longitude': 114.17, 'gender': '女',
            'hour_confidence': 'high'
        },
        'expected_range': (55, 62),
        'description': '測試沖剋嚴重：地支多沖無化解',
        'expected_model': '相欠型'
    },
    {
        'bazi_data1': {
            'year': 2000, 'month': 1, 'day': 1, 'hour': 0,
            'minute': 0, 'longitude': 114.17, 'gender': '男',
            'hour_confidence': 'high'
        },
        'bazi_data2': {
            'year': 2001, 'month': 6, 'day': 15, 'hour': 12,
            'minute': 0, 'longitude': 114.17, 'gender': '女',
            'hour_confidence': 'high'
        },
        'expected_range': (85, 90),
        'description': '測試年輕組合：五行流通順暢',
        'expected_model': '平衡型'
    },
    {
        'bazi_data1': {
            'year': 1978, 'month': 9, 'day': 18, 'hour': 18,
            'minute': 0, 'longitude': 114.17, 'gender': '男',
            'hour_confidence': 'high'
        },
        'bazi_data2': {
            'year': 1982, 'month': 3, 'day': 8, 'hour': 8,
            'minute': 0, 'longitude': 114.17, 'gender': '女',
            'hour_confidence': 'high'
        },
        'expected_range': (60, 66),
        'description': '測試中年組合：穩定但有沖剋',
        'expected_model': '混合型'
    },
    {
        'bazi_data1': {
            'year': 1994, 'month': 7, 'day': 7, 'hour': 7,
            'minute': 0, 'longitude': 114.17, 'gender': '男',
            'hour_confidence': 'high'
        },
        'bazi_data2': {
            'year': 1996, 'month': 12, 'day': 24, 'hour': 18,
            'minute': 0, 'longitude': 114.17, 'gender': '女',
            'hour_confidence': 'high'
        },
        'expected_range': (88, 92),
        'description': '測試極品組合：天合地合帶貴人',
        'expected_model': '平衡型'
    },
    {
        'bazi_data1': {
            'year': 1990, 'month': 6, 'day': 15, 'hour': 12,
            'minute': 0, 'longitude': 114.17, 'gender': '男',
            'hour_confidence': 'high'
        },
        'bazi_data2': {
            'year': 1991, 'month': 7, 'day': 20, 'hour': 14,
            'minute': 0, 'longitude': 114.17, 'gender': '女',
            'hour_confidence': 'high'
        },
        'expected_range': (68, 74),
        'description': '測試兼容性：基本八字組合',
        'expected_model': '平衡型'
    }
]
# ========== 1.1 管理員測試案例結束 ==========

# ========== 1.2 邊界測試案例開始 ==========
BOUNDARY_TEST_CASES = [
    {
        'name': '最小年份測試',
        'bazi_data': {
            'year': 1900, 'month': 1, 'day': 1, 'hour': 0,
            'minute': 0, 'longitude': 114.17, 'gender': '男',
            'hour_confidence': 'high'
        },
        'description': '測試最小支持年份'
    },
    {
        'name': '最大年份測試',
        'bazi_data': {
            'year': 2025, 'month': 12, 'day': 31, 'hour': 23,
            'minute': 59, 'longitude': 114.17, 'gender': '女',
            'hour_confidence': 'high'
        },
        'description': '測試最大支持年份'
    },
    {
        'name': '閏年測試',
        'bazi_data': {
            'year': 2000, 'month': 2, 'day': 29, 'hour': 12,
            'minute': 0, 'longitude': 114.17, 'gender': '男',
            'hour_confidence': 'high'
        },
        'description': '測試閏年日期處理'
    },
    {
        'name': '時辰邊界測試',
        'bazi_data': {
            'year': 1990, 'month': 6, 'day': 15, 'hour': 0,
            'minute': 0, 'longitude': 114.17, 'gender': '女',
            'hour_confidence': 'high'
        },
        'description': '測試子時開始'
    },
    {
        'name': '分鐘缺失測試',
        'bazi_data': {
            'year': 1990, 'month': 6, 'day': 15, 'hour': 12,
            'longitude': 114.17, 'gender': '男',
            'hour_confidence': 'high'
        },
        'description': '測試分鐘缺失時的默認處理'
    },
    {
        'name': '置信度測試',
        'bazi_data': {
            'year': 1990, 'month': 6, 'day': 15, 'hour': 12,
            'minute': 0, 'longitude': 114.17, 'gender': '女',
            'hour_confidence': 'low'
        },
        'description': '測試低置信度情況'
    }
]
# ========== 1.2 邊界測試案例結束 ==========

# ========== 1.3 性能測試案例開始 ==========
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
        'name': '八字計算測試',
        'count': 1000,
        'description': '測試1000次八字計算的性能'
    }
]
# ========== 1.3 性能測試案例結束 ==========

# ========== 1.4 一致性測試案例開始 ==========
CONSISTENCY_TEST_CASES = [
    {
        'name': '相同八字一致性測試',
        'bazi_data': {
            'year': 1990, 'month': 6, 'day': 15, 'hour': 12,
            'minute': 0, 'longitude': 114.17, 'gender': '男',
            'hour_confidence': 'high'
        },
        'expected_hash': '預期哈希值',
        'description': '同一八字在不同功能中應產生相同結果'
    },
    {
        'name': '時辰邊界測試',
        'bazi_data': {
            'year': 1990, 'month': 6, 'day': 15, 'hour': 23,
            'minute': 30, 'longitude': 114.17, 'gender': '男',
            'hour_confidence': 'high'
        },
        'expected_day': '翌日日柱',
        'description': '23:00後應算翌日日柱'
    },
    {
        'name': '真太陽時校正測試',
        'bazi_data': {
            'year': 1990, 'month': 6, 'day': 15, 'hour': 12,
            'minute': 0, 'longitude': 120.0, 'gender': '男',
            'hour_confidence': 'high'
        },
        'expected_hour_pillar': '校正後時柱',
        'description': '不同經度應有不同真太陽時'
    }
]
# ========== 1.4 一致性測試案例結束 ==========

# ========== 1.5 師傅級測試案例開始 ==========
MASTER_TEST_CASES = [
    {
        'name': '師傅級案例1 - 極品組合',
        'bazi_data1': {
            'year': 1988, 'month': 8, 'day': 8, 'hour': 8,
            'minute': 0, 'longitude': 114.17, 'gender': '男',
            'hour_confidence': 'high'
        },
        'bazi_data2': {
            'year': 1990, 'month': 10, 'day': 10, 'hour': 10,
            'minute': 0, 'longitude': 114.17, 'gender': '女',
            'hour_confidence': 'high'
        },
        'expected_score': (85, 95),
        'description': '天合地合帶貴人，師傅級極品組合'
    },
    {
        'name': '師傅級案例2 - 互為忌神',
        'bazi_data1': {
            'year': 1985, 'month': 10, 'day': 24, 'hour': 10,
            'minute': 0, 'longitude': 114.17, 'gender': '男',
            'hour_confidence': 'high'
        },
        'bazi_data2': {
            'year': 1988, 'month': 2, 'day': 15, 'hour': 14,
            'minute': 0, 'longitude': 114.17, 'gender': '女',
            'hour_confidence': 'high'
        },
        'expected_score': (55, 65),
        'description': '互為忌神，師傅會重扣分'
    },
    {
        'name': '師傅級案例3 - 日支六害',
        'bazi_data1': {
            'year': 1990, 'month': 6, 'day': 15, 'hour': 12,
            'minute': 0, 'longitude': 114.17, 'gender': '男',
            'hour_confidence': 'high'
        },
        'bazi_data2': {
            'year': 1993, 'month': 9, 'day': 9, 'hour': 9,
            'minute': 0, 'longitude': 114.17, 'gender': '女',
            'hour_confidence': 'high'
        },
        'expected_score': (50, 60),
        'description': '日支六害，師傅級會重扣15-20分'
    }
]
# ========== 1.5 師傅級測試案例結束 ==========

# ========== 1.6 測試工具函數開始 ==========
def get_test_case_by_id(test_id: int) -> Dict:
    """根據ID獲取測試案例"""
    if 1 <= test_id <= len(ADMIN_TEST_CASES):
        return ADMIN_TEST_CASES[test_id - 1]
    return None

def get_all_test_descriptions() -> List[str]:
    """獲取所有測試案例的描述"""
    return [f"{i+1}. {case['description']}" for i, case in enumerate(ADMIN_TEST_CASES)]

def get_test_count() -> Dict[str, int]:
    """獲取各類測試案例數量"""
    return {
        'admin': len(ADMIN_TEST_CASES),
        'boundary': len(BOUNDARY_TEST_CASES),
        'performance': len(PERFORMANCE_TEST_CASES),
        'consistency': len(CONSISTENCY_TEST_CASES),
        'master': len(MASTER_TEST_CASES),
        'total': len(ADMIN_TEST_CASES) + len(BOUNDARY_TEST_CASES) + 
                len(PERFORMANCE_TEST_CASES) + len(CONSISTENCY_TEST_CASES) +
                len(MASTER_TEST_CASES)
    }

def format_test_case(test_case: Dict, index: int = None) -> str:
    """格式化測試案例為可讀文本"""
    if index is not None:
        header = f"測試案例 #{index + 1}"
    else:
        header = "測試案例"
    
    text = f"""📋 {header}
====================
📝 描述: {test_case.get('description', '無描述')}
"""
    
    if 'bazi_data1' in test_case and 'bazi_data2' in test_case:
        b1 = test_case['bazi_data1']
        b2 = test_case['bazi_data2']
        
        text += f"""👥 八字A: {b1['year']}年{b1['month']}月{b1['day']}日 {b1['hour']}時 ({b1['gender']})
👥 八字B: {b2['year']}年{b2['month']}月{b2['day']}日 {b2['hour']}時 ({b2['gender']})
"""
    
    if 'expected_range' in test_case:
        exp_min, exp_max = test_case['expected_range']
        text += f"🎯 預期分數: {exp_min}-{exp_max}分\n"
    
    if 'expected_model' in test_case:
        text += f"🎭 預期模型: {test_case['expected_model']}\n"
    
    return text
# ========== 1.6 測試工具函數結束 ==========

# ========== 文件信息開始 ==========
"""
文件: test_cases.py
功能: 測試用例配置 - 包含各種測試案例，用於驗證算法一致性

引用文件: 無
被引用文件:
- admin_service.py (管理員服務)
- bot.py (主程序)

包含測試案例類型:
1. 管理員測試案例 (20組) - 用於驗證主要算法功能
2. 邊界測試案例 - 測試系統邊界條件
3. 性能測試案例 - 測試系統性能
4. 一致性測試案例 - 測試結果一致性
5. 師傅級測試案例 - 用於對比專業師傅判斷

格式說明:
所有測試案例格式已更新為兼容new_calculator.py接口:
- 包含hour_confidence參數
- 包含minute參數
- 包含longitude參數
- 使用新的八字計算接口

使用方法:
1. 導入ADMIN_TEST_CASES等常量
2. 使用get_test_case_by_id()獲取特定案例
3. 使用format_test_case()格式化顯示
"""
# ========== 文件信息結束 ==========

# ========== 目錄開始 ==========
"""
1.1 管理員測試案例 - 20組主要測試案例
1.2 邊界測試案例 - 測試系統邊界條件
1.3 性能測試案例 - 測試性能表現
1.4 一致性測試案例 - 測試結果一致性
1.5 師傅級測試案例 - 專業師傅對比案例
1.6 測試工具函數 - 輔助函數和格式化工具
"""
# ========== 目錄結束 ==========

# ========== 修正紀錄開始 ==========
"""
版本 1.0 (2026-02-01)
主要修改:
1. 完全更新測試案例格式以兼容new_calculator.py
2. 添加hour_confidence參數（默認'high'）
3. 添加minute參數（默認0）
4. 添加longitude參數（默認114.17）
5. 擴展管理員測試案例到20組
6. 添加師傅級測試案例（用於對比專業判斷）
7. 添加測試工具函數，便於管理和格式化
8. 保持原有測試案例邏輯不變，只更新格式

兼容性:
- 完全兼容new_calculator.py的所有接口
- 兼容admin_service.py的管理員測試功能
- 支持真太陽時校正和新的評分系統

測試案例說明:
1. 涵蓋各種情況：救命優先、現實保底、神煞加持、不對稱性等
2. 包含邊界條件測試：最小/最大年份、閏年、時辰邊界等
3. 包含師傅級專業判斷對比案例
4. 所有案例都有預期分數範圍和關係模型

使用方法:
1. 在admin_service.py中導入ADMIN_TEST_CASES
2. 運行全部20組測試案例
3. 對比分數是否在預期範圍內
4. 檢查關係模型是否匹配預期
"""
# ========== 修正紀錄結束 ==========