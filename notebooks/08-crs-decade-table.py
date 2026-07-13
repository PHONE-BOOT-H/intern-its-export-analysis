"""브리프 숫자의 출처: 눈검증 끝난 리뷰 CSV에서 10년 표를 만든다.
입력: data/processed/crs_multiyear_its_review.csv (판정 O/X 전부 채워진 상태)
"""
import pandas as pd

df = pd.read_csv('data/processed/crs_multiyear_its_review.csv', encoding='utf-8-sig')
assert df['판정'].isin(['O', 'X']).all(), '판정 안 끝난 행 있음'
o = df[df['판정'] == 'O'].copy()
o['donor'] = o['DonorName'].replace({'EU Institutions': 'EU', 'United States': 'US'})

print('확정 O:', len(o), '행 | 고유 사업(제목 기준):',
      o['ProjectTitle'].fillna(o['ShortDescription']).str.lower().str.strip().nunique())

pv = o.pivot_table(index='Year', columns='donor', aggfunc='size', fill_value=0)
main = [c for c in ['Korea', 'Japan', 'US', 'Spain', 'Germany', 'EU'] if c in pv.columns]
print('\n[연도 x 공여국 행수]');  print(pv[main].to_string())

print('\n[10년 합계 — 행수 / 약정 $M / 집행 $M]')
g = o.groupby('donor').agg(행수=('donor', 'size'),
                           약정M=('USD_Commitment', 'sum'),
                           집행M=('USD_Disbursement', 'sum'))
print(g.sort_values('행수', ascending=False).round(1).to_string())

tr = o['ProjectTitle'].fillna('').str.contains('Achieving Effective', case=False)
print('\n한국 초청연수(Achieving Effective ... ITS)', tr.sum(), '행 제외 시:')
print(o[~tr]['donor'].value_counts().head(5).to_string())
