# 개도국 교통·ITS 수출 경쟁 지형 분석

공개 데이터로 "개도국 교통·ITS 사업을 어느 나라가 따가나, 한국은 어디 있나"를 분석한다.

## 무엇을, 왜

네 개의 공개 데이터를 겹쳐 ITS 수출 경쟁 지형을 본다.

- MDB 낙찰: ADB·World Bank(IPF) — 누가 계약을 따나
- 양자 원조: OECD CRS — 어느 공여국이 ITS를 실명으로 다루나
- 중국 개발금융: AidData — BRI 교통 재원에 ITS가 있나
- 한국 실적: ITS Korea 수출통계 — 한국 자기보고(보조 층)

1차 목적은 재현 가능한 공개데이터 분석 그 자체(포트폴리오·데이터 실력)다.

## 핵심 발견 (재현됨, 숫자는 notebooks/로 추적)

- MDB 낙찰은 대부분 안방 싸움이다. ADB 59.6%, WB 58.3%(금액)가 사업국 자국 기업
  몫이다. 안방을 빼면 두 곳 다 중국이 수출 1위(ADB 50%, WB 56%), 한국은 ADB 2위·WB 12위.
- ITS를 MDB 낙찰 건명으로 찾으면 ADB엔 사실상 없고(키워드 24건 전부 컨설팅·장비,
  시스템 구축 0), WB엔 있다 — 교차판정으로 확정한 21개 프로젝트 $117M. 단 그 시장의
  71%를 중국이 가져갔고 한국은 $0.3M로 사실상 없다.
- 실명 ITS는 양자 원조(CRS)에 있다. 2014~2023 한국이 건수 최다(68행), 금액은
  일본이 최대($163M vs 한국 $37M) = 한국 소프트·다건, 일본 하드·대액.
- 중국 BRI(AidData 2000~2021): 이행된 ITS는 소액 그랜트 4건뿐, 대형 시도 2건 무산.
- 함의: 한국 ITS 수출의 승부처는 MDB 입찰이 아니라 양자 채널(EDCF·JICA·BRI)이다.

전략 브리프 [reports/brief.md](reports/brief.md), 대시보드는 GitHub Pages로 배포.

## 빠른 실행

```
pip install -r requirements.txt
# 데이터는 data/raw/README.md의 출처에서 받아 data/raw/ 에 둔다
python notebooks/03-adb-domestic-vs-export.py   # ADB 안방 vs 수출 리그
python notebooks/08-crs-decade-table.py         # CRS 10년 ITS 표
python notebooks/15-wb-its-judged.py            # WB ITS 판정 최종표
```

스크립트는 레포 루트에서 실행한다.

## 구조

```
data/raw/     원본 (공개 데이터, git 미포함, 출처는 data/raw/README.md)
notebooks/    탐색·분석 스크립트 (01~16)
docs/         스펙, 결정, 규칙, 계획
reports/      결과물 (전략 브리프)
dashboard/    정적 대시보드 (GitHub Pages)
```

## 한계

- 낙찰 국적은 등록지 기준(원산지 아님)이고, 하도급은 빠진다.
- MDB ITS는 낙찰 건명 키워드로 잡는다 — 도로사업에 부속으로 묻힌 ITS는 못 본다.
- ITS 판정은 텍스트 기반 LLM 교차판정이라 재현 가능하되 어휘를 놓칠 수 있다
  (거짓음성 리콜 편향은 각 층에서 자백).
- 소스마다 기간·정의가 다르다(WB FY2020~27, CRS 2014~2023 등). 규모를 직접
  비교하지 않고 방향으로 읽는다.
- ITS Korea 수출통계는 한국 자기보고(경쟁자·채널 구분 없음)라 보조 층으로만 쓴다.

## 문서

- [reports/brief.md](reports/brief.md) 전략 브리프 (핵심 산출물)
- [docs/CONVENTIONS.md](docs/CONVENTIONS.md) 레포 규칙
- [docs/CURRENT_STATE.md](docs/CURRENT_STATE.md) 진행 상황
- [docs/DECISION_LOG.md](docs/DECISION_LOG.md) 결정 기록
