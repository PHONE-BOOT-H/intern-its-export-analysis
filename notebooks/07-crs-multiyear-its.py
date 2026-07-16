"""CRS 2014~2023 ITS 추출 — "한국 최다"가 2022 약정 뭉침 착시인지 가른다.

2022 눈검증에서 확정된 규칙을 자동 적용:
  1) 키워드 매칭 (04와 동일 정규식)
  2) 소유격 its 오탐 제거 (ITS 토큰만 걸렸는데 대문자 ITS가 없는 행)
  3) 항공·해상 명백 오탐 제거 (air traffic, aviation, airport, maritime 등)
남는 후보만 리뷰 CSV로. 2022 판정(O/X)은 공여국+제목이 같으면 다른 연도에도 전파.
"""
import re
import pandas as pd

YEARS = range(2014, 2024)
TXT = ['ProjectTitle', 'ShortDescription', 'LongDescription', 'Keywords']
KEEP = TXT + ['Year', 'DonorName', 'RecipientName', 'USD_Commitment', 'USD_Disbursement']

# 주의: 이 정규식은 2022~10년 눈검증 당시 버전으로 동결한다 (air-traffic 하이픈·marine
# 누락 구멍은 리뷰 CSV에서 수동 보정됨). src/its_filter의 최신판으로 갈면 자동필터
# 숫자(소유격 564/항공해상 191)가 바뀌어 문서·판정 파일 재현이 깨진다. 새 층은 src를 쓸 것.
ITS_RE = re.compile(
    r'\bintelligent transport|\bITS\b|\bC-ITS\b|\bV2X\b|\btraffic management|'
    r'\btraffic signal|\btraffic control|\bATMS\b|\belectronic toll|\btolling\b|'
    r'\bsmart mobility|\bsmart traffic|\bvariable message|\bvehicle detection|'
    r'\bincident management|\bATC\b|\badaptive signal', re.IGNORECASE)
UPPER_ITS = re.compile(r'\bITS\b')  # case-sensitive
# ITS 외 키워드가 하나라도 있는지 (소유격 오탐 판별용)
NON_ITS_RE = re.compile(
    r'\bintelligent transport|\bC-ITS\b|\bV2X\b|\btraffic management|'
    r'\btraffic signal|\btraffic control|\bATMS\b|\belectronic toll|\btolling\b|'
    r'\bsmart mobility|\bsmart traffic|\bvariable message|\bvehicle detection|'
    r'\bincident management|\bATC\b|\badaptive signal', re.IGNORECASE)
AIR_SEA_RE = re.compile(
    r'\bair traffic|\baviation\b|\bairport|\bairspace|\bmaritime\b|'
    r'\bvessel traffic|\bport authority|\bharbou?r\b|\brailway signal', re.IGNORECASE)

frames = []
for y in YEARS:
    df = pd.read_parquet(f'data/raw/crs_{y}.parquet', columns=KEEP + ['SectorCode', 'Bi_Multi'])
    df['SectorCode'] = pd.to_numeric(df['SectorCode'], errors='coerce')
    tr = df[(df['SectorCode'] == 210)
            & df['Bi_Multi'].astype(str).str.strip().isin(['1', '1.0'])]
    blob = tr[TXT].fillna('').agg(' '.join, axis=1)
    hit = tr[blob.str.contains(ITS_RE, na=False)].copy()
    hit['blob'] = blob[hit.index]
    frames.append(hit[KEEP + ['blob']])
    print(y, '교통양자', len(tr), '-> 키워드', len(hit))

cand = pd.concat(frames, ignore_index=True)

# 자동 제거 1: 소유격 its (다른 키워드 없음 + 대문자 ITS 없음)
possessive = ~cand['blob'].str.contains(NON_ITS_RE) & ~cand['blob'].str.contains(UPPER_ITS)
# 자동 제거 2: 항공·해상 (단, 진짜 ITS 키워드가 제목에 있으면 살림 — 눈으로 보게)
air_sea = cand['blob'].str.contains(AIR_SEA_RE) & ~cand['ProjectTitle'].fillna('').str.contains(UPPER_ITS)
cand['auto_drop'] = ''
cand.loc[air_sea, 'auto_drop'] = 'air_sea'
cand.loc[possessive, 'auto_drop'] = 'possessive_its'
print('\n키워드 총', len(cand), '| 소유격 자동제거', possessive.sum(),
      '| 항공해상 자동제거', (air_sea & ~possessive).sum())

# 2022 판정 전파 (공여국+제목 소문자 키)
rev = pd.read_csv('data/processed/crs2022_its_review_한글.csv', encoding='utf-8-sig')
rev = rev[rev['판정'].isin(['O', 'X'])]
key = lambda d: d['DonorName'].astype(str).str.strip() + '|' + \
    d['ProjectTitle'].fillna('').astype(str).str.lower().str.strip()
verdict_map = dict(zip(key(rev), rev['판정']))
cand['판정'] = key(cand).map(verdict_map).fillna('')
cand.loc[cand['auto_drop'] != '', '판정'] = cand.loc[cand['auto_drop'] != '', '판정'].replace('', 'X')

todo = cand[cand['판정'] == '']
print('판정 전파:', (cand['판정'] != '').sum(), '| 남은 눈검증 후보:', len(todo))
print('\n[남은 후보 연도별]');  print(todo['Year'].value_counts().sort_index().to_string())
print('\n[남은 후보 공여국별 상위]');  print(todo['DonorName'].value_counts().head(12).to_string())

import os
OUT = 'data/processed/crs_multiyear_its_review.csv'
if os.path.exists(OUT):
    print('\n주의:', OUT, '이미 있음 — 눈검증 판정 보호 위해 덮어쓰지 않음')
else:
    out = cand.drop(columns=['blob'])
    out = out.sort_values(['판정', 'Year']).reset_index(drop=True)
    out.to_csv(OUT, index=False, encoding='utf-8-sig')
    print('\n저장:', OUT, len(out), '행')

# 미리보기: 확정 O만으로 연도x공여국 (판정 전파분 — 최종 아님)
o = cand[cand['판정'] == 'O']
if len(o):
    print('\n[미리보기 — 전파된 O만, 최종 아님] 연도 x 주요 공여국 건수')
    top = o['DonorName'].value_counts().head(6).index
    print(o[o['DonorName'].isin(top)].pivot_table(
        index='Year', columns='DonorName', aggfunc='size', fill_value=0).to_string())
