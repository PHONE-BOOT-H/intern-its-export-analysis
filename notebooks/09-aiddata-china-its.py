"""중국 층: AidData GCDF 3.0에서 ITS 성격 사업 추출.
CRS와 같은 키워드·제외 규칙(07과 동일)을 교통 부문(Sector Code 210)에 적용.
후보는 리뷰 CSV로 — 최종 판정은 눈으로.

판정 후 감사(2026-07-14): 후보 7건을 LLM 3심 교차판정, 전체 1,665건을
정규식 밖 어휘(surveillance·monitoring·traffic lights 등)로 전수 스윕.
거짓음성 4건 발견(몰도바 2, 라이베리아, 민스크 air_sea 오폭) — 스윕 발견분은
리뷰 CSV에 '비고' 표시로 append됨. 최종표 재현은 notebooks/10.
"""
import io
import os
import re
import zipfile

import pandas as pd

XLSX = ('AidDatas_Global_Chinese_Development_Finance_Dataset_Version_3_0/'
        'AidDatasGlobalChineseDevelopmentFinanceDataset_v3.0.xlsx')
CACHE = 'data/processed/gcdf3_transport.parquet'

COLS = ['AidData Record ID', 'Recipient', 'Commitment Year', 'Status', 'Flow Class',
        'Amount (Constant USD 2021)', 'Title', 'Description', 'Sector Code',
        'Recommended For Aggregates']
if os.path.exists(CACHE):
    tr = pd.read_parquet(CACHE)
else:
    z = zipfile.ZipFile('data/raw/aiddata_gcdf_v3.zip')
    df = pd.read_excel(io.BytesIO(z.read(XLSX)), sheet_name='GCDF_3.0')
    tr = df.loc[pd.to_numeric(df['Sector Code'], errors='coerce') == 210, COLS].copy()
    tr.to_parquet(CACHE)
print('GCDF 교통(210):', len(tr), '행 | 약정연도',
      int(tr['Commitment Year'].min()), '~', int(tr['Commitment Year'].max()))

# 07과 동일 규칙
ITS_RE = re.compile(
    r'\bintelligent transport|\bITS\b|\bC-ITS\b|\bV2X\b|\btraffic management|'
    r'\btraffic signal|\btraffic control|\bATMS\b|\belectronic toll|\btolling\b|'
    r'\bsmart mobility|\bsmart traffic|\bvariable message|\bvehicle detection|'
    r'\bincident management|\bATC\b|\badaptive signal', re.IGNORECASE)
NON_ITS_RE = re.compile(ITS_RE.pattern.replace(r'\bITS\b|', ''), re.IGNORECASE)
UPPER_ITS = re.compile(r'\bITS\b')
AIR_SEA_RE = re.compile(
    r'\bair.traffic|\baviation\b|\bairport|\bairspace|\bmaritime\b|\bmarine\b|'
    r'\bvessel traffic|\bport authority|\bharbou?r\b|\brailway signal', re.IGNORECASE)

blob = tr[['Title', 'Description']].fillna('').agg(' '.join, axis=1)
hit = tr[blob.str.contains(ITS_RE, na=False)].copy()
hb = blob[hit.index]
possessive = ~hb.str.contains(NON_ITS_RE) & ~hb.str.contains(UPPER_ITS)
air_sea = hb.str.contains(AIR_SEA_RE) & ~hit['Title'].fillna('').str.contains(UPPER_ITS)
hit['auto_drop'] = ''
hit.loc[air_sea, 'auto_drop'] = 'air_sea'
hit.loc[possessive, 'auto_drop'] = 'possessive_its'
print('키워드', len(hit), '| 소유격 자동제거', possessive.sum(),
      '| 항공해상 자동제거', (air_sea & ~possessive).sum(),
      '| 눈검증 후보', (hit['auto_drop'] == '').sum())

out = hit.drop(columns=['Sector Code']).copy()
out.insert(0, '판정', '')
out.loc[out['auto_drop'] != '', '판정'] = 'X'
OUT = 'data/processed/aiddata_its_review.csv'
if os.path.exists(OUT):
    print('주의:', OUT, '이미 있음 — 판정 보호 위해 덮어쓰지 않음')
else:
    out.sort_values(['판정', 'Commitment Year']).to_csv(OUT, index=False, encoding='utf-8-sig')
    print('저장:', OUT, len(out), '행')
