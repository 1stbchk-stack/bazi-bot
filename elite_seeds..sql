-- ========================================
-- 八字配對系統 - 精英種子庫
-- 生成時間：2026-01-30 09:44:42
-- 掃描範圍：1925-2025年
-- ========================================

-- 1. 創建精英種子表
DROP TABLE IF EXISTS elite_bazi_seeds;
CREATE TABLE elite_bazi_seeds (
    seed_id SERIAL PRIMARY KEY,
    birth_timestamp TIMESTAMP NOT NULL,
    bazi_data JSONB NOT NULL,
    bazi_score_base INTEGER NOT NULL,
    primary_element VARCHAR(2) NOT NULL,
    gender_suitability CHAR(1) DEFAULT 'U' -- U:通用, M:男, F:女
);

-- 2. 創建索引
CREATE INDEX idx_birth_timestamp ON elite_bazi_seeds(birth_timestamp);
CREATE INDEX idx_bazi_score ON elite_bazi_seeds(bazi_score_base DESC);
CREATE INDEX idx_primary_element ON elite_bazi_seeds(primary_element);
CREATE INDEX idx_gender ON elite_bazi_seeds(gender_suitability);

-- 3. 開始插入數據
BEGIN;

INSERT INTO elite_bazi_seeds (birth_timestamp, bazi_data, bazi_score_base, primary_element, gender_suitability) VALUES ('1925-01-03 12:00:00', '{"year_pillar": "乙丑", "month_pillar": "乙寅", "day_pillar": "癸卯", "hour_pillar": "庚午", "elements": {"木": 26.5, "火": 21.3, "土": 14.2, "金": 22.6, "水": 15.3}, "day_branch": "卯", "month_branch": "寅", "pattern_type": "從強格", "shen_sha_names": "天乙貴人", "quality_score": 76.85, "quality_reasons": ["五行平衡度: 23.9分", "格局清晰度: 25分 (從強格)", "神煞組合: 8分"]}', 76.85, '木', 'F');
INSERT INTO elite_bazi_seeds (birth_timestamp, bazi_data, bazi_score_base, primary_element, gender_suitability) VALUES ('1925-01-05 00:00:00', '{"year_pillar": "乙丑", "month_pillar": "乙寅", "day_pillar": "己丑", "hour_pillar": "甲子", "elements": {"木": 28.3, "火": 15.9, "土": 13.0, "金": 26.2, "水": 16.5}, "day_branch": "丑", "month_branch": "寅", "pattern_type": "從強格", "shen_sha_names": "天乙貴人", "quality_score": 75.35, "quality_reasons": ["五行平衡度: 22.4分", "格
