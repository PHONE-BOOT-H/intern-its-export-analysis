# Day 00 — SORT 구조 지도

> 목적: 대상 코드(`abewley/sort`)를 재현하기 전에 "지도"부터. 어디에 뭐가 있고, 데이터가 어떻게 흐르는지.
> 원칙: 이 문서는 **큰 그림만**. 알고리즘 속(왜 칼만필터가 이렇게 생겼나 등)은 내가 직접 파서 아래 "내가 답할 질문"에 채운다.

대상: `reference/sort/sort.py` (330줄, 단일 파일)
출처: https://github.com/abewley/sort — Bewley et al., "Simple Online and Realtime Tracking", ICIP 2016
라이센스: GPL-3.0 (원본은 레포에 안 올림. 재현은 백지에서.)

---

## 한 문장

**매 프레임 "탐지된 박스들"이 들어오면, 이전 프레임의 물체들과 짝지어 같은 물체에 같은 ID를 붙여 내보내는 실시간 다중객체 추적기.**
탐지(YOLO 등)는 이 코드가 안 함 — 박스는 입력으로 받는다. SORT가 하는 건 **"추적(=ID 유지)"** 뿐.

---

## 데이터 흐름 (한 그림)

```
매 프레임:
  탐지 박스들 dets [[x1,y1,x2,y2,score], ...]
        │
        ▼
  Sort.update(dets)                          ← 심장부 (line 210)
        │
        ├─ 1) 기존 트래커들이 이번 프레임 위치를 "예측"  (KalmanBoxTracker.predict)
        ├─ 2) 예측 박스 vs 탐지 박스를 "짝짓기"          (associate_detections_to_trackers)
        │        - IoU로 겹침 계산 → 헝가리안으로 최적 매칭
        ├─ 3) 짝지어진 트래커는 탐지로 "보정"            (KalmanBoxTracker.update)
        ├─ 4) 안 짝지어진 탐지 → 새 트래커 생성
        └─ 5) 오래 안 보인 트래커 → 삭제
        │
        ▼
  [[x1,y1,x2,y2, ID], ...]  ← 같은 물체엔 같은 ID
```

---

## 파일 지도 (함수·클래스별 역할 + 라인)

| 위치 | 이름 | 역할 | 재현 대상? |
|---|---|---|---|
| L36 | `linear_assignment` | 비용행렬 → 최적 짝짓기 (헝가리안, lap/scipy) | ○ (핵심) |
| L47 | `iou_batch` | 박스 두 묶음 간 IoU 행렬 계산 | ○ (핵심) |
| L66 | `convert_bbox_to_z` | 박스 [x1,y1,x2,y2] → 칼만 상태 [cx,cy,넓이,비율] | ○ |
| L81 | `convert_x_to_bbox` | 칼만 상태 → 박스 (역변환) | ○ |
| L94 | `KalmanBoxTracker` | **물체 1개의 상태**(칼만필터). predict/update/get_state | ○ (핵심) |
| L154 | `associate_detections_to_trackers` | 탐지↔트래커 매칭 (IoU + 헝가리안 + 임계값) | ○ (핵심) |
| L199 | `Sort` | **전체 오케스트레이터**. update()가 매 프레임 루프 | ○ (핵심) |
| L255~ | `parse_args` / `__main__` | MOT 벤치마크 데모 실행 (시각화·파일IO) | × (부수) |

재현할 알맹이는 위 표의 ○ — 대략 **150줄 안쪽**. 나머지(matplotlib 시각화, 벤치마크 파일 로딩)는 재현 대상 아님.

---

## 핵심 3덩어리 (여기가 손코딩 반복이 나오는 곳)

1. **IoU** (`iou_batch`) — 가장 쉬움. 순수 넘파이 기하. 여기부터 시작.
2. **데이터 연관** (`associate_detections_to_trackers`) — IoU 행렬 만들고, 헝가리안으로 최적 매칭, 임계값 미달 버리기. 트래킹의 "짝짓기" 두뇌.
3. **칼만 박스 트래커** (`KalmanBoxTracker`) — 가장 어려움. 등속(constant velocity) 모델로 상태 7차원 [cx,cy,s,r,vx,vy,vs] 예측·보정. 칼만필터 수학이 처음이면 여기서 시간을 쓴다.

---

## 재현 로드맵 (한 달 쪼개기 — 작은 것부터)

- **1주차**: IoU 손코딩 → 원본과 diff. 그다음 `convert_bbox_to_z`/`convert_x_to_bbox` 좌표변환.
- **2주차**: 데이터 연관(헝가리안 매칭) 손코딩. `scipy.optimize.linear_sum_assignment`가 뭘 푸는지부터.
- **3주차**: 칼만 박스 트래커. 칼만필터 개념(예측/보정) → 등속모델 F,H 행렬이 왜 저 모양인지.
- **4주차**: `Sort.update` 오케스트레이션으로 다 붙이기 → 간단한 입력으로 원본과 ID 출력 비교. README에 왜/어떻게.

각 주 안에서 매일: 조각 1개 재현 + 1커밋 (예측→기록→비교→수정).

---

## 오늘 안 판 것 / 다음에 팔 것

- 오늘(Day00): 대상 락, clone, 구조 지도까지. **아직 코드 한 줄도 직접 안 씀.**
- 다음(Day01): `iou_batch`를 **원본 안 보고** 백지에서 재구성 → 원본과 diff. (가장 작고 순수한 조각)

---

## 내가(한태영) 코드 읽으며 답할 질문

> 여기는 비워둔다. sort.py를 직접 읽고 아래에 내 언어로 채운다. 못 채우는 칸 = 내일 팔 곳.

1. `Sort.update`가 매 프레임 하는 5단계를 내 말로 한 줄씩:
   - (1)
   - (2)
   - (3)
   - (4)
   - (5)
2. 칼만 상태가 왜 [x1,y1,x2,y2]가 아니라 [cx, cy, s(넓이), r(비율)] 형태일까? (`convert_bbox_to_z`)
3. `min_hits`, `max_age`는 각각 무슨 문제를 막으려는 파라미터일까?
4. `associate_detections_to_trackers`에서 IoU가 임계값보다 낮은 매칭을 왜 다시 버릴까? (L186)
5. (심화) `predict()`의 `if((self.kf.x[6]+self.kf.x[2])<=0)` 는 무엇을 방어하나?
