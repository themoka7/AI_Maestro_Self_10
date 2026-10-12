# 게이트 검토 로그
- 대상: samples/loop-demo/
- 시작: 2026-10-12 11:13:20

## 1회차
### 검사 결과
ES5: 위반 2건 / 개인정보: 위반 3건

```
$ node gates/es5/check-es5.js samples/loop-demo/
samples/loop-demo/STD_CHG_LIST.xml:11  [ES5 문법] The keyword 'const' is reserved
    const param = { year: ica_year.getValue(), term: sbx_term.getValue() };
samples/loop-demo/STD_CHG_LIST.xml:13  [미지원 API] Array/String.prototype.includes
    if (depts.includes(sbx_dept.getValue())) {

검사 파일 1개, 위반 2건
(종료 코드 1)

$ python3 gates/pii/check_pii.py --columns gates/pii/pii_columns.txt samples/loop-demo/
samples/loop-demo/SP_STD_ALL.sql:3  [SELECT *] 컬럼을 명시해야 함
    OPEN O_CUR FOR SELECT * FROM TB_STD_MST;
samples/loop-demo/SP_STD_CHG_LIST.sql:9  [개인정보 컬럼] EMAIL
    SELECT A.STD_NO, B.STD_NM, B.MOBILE_NO, B.EMAIL, A.CHG_DIV_CD, A.CHG_DT
samples/loop-demo/SP_STD_CHG_LIST.sql:9  [개인정보 컬럼] MOBILE_NO
    SELECT A.STD_NO, B.STD_NM, B.MOBILE_NO, B.EMAIL, A.CHG_DIV_CD, A.CHG_DT

검사 파일 2개, 위반 3건
(종료 코드 1)
```

### 조치
| 파일:줄 | 위반 | 분류 | 조치 |
|---|---|---|---|
| samples/loop-demo/STD_CHG_LIST.xml:11 | [ES5 문법] const | 자동 수정 가능 | `const` → `var` |
| samples/loop-demo/STD_CHG_LIST.xml:13 | [미지원 API] includes | 자동 수정 가능 | `includes(x)` → `indexOf(x) !== -1` |
| samples/loop-demo/SP_STD_ALL.sql:3 | [SELECT *] | 사람 확인 필요 | 수정하지 않음 (최종 결과 참조) |
| samples/loop-demo/SP_STD_CHG_LIST.sql:9 | [개인정보 컬럼] EMAIL | 사람 확인 필요 | 수정하지 않음 (최종 결과 참조) |
| samples/loop-demo/SP_STD_CHG_LIST.sql:9 | [개인정보 컬럼] MOBILE_NO | 사람 확인 필요 | 수정하지 않음 (최종 결과 참조) |

### 수정 내용
samples/loop-demo/STD_CHG_LIST.xml:11
```
- 전:     const param = { year: ica_year.getValue(), term: sbx_term.getValue() };
+ 후:     var param = { year: ica_year.getValue(), term: sbx_term.getValue() };
```
samples/loop-demo/STD_CHG_LIST.xml:13
```
- 전:     if (depts.includes(sbx_dept.getValue())) {
+ 후:     if (depts.indexOf(sbx_dept.getValue()) !== -1) {
```

## 2회차
### 검사 결과
ES5: 위반 0건 / 개인정보: 위반 3건

```
$ node gates/es5/check-es5.js samples/loop-demo/

검사 파일 1개, 위반 0건
(종료 코드 0)

$ python3 gates/pii/check_pii.py --columns gates/pii/pii_columns.txt samples/loop-demo/
samples/loop-demo/SP_STD_ALL.sql:3  [SELECT *] 컬럼을 명시해야 함
    OPEN O_CUR FOR SELECT * FROM TB_STD_MST;
samples/loop-demo/SP_STD_CHG_LIST.sql:9  [개인정보 컬럼] EMAIL
    SELECT A.STD_NO, B.STD_NM, B.MOBILE_NO, B.EMAIL, A.CHG_DIV_CD, A.CHG_DT
samples/loop-demo/SP_STD_CHG_LIST.sql:9  [개인정보 컬럼] MOBILE_NO
    SELECT A.STD_NO, B.STD_NM, B.MOBILE_NO, B.EMAIL, A.CHG_DIV_CD, A.CHG_DT

검사 파일 2개, 위반 3건
(종료 코드 1)
```

### 조치
| 파일:줄 | 위반 | 분류 | 조치 |
|---|---|---|---|
| samples/loop-demo/SP_STD_ALL.sql:3 | [SELECT *] | 사람 확인 필요 | 수정하지 않음 |
| samples/loop-demo/SP_STD_CHG_LIST.sql:9 | [개인정보 컬럼] EMAIL | 사람 확인 필요 | 수정하지 않음 |
| samples/loop-demo/SP_STD_CHG_LIST.sql:9 | [개인정보 컬럼] MOBILE_NO | 사람 확인 필요 | 수정하지 않음 |

### 수정 내용
없음. 남은 위반이 모두 "사람 확인 필요"이므로 여기서 멈춘다 (3회를 채우지 않음).

## 최종 결과
- 상태: 사람 확인 대기
- 왕복 횟수: 2
- 사람 확인 필요 항목:

| 파일:줄 | 위반 | 수정안 (가) | 수정안 (나) |
|---|---|---|---|
| samples/loop-demo/SP_STD_CHG_LIST.sql:9 | [개인정보 컬럼] EMAIL | 명세에 없는 컬럼이면 SELECT에서 `B.EMAIL` 제거 | 업무상 필요하면 담당자 승인 후 `-- PII-APPROVED: <승인 근거> : EMAIL` 추가 |
| samples/loop-demo/SP_STD_CHG_LIST.sql:9 | [개인정보 컬럼] MOBILE_NO | 명세에 없는 컬럼이면 SELECT에서 `B.MOBILE_NO` 제거 | 업무상 필요하면 담당자 승인 후 `-- PII-APPROVED: <승인 근거> : MOBILE_NO` 추가 |
| samples/loop-demo/SP_STD_ALL.sql:3 | [SELECT *] | TB_STD_MST의 실제 컬럼 목록(스키마)과 이 SP의 명세(화면에 필요한 컬럼)를 받아 필요한 컬럼만 명시 | 해당 없음. 컬럼 이름을 지어내지 않음. 필요 정보: TB_STD_MST 스키마, SP_STD_ALL 명세/호출 화면 |

참고: SP_STD_CHG_LIST.sql 1행 주석에 "명세에 없는 컬럼 포함"이라고 되어 있으나, 어느 컬럼이 명세 밖인지는 명세 원문으로 담당자가 확인해야 한다.
