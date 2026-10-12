-- 재현 유형: 개인정보 - 미승인 이메일 조회
-- 기대 탐지: [개인정보 컬럼] EMAIL
-- 기대 줄: 8
-- 비고: 실제 운영 결함이 아니라 과거 결함 유형을 재현한 회귀 시험 사례
CREATE OR REPLACE PROCEDURE SP_REG_EMAIL (P_DEPT_CD IN VARCHAR2, O_CUR OUT SYS_REFCURSOR) AS
BEGIN
    OPEN O_CUR FOR
    SELECT STD_NO, STD_NM, EMAIL
      FROM TB_STD_MST
     WHERE DEPT_CD = P_DEPT_CD;
END;
/
