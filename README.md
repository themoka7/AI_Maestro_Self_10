# 8회차 · AI Agent 도입 가능성 검토 및 확장 토의

## 주제

**WebSquare 화면·SP 개발 에이전트 실업무 도입 검토** (7회차 시제품 확장)

7회차에 만든 "WebSquare 화면 + 저장 프로시저(SP) 생성 에이전트" 시제품을 정보화본부의 학사·행정 시스템 개발 업무에 실제로 들일 수 있는지 검토한다. 아래 네 가지 질문에 근거를 갖고 답하는 것이 목표다.

| # | 질문 | 문서 |
|---|------|------|
| 1 | **효과**: 실제로 빨라지는가? 결함은 늘지 않는가? | [docs/01-효과검증.md](docs/01-효과검증.md) |
| 2 | **보안·제도**: 소스와 DB 스키마를 밖으로 보내도 되는가? | [docs/02-보안-제도.md](docs/02-보안-제도.md) |
| 3 | **품질 게이트**: 생성된 코드를 무엇으로 걸러 낼 것인가? | [docs/03-품질게이트.md](docs/03-품질게이트.md) |
| 4 | **확장 로드맵**: 개인 도구에서 표준 프로세스까지 어떻게 넓힐 것인가? | [docs/04-확장로드맵.md](docs/04-확장로드맵.md) |
| - | 토의 안건과 결론 기록 | [docs/05-토의안건.md](docs/05-토의안건.md) |

## 핵심 결과 (7회차 시제품 제작 실측)

| 예상 | 실제 | 방법 |
|------|------|------|
| 약 1주 | **반나절** | 개인 코딩 베이스(정규식 처리 등)를 스킬로 만들어 생성에 활용, 이해가 안 되는 DB 설계·SP는 설명 스킬로 풀어서 이해한 뒤 반영 |

예상치 대비 비교라서, 정식 비교 실험으로 확인할 예정이다. 자세한 내용은 [01 문서 1.2](docs/01-효과검증.md).

## 저장소 구성

```
docs/            검토 문서 (위 표)
gates/es5/       WebSquare XML·JS의 ES5 문법 검사기 (Node, acorn)
gates/pii/       SP의 개인정보 컬럼 접근 검사기 (Python, 표준 라이브러리만 사용)
samples/         검사기 동작 확인용 예제 (통과·실패 각 1건)
```

## 품질 게이트 실행

```bash
# ES5 검사: WebSquare XML 안의 <script> 블록과 .js 파일을 ES5로 파싱
cd gates/es5 && npm install && cd ../..
node gates/es5/check-es5.js samples/pass   # 통과
node gates/es5/check-es5.js samples/fail   # const, includes() 위반 2건

# 개인정보 컬럼 검사: 승인 주석 없이 민감 컬럼을 조회하는 SP를 찾아냄
python3 gates/pii/check_pii.py --columns gates/pii/pii_columns.txt samples/pass   # 통과 (승인 주석 있는 SP 포함)
python3 gates/pii/check_pii.py --columns gates/pii/pii_columns.txt samples/fail   # SELECT *, 미승인 MOBILE_NO·EMAIL 3건
```

두 검사기 모두 위반이 있으면 종료 코드 1을 반환하므로, pre-commit 훅이나 CI 단계에 그대로 걸 수 있다.

## 진행 상태

- [x] 검토 틀과 품질 게이트 시제품 작성
- [x] 시제품 제작 실측 기록 (예상 1주 → 실제 반나절)
- [ ] 효과 검증 실험 실시 (조회형 화면 1본, 기존 방식과 에이전트 방식 비교)
- [ ] 보안 담당 부서 의견 수렴
- [ ] 토의 결과 반영, 다음 단계 결정
