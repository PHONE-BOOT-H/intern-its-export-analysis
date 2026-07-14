"""대시보드 데이터 굽기: 4개 층을 dashboard/data.js 하나로.
로직은 기존 노트북 재현(01~03 ADB, 08 CRS, 10 AidData, 11 ITS Korea).
성공 기준: 구운 숫자가 브리프 숫자와 일치(아래 assert).
"""
import json
import re

import pandas as pd

AMT = 'ADB-FINANCED AMOUNT'
KO = {'China, People\'s Republic of': '중국', 'Korea, Republic of': '한국',
      'India': '인도', 'Philippines': '필리핀', 'Japan': '일본', 'France': '프랑스',
      'Indonesia': '인도네시아', 'Pakistan': '파키스탄', 'Bangladesh': '방글라데시',
      'Viet Nam': '베트남', 'Thailand': '태국', 'Uzbekistan': '우즈베키스탄',
      'Kazakhstan': '카자흐스탄', 'Sri Lanka': '스리랑카', 'Malaysia': '말레이시아',
      'Singapore': '싱가포르', 'Australia': '호주', 'United States': '미국',
      'Turkey': '튀르키예', 'Azerbaijan': '아제르바이잔', 'Georgia': '조지아',
      'Italy': '이탈리아', 'Spain': '스페인', 'Germany': '독일', 'Nepal': '네팔',
      'United Kingdom': '영국', 'Turkiye': '튀르키예'}
ko = lambda n: KO.get(str(n).strip(), str(n).strip())

# ---- ADB (01~03 재현) ----
df = pd.read_excel('data/raw/adb_procurement_by_nationality.xlsx',
                   sheet_name='By Nationality (download only)', header=1)
df.columns = [str(c).strip() for c in df.columns]
df[AMT] = pd.to_numeric(df[AMT], errors='coerce')
for c in ['NATIONALITY', 'BORROWING COUNTRY']:
    df[c] = df[c].astype(str).str.strip()
tr = df[df['SECTOR'].astype(str).str.contains('transport', case=False, na=False)].copy()
tr['is_domestic'] = tr['NATIONALITY'] == tr['BORROWING COUNTRY']

def league(d, topn=10):
    g = d.groupby('NATIONALITY').agg(cnt=('NATIONALITY', 'size'),
                                     amt=(AMT, 'sum')).sort_values('amt', ascending=False)
    tot = g['amt'].sum()
    return [{'nat': ko(n), 'cnt': int(r.cnt), 'amt_m': round(r.amt / 1e6, 1),
             'share': round(r.amt / tot * 100, 1)} for n, r in g.head(topn).iterrows()]

dom_pct = tr[tr['is_domestic']][AMT].sum() / tr[AMT].sum() * 100
xb = tr[~tr['is_domestic']]
its636 = tr[tr['SUBSECTOR'].astype(str).str.contains(
    'traffic|intelligent|signal|ITS', case=False, na=False)].copy()
works = its636['NATURE OF PROCUREMENT'].astype(str).str.contains('works|civil', case=False)
kw = (its636['CONTRACT DESCRIPTION'].astype(str) + ' ' + its636['PROJECT TITLE'].astype(str)).str.contains(
    'intelligent|ITS|C-ITS|V2X|smart traffic|ATMS|signal|tolling|electronic toll', case=False, na=False)
kw24 = its636[kw].groupby('NATURE OF PROCUREMENT').size()

adb = {
    'period': '2016.1 ~ 2026.5', 'rows': len(tr),
    'domestic_pct': round(dom_pct, 1),
    'league_all': league(tr), 'league_export': league(xb),
    'its636': {'n': len(its636),
               'works_amt_pct': round(its636[works][AMT].sum() / its636[AMT].sum() * 100, 0),
               'nature': [{'k': str(n)[:20], 'cnt': int(c), 'amt_m': round(a / 1e6, 1)}
                          for n, c, a in zip(its636.groupby('NATURE OF PROCUREMENT').size().index,
                                             its636.groupby('NATURE OF PROCUREMENT').size(),
                                             its636.groupby('NATURE OF PROCUREMENT')[AMT].sum())]},
    'kw24': {'n': int(kw.sum()), 'nature': {str(k): int(v) for k, v in kw24.items()}},
}
kx = [r for r in adb['league_export'] if r['nat'] == '한국'][0]
assert abs(adb['domestic_pct'] - 59.6) < 0.5 and abs(kx['share'] - 18.2) < 0.5
assert adb['its636']['n'] == 636 and adb['kw24']['n'] == 24

# ---- CRS 10년 (08 재현) ----
crs = pd.read_csv('data/processed/crs_multiyear_its_review.csv', encoding='utf-8-sig')
o = crs[crs['판정'] == 'O'].copy()
NM = {'Korea': '한국', 'Japan': '일본', 'United States': '미국', 'Spain': '스페인',
      'Germany': '독일', 'EU Institutions': 'EU', 'United Kingdom': '영국'}
o['donor'] = o['DonorName'].map(NM).fillna(o['DonorName'])
main = ['한국', '일본', '미국', '스페인', '독일']
pv = o[o['donor'].isin(main)].pivot_table(index='Year', columns='donor',
                                          aggfunc='size', fill_value=0)
tot = o.groupby('donor').agg(rows=('donor', 'size'), commit=('USD_Commitment', 'sum'),
                             disb=('USD_Disbursement', 'sum')).sort_values('rows', ascending=False)
