"""결정적 시험: 양자 원조(OECD CRS)에서 ITS가 실제로 골라지나?
ADB 낙찰에선 교통 636건 중 진짜 ITS 키워드가 24건뿐이었다(대부분 토목).
CRS 교통(210) 양자 원조에서 ITS 키워드가 몇 건 잡히고, 한국·일본이 나오나 확인한다.
나오면 프로젝트가 산다(양자에 ITS가 있다). 안 나오면 전제를 튼다.

배관은 여기서. 오탐 판단(이게 진짜 ITS냐)은 한태영이 매칭 샘플을 눈으로 보고 방어한다."""
import re
import pandas as pd

df = pd.read_parquet('data/raw/crs_2022.parquet')
print('CRS 2022 전체:', len(df), '행 (전 공여국·전 부문)')

# 텍스트 4필드 합치기
TXT = ['ProjectTitle', 'ShortDescription', 'LongDescription', 'Keywords']
blob = df[TXT].fillna('').agg(' '.join, axis=1)

# 교통: SectorCode 210 (Transport & Storage)
df['SectorCode'] = pd.to_numeric(df['SectorCode'], errors='coerce')
tr = df[df['SectorCode'] == 210].copy()
tr_blob = blob[tr.index]
print('교통(sector=210):', len(tr), '행 | 양자(Bi) 비중 확인 ->', tr['Bi_Multi'].value_counts().to_dict())

# 양자만 (Bi_Multi==1 이 bilateral). 값 실제 확인 후 사용
tr['is_bi'] = tr['Bi_Multi'].astype(str).str.strip().isin(['1', '1.0'])
trb = tr[tr['is_bi']].copy()
trb_blob = tr_blob[trb.index]
print('교통 양자만:', len(trb), '행')

# ITS 키워드 (짧은 토큰은 단어경계로 오탐 방지)
# 2022 타당성 탐색 당시 버전으로 동결 — 브리프의 "키워드 115건" 재현용. 새 층은 src/its_filter를 쓸 것.
ITS_RE = re.compile(
    r'\bintelligent transport|\bITS\b|\bC-ITS\b|\bV2X\b|\btraffic management|'
    r'\btraffic signal|\btraffic control|\bATMS\b|\belectronic toll|\btolling\b|'
    r'\bsmart mobility|\bsmart traffic|\bvariable message|\bvehicle detection|'
    r'\bincident management|\bATC\b|\badaptive signal', re.IGNORECASE)

hit = trb_blob.str.contains(ITS_RE, na=False)
its = trb[hit].copy()
its_blob = trb_blob[hit]
AMT = 'USD_Commitment'  # CRS 금액 단위 = USD 백만
print('\n[결정적 숫자] 교통 양자 중 ITS 키워드 매칭: %d건 / $%.0fM (2022 한 해)'
      % (len(its), its[AMT].sum()))
print('  (비교: ADB 낙찰은 교통 636건 중 진짜 ITS 24건)')

print('\n[공여국별 ITS 건수·금액]')
g = its.groupby('DonorName').agg(건수=('DonorName', 'size'),
                                 금액M=(AMT, 'sum')).sort_values('금액M', ascending=False)
for don, r in g.head(15).iterrows():
    n = str(don).lower()
    mk = ' <한국' if 'korea' in n else (' <일본' if 'japan' in n else (' <중국' if 'china' in n else ''))
    print('  %-34s %4d건  $%9.1fM%s' % (str(don)[:32], int(r.건수), r.금액M, mk))

print('\n[매칭된 제목 샘플 — 오탐 눈으로 확인용, 한국·일본 우선]')
for lab, key in [('한국', 'korea'), ('일본', 'japan')]:
    sub = its[its['DonorName'].astype(str).str.lower().str.contains(key)]
    print('  --- %s (%d건) ---' % (lab, len(sub)))
    for idx in sub.index[:8]:
        title = str(df.loc[idx, 'ProjectTitle'])[:90]
        amt = df.loc[idx, AMT]
        print('     $%7.1fM  %s' % (amt, title))

print('\n[기타 주요 공여국 샘플 5건]')
other = its[~its['DonorName'].astype(str).str.lower().str.contains('korea|japan')]
for idx in other.sort_values(AMT, ascending=False).index[:5]:
    print('     %-22s $%7.1fM  %s' % (str(df.loc[idx, 'DonorName'])[:20], df.loc[idx, AMT],
                                      str(df.loc[idx, 'ProjectTitle'])[:70]))
