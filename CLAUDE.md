# CLAUDE.md — 개도국 교통·ITS 수출 경쟁 지형 분석 (인턴 한 달)

이 파일은 Claude Code가 매 세션마다 자동으로 읽는 프로젝트 컨텍스트다.

---

## 프로젝트 개요

- **무엇**: 공개 데이터로 개도국 교통·ITS 수출 경쟁 지형을 분석한다. MDB(ADB·World Bank) 낙찰로 "누가 계약을 따나", AidData로 "중국 BRI 재원이 어디로 흐르나"를 결합해 한국의 위치를 본다. 산출물은 재현 가능한 파이프라인 + 대시보드 + 짧은 전략 브리프.
- **핵심 발견(검증됨)**: ADB 교통 낙찰의 60%는 안방 싸움(등록국=사업국)이고, 그걸 빼면 한국은 순수 수출 2위(중국 다음). 근데 ITS 니치는 대부분 도로공사라 MDB엔 ITS 기술 경쟁이 안 보인다. 양자 데이터(OECD CRS)에선 ITS가 실명으로 잡힌다(2014~2023 10년 눈검증: 한국이 2018년 이후 매년 건수 최다·10년 68행, 금액은 일본이 최대 $163M vs 한국 $37M) → 진짜 ITS 수출 싸움은 양자 채널(EDCF·BRI·JICA)에 있다. 핵심 산출물은 이걸 데이터로 증명하는 전략 브리프 2~3장.
- **목적**: 1차는 포트폴리오와 데이터 실력(검증·정직한 해석·재현성). ITS Korea 국제협력부 인턴 도메인과 직결되고, 부서 브리핑용 인텔이 되는 건 보너스.
- **마감**: 인턴 한 달(약 2026-07 말). 진짜 마감선은 **매일 커밋 1개**.
- **혼자**: 나(한태영)를 위한 프로젝트.
- **데이터 원칙**: 공개 오픈데이터만 쓴다. 회사 내부·게이트 걸린 자료는 안 올린다. 원본은 `data/raw/`에 두고 수정하지 않는다.
- **글쓰기**: 모든 문서·커밋·README는 [docs/CONVENTIONS.md](docs/CONVENTIONS.md)를 따른다.

상세는:
- [docs/PROJECT_SPEC.md](docs/PROJECT_SPEC.md) — 살아있는 스펙
- [docs/CURRENT_STATE.md](docs/CURRENT_STATE.md) — 지금 어디까지 왔는지
- [docs/CONVENTIONS.md](docs/CONVENTIONS.md) — 레포 규칙(문체·구조·커밋)

---

개인 작업 스타일·운영 규칙은 `CLAUDE.local.md`(git 미추적)에 있다. 매 세션 함께 적용한다.

---

## 핵심 작업 원칙

### 1. 큰 결정 전에 멈추기

다음 상황에서는 **반드시 한태영에게 확인** 후 진행:
- 아키텍처/기술스택 결정 (새 라이브러리, 새 도구 도입)
- 데이터 스키마 변경
- 외부 서비스 연동 방식 (API, DB, 외부 도구)
- 비용 발생 결정 (API 호출 비용, 유료 도구)
- 협업자에게 영향 가는 변경

확인 형식: 자유 텍스트로 충분.

### 2. 작업 흐름

- **코드 작업**: Research → Plan → Implement → Test 4단계 권장
  - 큰 작업이면 먼저 계획 세우고 한태영 확인 후 진행
- **비-코드 작업** (조사·인터뷰·발표자료·문서): 정보 수집 → 정리 → 산출물 작성 → 리뷰
- 어떤 워크플로/도구(skill 등)가 도움될 것 같으면 Claude가 먼저 제안. 한태영이 OK 해야 사용.

### 3. 컨텍스트 관리

- 새 작업 시작 시 `/clear`로 컨텍스트 초기화 권장
- 컨텍스트 사용량 70% 이상이면 새 세션
- 세션 끝낼 때 `docs/CURRENT_STATE.md` 업데이트 (다음 세션이 이어받기 위해)

### 4. 새 세션 시작 시 읽는 순서

1. `CLAUDE.md` (이 파일)
2. **`docs/CURRENT_STATE.md`** ← 가장 중요 (어디서 이어갈지)
3. 필요시 `docs/PROJECT_SPEC.md`, `docs/CHANGELOG.md`, `docs/DECISION_LOG.md`

→ 그래서 한태영이 "ㄱㄱ"만 해도 어디부터 이어갈지 안다.

---

## 위험 명령 — 반드시 확인

자동 실행 금지, 먼저 확인:

### 파일/저장소
- `rm -rf` (폴더 통째 삭제)
- `git reset --hard` (커밋 이력 강제 변경)
- `git push --force` (다른 작업 덮어쓸 수 있음)

### 보안/개인정보
- API key, secret, `.env` 파일 수정/공개
- 개인정보 포함 데이터를 외부 서비스에 전송

### 비용 발생
- 외부 API 대량 호출
- 유료 도구/서비스 가입

### 시스템
- 권한 상승 (`sudo`, `chmod 777`)
- 외부 데이터셋 대량 다운로드 전 사이즈/라이센스 확인

---

## 사용 가능한 Skill

`.claude/skills/` 안 슬래시 커맨드. 자주 쓰는 작업을 `/이름`으로 호출.

- `/spec-interview` — `docs/PROJECT_SPEC.md` 채울 때 인터뷰
- `/method-first` — "어떻게 하는 게 좋은지" 모를 때 방법론 조사
- `/controlled-randomness` — 디자인/접근법 결정할 때 옵션 제시
- `/rpit` — Research → Plan → Implement → Test 코드 루프
- `/code-review` — 큰 변경 전 리뷰
- `/update-docs` — 기능 완료 후 문서 갱신 + 커밋
- `/retro` — 마일스톤 회고
- `/whats-next` — 다음 할 일 막혔을 때
- `/screenshot-debug` — UI 스크린샷 기반 디버깅

> 같은 작업이 반복되면 Claude가 새 skill 만들 것을 제안.

---

## 관련 문서

- [docs/PROJECT_SPEC.md](docs/PROJECT_SPEC.md) — 살아있는 스펙
- [docs/CURRENT_STATE.md](docs/CURRENT_STATE.md) — 현재 진행 상황 (세션 인수인계)
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — 시스템 구조 (코드 프로젝트일 때)
- [docs/CHANGELOG.md](docs/CHANGELOG.md) — 변경 이력
- [docs/DECISION_LOG.md](docs/DECISION_LOG.md) — 주요 결정 기록
- [docs/RETRO_LOG.md](docs/RETRO_LOG.md) — 마일스톤 회고