training = o['ProjectTitle'].fillna('').str.contains('Achieving Effective', case=False)
crs_data = {
    'years': [int(y) for y in pv.index],
    'donors': main,
    'pivot': {d: [int(v) for v in pv[d]] for d in main},
    'totals': [{'donor': d, 'rows': int(r.rows), 'commit_m': round(r.commit, 1),
                'disb_m': round(r.disb, 1)} for d, r in tot.iterrows()],
    'total_rows': int(len(o)),
    'unique': int(o['ProjectTitle'].fillna(o['ShortDescription']).str.lower().str.strip().nunique()),
    'korea_no_training': int((~training & (o['donor'] == '한국')).sum()),
}
assert crs_data['total_rows'] == 164 and crs_data['pivot']['한국'] == [3, 4, 4, 3, 8, 12, 10, 7, 9, 8]

# ---- 중국 (10 재현 + 깔때기) ----
aid = pd.read_csv('data/processed/aiddata_its_review.csv', encoding='utf-8-sig')
ao = aid[aid['판정'] == 'O']
agg_yes = ao['Recommended For Aggregates'].astype(str).str.strip() == 'Yes'
REC_KO = {'Moldova': '몰도바', 'Liberia': '라이베리아', 'Nigeria': '나이지리아',
          'Belarus': '벨라루스', 'Ghana': '가나'}
TITLE_KO = {66233: '키시나우 주요 교차로 도로감시 시스템 설치 (EUR 3M 무상원조)',
            66237: '키시나우 41개 교차로 영상감시·교통관제센터 구축 (RMB 30M 무상원조)',
            1799: '몬로비아 태양광 신호등 19기 설치 (RMB 50M 무상원조 연계)',
            52632: '아부자 태양광 교통신호 시스템 2단계 (RMB 1.2M 무상원조)',
            49039: '민스크 지능형교통시스템 차관 $102M — 약속 단계에서 중단'}
proj = lambda r: {'year': int(r['Commitment Year']),
                  'rec': REC_KO.get(str(r['Recipient']), str(r['Recipient'])),
                  'amt_m': None if pd.isna(r['Amount (Constant USD 2021)'])
                  else round(r['Amount (Constant USD 2021)'] / 1e6, 1),
                  'title': TITLE_KO.get(int(r['AidData Record ID']), str(r['Title']))}
china = {
    'funnel': [{'label': '중국이 지원한 개도국 교통사업 (2000~2021)', 'n': 1665},
               {'label': '검색어와 전수 확인으로 추린 후보', 'n': int(len(aid))},
               {'label': '수작업·교차 검증을 통과한 ITS 사업', 'n': int(len(ao))},
               {'label': '실제 집행된 ITS 사업 — 약속 단계에서 멈춘 1건 제외', 'n': int(agg_yes.sum())}],
    'projects': [proj(r) for _, r in ao[agg_yes].sort_values('Commitment Year').iterrows()],
    'pledge': [proj(r) for _, r in ao[~agg_yes].iterrows()],
    'impl_amt_m': round(ao.loc[agg_yes, 'Amount (Constant USD 2021)'].sum() / 1e6, 1),
}
assert china['funnel'][3]['n'] == 4 and abs(china['impl_amt_m'] - 12.6) < 0.1

# ---- 한국 실측 (11 캐시) ----
load = lambda ep: json.load(open(f'data/raw/itskorea_dashboard/{ep}.json', encoding='utf-8'))
ann = sorted(load('annual'), key=lambda r: r['year'])
nation = sorted(load('nation'), key=lambda r: -r['totalAmtUsd'])[:10]
service = sorted(load('service'), key=lambda r: -r['totalAmtUsd'])
biz = load('biz-kind')
korea = {
    'annual': [{'y': r['year'], 'amt_m': round(r['totalAmtUsd'] / 1e6, 1), 'cnt': r['bizCnt']} for r in ann],
    'nation': [{'k': r['ntnl'], 'amt_m': round(r['totalAmtUsd'] / 1e6, 1), 'cnt': r['bizCnt']} for r in nation],
    'service': [{'k': r['serviceTy'].strip(), 'amt_m': round(r['totalAmtUsd'] / 1e6, 1), 'cnt': r['bizCnt']} for r in service],
    'bizkind': [{'k': r['bizKind'].strip(), 'amt_m': round(r['totalAmtUsd'] / 1e6, 1), 'pct': r['rate']} for r in biz],
    'total_amt_b': round(sum(r['totalAmtUsd'] for r in ann) / 1e9, 2),
    'total_cnt': sum(r['bizCnt'] for r in ann),
    'fetched': '2026-07-14',
}
assert korea['total_cnt'] == 687 and korea['total_amt_b'] == 1.98

data = {'adb': adb, 'crs': crs_data, 'china': china, 'korea': korea}
with open('dashboard/data.js', 'w', encoding='utf-8') as f:
    f.write('const DATA = ' + json.dumps(data, ensure_ascii=False) + ';\n')
print('dashboard/data.js 저장. 검증 전부 통과.')
print('ADB 안방', adb['domestic_pct'], '| 수출리그', adb['league_export'][:2],
      '| CRS', crs_data['total_rows'], '행 | 중국 이행', china['funnel'][3]['n'],
      '| 한국', korea['total_cnt'], '건')
