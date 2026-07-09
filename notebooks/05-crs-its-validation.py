"""CRS ITS 115건 오탐 검증 (04의 후속).
04의 정규식은 \bITS\b에 IGNORECASE라 영어 소유격 "its"도 잡는다 — 여기가 오탐 의심 1순위.
매 건이 어떤 키워드로 잡혔는지 분해하고, "소문자 its로만 매칭"을 의심군으로 분리한다.
최종 판정(진짜 ITS냐)은 한태영이 리뷰 CSV를 눈으로 보고 내린다. 여기는 배관 + 1차 분류만."""
import re
import pandas as pd

df = pd.read_parquet('data/raw/crs_2022.parquet')
TXT = ['ProjectTitle', 'ShortDescription', 'LongDescription', 'Keywords']
blob = df[TXT].fillna('').agg(' '.join, axis=1)

df['SectorCode'] = pd.to_numeric(df['SectorCode'], errors='coerce')
tr = df[df['SectorCode'] == 210].copy()
tr['is_bi'] = tr['Bi_Multi'].astype(str).str.strip().isin(['1', '1.0'])
trb = tr[tr['is_bi']].copy()
trb_blob = blob[trb.index]

# 04와 동일한 패턴을 개별 키워드로 쪼갬 (합치면 04 정규식과 동치)
PATTERNS = {
    'intelligent transport': r'\bintelligent transport',
    'ITS(대소문자무시)': r'\bITS\b',
    'C-ITS': r'\bC-ITS\b',
    'V2X': r'\bV2X\b',
    'traffic management': r'\btraffic management',
    'traffic signal': r'\btraffic signal',
    'traffic control': r'\btraffic control',
    'ATMS': r'\bATMS\b',
    'electronic toll': r'\belectronic toll',
    'tolling': r'\btolling\b',
    'smart mobility': r'\bsmart mobility',
    'smart traffic': r'\bsmart traffic',
    'variable message': r'\bvariable message',
    'vehicle detection': r'\bvehicle detection',
    'incident management': r'\bincident management',
    'ATC': r'\bATC\b',
    'adaptive signal': r'\badaptive signal',
}

hits = pd.DataFrame({k: trb_blob.str.contains(p, case=False, regex=True, na=False)
                     for k, p in PATTERNS.items()})
matched = hits.any(axis=1)
its = trb[matched].copy()
AMT = 'USD_Commitment'

# 04 결과 재현 확인 (숫자 다르면 여기서 멈추고 원인부터)
print('[재현 확인] 매칭 %d건 / $%.0fM  (04에서 115건/$657M)' % (len(its), its[AMT].sum()))
assert len(its) == 115, '04와 건수 불일치 — 로직 확인 필요'

# 오탐 의심: 매칭이 'ITS(대소문자무시)' 하나뿐 + 대문자 ITS는 실제로 없음(= 소유격 its)
h = hits[matched]
only_its_token = h['ITS(대소문자무시)'] & (h.drop(columns=['ITS(대소문자무시)']).sum(axis=1) == 0)
upper_its = trb_blob[matched].str.contains(r'\bITS\b', regex=True, na=False)  # case-sensitive
suspect = only_its_token & ~upper_its

print('\n[분해]')
print('  진짜 키워드(신호·관제·톨링 등)로 매칭: %d건 / $%.0fM'
      % ((~only_its_token).sum(), its[AMT][~only_its_token].sum()))
print('  ITS 토큰으로만 매칭: %d건' % only_its_token.sum())
print('    ├ 대문자 ITS 실재(진짜 후보): %d건 / $%.0fM'
      % ((only_its_token & upper_its).sum(), its[AMT][only_its_token & upper_its].sum()))
print('    └ 소문자 its뿐(오탐 확실시): %d건 / $%.0fM'
      % (suspect.sum(), its[AMT][suspect].sum()))

print('\n[오탐 제거 시 교정치] %d건 / $%.0fM' % ((~suspect).sum(), its[AMT][~suspect].sum()))

ko = its['DonorName'].astype(str).str.lower().str.contains('korea')
print('  한국: %d건 → 오탐 제거 후 %d건 / $%.1fM'
      % (ko.sum(), (ko & ~suspect).sum(), its[AMT][ko & ~suspect].sum()))

# 전 건 리뷰 CSV (한태영 눈검증용): 의심군 위로 정렬
rev = pd.DataFrame({
    'suspect_오탐확실시': suspect.map({True: 'X', False: ''}),
    'matched_keywords': h.apply(lambda r: '; '.join(k for k in PATTERNS if r[k]), axis=1),
    'DonorName': its['DonorName'],
    'RecipientName': its['RecipientName'],
    'USD_M': its[AMT].round(2),
    'ProjectTitle': its['ProjectTitle'],
    'ShortDescription': its['ShortDescription'].astype(str).str.slice(0, 200),
}).sort_values(['suspect_오탐확실시', 'USD_M'], ascending=[False, False])
out = 'data/processed/crs2022_its_review.csv'
rev.to_csv(out, index=False, encoding='utf-8-sig')
print('\n리뷰 CSV 저장:', out, '(%d행) — 한태영이 열어서 최종 판정' % len(rev))
