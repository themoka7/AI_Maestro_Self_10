-- 재현 유형: 개인정보 - SELECT * 로 전체 컬럼 조회
-- 기대 탐지: [SELECT *]
-- 기대 줄: 8
-- 비고: 실제 운영 결함이 아니라 과거 결함 유형을 재현한 회귀 시험 사례
CREATE OR REPLACE PROCEDURE SP_REG_STAR (O_CUR OUT SYS_REFCURSOR) AS
BEGIN
    OPEN O_CUR FOR
    SELECT *
      FROM TB_STD_MST;
END;
/
