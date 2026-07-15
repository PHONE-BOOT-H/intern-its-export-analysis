"""WB 교통 낙찰 분석 = ADB 01/02/03을 WB에 복제. 브리프 [구멍1] 교차확인.
입력: data/raw/wb_transport_awards.parquet (notebooks/13).

세 가지: (1) 국적 리그 + 안방(supplier=borrower) 비중, (2) 안방 제거 수출 리그,
(3) ITS 키워드 깔때기(09와 동일 정규식·필터) -> 후보 리뷰 CSV.

핵심 질문: ADB에서 본 'MDB엔 독립 ITS 시스템 발주가 없다'가 WB에서도 재현되나.
배관은 여기, 판정은 눈으로(리뷰 CSV). 각 숫자를 방어할 수 있어야.
"""
import os
import re

import pandas as pd

AMT = 'supplier_contract_amount_usd'
tr = pd.read_parquet('data/raw/wb_transport_awards.parquet')
tr[AMT] = pd.to_numeric(tr[AMT], errors='coerce')
tr['supplier_country'] = tr['supplier_country'].astype(str).str.strip()
tr['borrower_country'] = tr['borrower_country'].astype(str).str.strip()
print('WB 교통 낙찰:', len(tr), '행 | FY%d~%d | 총 $%.0fM'
      % (tr['fiscal_year'].min(), tr['fiscal_year'].max(), tr[AMT].sum() / 1e6))

# (1) 안방 vs 수출 — ADB와 같은 시험(등록국=사업국)
tr['is_domestic'] = tr['supplier_country'] == tr['borrower_country']
dom = tr[tr['is_domestic']][AMT].sum() / 1e6
xb = tr[~tr['is_domestic']][AMT].sum() / 1e6
print('  안방(supplier=borrower) $%.0fM (%.1f%%) | 수출 $%.0fM (%.1f%%)'
      % (dom, dom / (dom + xb) * 100, xb, xb / (dom + xb) * 100))


def league(df, title, n=12):
    g = df.groupby('supplier_country').agg(건수=('supplier_country', 'size'),
                                           금액M=(AMT, lambda s: s.sum() / 1e6)).sort_values('금액M', ascending=False)
    tot = g['금액M'].sum()
    print('\n===', title, '===')
    for i, (nat, r) in enumerate(g.head(n).iterrows(), 1):
        nl = nat.lower()
        mk = ' ★한국' if 'korea' in nl else (' <중국' if 'china' in nl else (' <일본' if nl == 'japan' else ''))
        print('%2d. %-24s %5d건 $%9.1fM %5.1f%%%s' % (i, nat[:22], int(r.건수), r.금액M, r.금액M / tot * 100, mk))
    return g


league(tr, '교통 낙찰 국적 리그 TOP12 (안방 포함)')
league(tr[~tr['is_domestic']], '안방 제거 = 순수 수출 리그 TOP12')

# (3) ITS 키워드 깔때기 — 정규식은 src/its_filter 단일 소스(테스트와 공유, 조용히 안 깨지게)
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.its_filter import ITS_RE, NON_ITS_RE, UPPER_ITS, AIR_SEA_RE, POSS_UPPER

blob = (tr['contract_description'].fillna('') + ' ' + tr['project_name'].fillna(''))
hit = tr[blob.str.contains(ITS_RE, na=False)].copy()
hb = blob[hit.index]
poss = (~hb.str.contains(NON_ITS_RE) & ~hb.str.contains(UPPER_ITS)) | \
       (~hb.str.contains(NON_ITS_RE) & hb.str.contains(POSS_UPPER))
air = hb.str.contains(AIR_SEA_RE) & ~hit['contract_description'].fillna('').str.contains(UPPER_ITS)
print('\nITS 키워드 깔때기: raw %d | 소유격its 제거 %d | 항공해상 제거 %d | 눈검증 후보 %d'
      % (len(hit), int(poss.sum()), int((air & ~poss).sum()), int((~poss & ~air).sum())))
keep = hit[~poss & ~air].copy()
print(keep['procurement_category'].value_counts().to_string())

REVIEW_COLS = ['fiscal_year', 'borrower_country', 'supplier', 'supplier_country',
               'procurement_category', AMT, 'contract_description', 'project_name', 'id_internal']
out = keep[REVIEW_COLS].copy()
out.insert(0, '판정', '')
OUT = 'data/processed/wb_its_review.csv'
if os.path.exists(OUT):
    print('주의:', OUT, '이미 있음 — 판정 보호 위해 덮어쓰지 않음')
else:
    out.sort_values(['procurement_category', 'fiscal_year']).to_csv(OUT, index=False, encoding='utf-8-sig')
    print('저장:', OUT, len(out), '행 (판정 열 비움 — 눈검증 대기)')

# 거짓음성 프로브: 09 교훈(정규식 밖 어휘). 비후보에서 ITS 인접어 훑어 눈검증 후보에 추가.
FN_RE = re.compile(
    r'\bCCTV\b|\bANPR\b|number plate|\bweigh\s?(?:bridge|station|-in-motion)|\bWIM\b|\bgantry|'
    r'\btoll (?:plaza|gate|collection|road|booth)|\btraffic (?:monitor|surveillance|count|light|sensor|camera)|'
    r'control (?:cent(?:er|re)|room)|command cent|smart (?:corridor|road|mobility|highway)|\bVMS\b|'
    r'road safety (?:camera|enforcement)', re.IGNORECASE)
nonhit = tr[~blob.str.contains(ITS_RE, na=False)]
nb = (nonhit['contract_description'].fillna('') + ' ' + nonhit['project_name'].fillna(''))
fn = nonhit[nb.str.contains(FN_RE, na=False)].copy()
print('\n거짓음성 프로브: %d건 (비후보 %d 중) — 판정 대기' % (len(fn), len(nonhit)))
OUT_FN = 'data/processed/wb_its_fn_probe.csv'
if os.path.exists(OUT_FN):
    print('주의:', OUT_FN, '이미 있음 — 판정 보호 위해 덮어쓰지 않음')
else:
    fn.to_csv(OUT_FN, index=False, encoding='utf-8-sig')
    print('저장:', OUT_FN, len(fn), '행')
