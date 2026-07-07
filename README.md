# 개도국 교통·ITS 수출 경쟁 지형 분석

공개 데이터로 "개도국 교통·ITS 사업을 어느 나라가 따가나, 한국은 어디 있나"를 분석한다.

## 무엇을, 왜

MDB(ADB·World Bank)는 개도국 교통 계약의 낙찰 데이터를 공개한다. AidData는 중국의 해외 개발금융을 공개한다. 이 둘을 합치면 두 층이 보인다.

- 낙찰 층: 누가 계약을 따나 (ADB·WB)
- 재원 층: 돈이 어디로 흐르나 (중국 BRI = AidData)

ITS Korea의 해외 발주 게시판은 공고를 하나씩 나열할 뿐 이 경쟁 지형을 보여주지 않는다. 그 빈틈을 공개 데이터로 채운다.

## 핵심 발견 (1차, ADB 2016–2026)

- 개도국 교통 낙찰에서 한국은 4위(7.4%, $2.55B). 자국 업체를 빼면 중국 다음 2위.
- ITS 니치(교통관리)만 보면 한국 14위, 중국 54%.
- 단 그 니치 금액의 86%는 도로공사(works)다. ITS 기술(장비·컨설팅)만 남기면 표본이 24건. MDB는 ITS 기술을 거의 사지 않는다.
- 함의: 한국·중국의 ITS 수출 경쟁은 MDB가 아니라 양자 채널(EDCF·BRI·JICA)에서 벌어진다.

수치는 방향성이다. 근거와 한계는 [docs/its_competition_plan.html](docs/its_competition_plan.html) 참고.

## 빠른 실행

```
pip install -r requirements.txt
# 데이터는 data/raw/README.md의 출처에서 받아 data/raw/ 에 둔다
python notebooks/01-adb-transport-league.py   # 교통 낙찰 국적별 리그테이블
python notebooks/02-adb-its-works-split.py     # ITS 니치를 works/goods/consulting로 분해
```

스크립트는 레포 루트에서 실행한다.

## 구조

```
data/raw/     원본 (공개 데이터, git 미포함, 출처는 data/raw/README.md)
notebooks/    탐색·분석 스크립트
docs/         스펙, 결정, 규칙, 계획
reports/      결과물 (그림, 브리프)
```

## 한계

- 지금은 ADB 한 곳 기준. WB·양자 데이터는 붙이는 중.
- 낙찰 국적은 등록지 기준이라 원산지가 아니고, 하도급은 빠져 있다.
- ITS 니치 표본이 작아 방향성으로만 읽는다.

## 문서

- [docs/CONVENTIONS.md](docs/CONVENTIONS.md) 레포 규칙
- [docs/PROJECT_SPEC.md](docs/PROJECT_SPEC.md) 스펙
- [docs/CURRENT_STATE.md](docs/CURRENT_STATE.md) 진행 상황
- [docs/DECISION_LOG.md](docs/DECISION_LOG.md) 결정 기록
