"""WB ITS 판정 최종표 = 브리프 [구멍1] 결론. 입력: notebooks/13 parquet + 14 후보.

판정: notebooks/14가 만든 후보(키워드 66 + 거짓음성 프로브 88 = 154)를 opus 교차판정
(2독립 렌즈 x 2그룹 + 불일치 16건 3차 조정, wf_7d5541fc). 확정 O 52행을 아래에 고정.
X는 나머지 전부(소유격 its·건물 CCTV·경관지 관제·통신탑·도로토목 등).

핵심 질문(ADB 대조): ADB by-title은 ITS 24건 전부 컨설팅·장비(works 0), 기술경쟁 거의 0.
WB(IPF FY2020+)는? -> 실명 ITS가 실제로 발주되고, 누가 먹나.
"""
import pandas as pd

# 교차판정 확정 O (id_internal). 감사추적: 판정 근거는 wf_7d5541fc 워크플로 결과.
CONFIRMED_O = {
    '16928', '36916', '41202', '49106', '70129', '84564', '104001', '113917', '138039',
    '161831', '135871', '135872', '135873', '143683', '150204', '150205', '150206',
    '150207', '320', '3781', '14913', '29576', '30577', '39808', '75118', '75119',
    '81913', '82454', '118144', '119517', '120411', '120412', '182036', '182038',
    '278209', '5794', '11556', '20031', '49745', '49746', '51237', '66555', '70918',
    '133674', '154543', '162498', '207469', '211109', '211110', '240949', '86924', '191958',
}

AMT = 'supplier_contract_amount_usd'
tr = pd.read_parquet('data/raw/wb_transport_awards.parquet')
tr[AMT] = pd.to_numeric(tr[AMT], errors='coerce').fillna(0)
o = tr[tr['id_internal'].astype(str).isin(CONFIRMED_O)].copy()

print('확정 ITS 계약행:', len(o), '| 고유 project_name:', o['project_name'].nunique(),
      '| 금액합 $%.1fM' % (o[AMT].sum() / 1e6))
print('기간 FY%d~%d' % (o['fiscal_year'].min(), o['fiscal_year'].max()))

print('\n[조달 유형] — ADB는 ITS가 works 0, 전부 컨설팅·장비였다')
print(o['procurement_category'].value_counts().to_string())

print('\n[공급국 리그 (금액$M)] — MDB ITS 시장은 누가 먹나')
lg = (o.groupby('supplier_country')[AMT].sum() / 1e6).sort_values(ascending=False)
tot = lg.sum()
for nat, v in lg.head(10).items():
    nl = str(nat).lower()
    mk = ' ★한국' if 'korea' in nl else (' <중국' if 'china' in nl or 'hong kong' in nl else '')
    print('  %-22s $%7.1fM  %5.1f%%%s' % (str(nat)[:20], v, v / tot * 100, mk))

china = lg[[i for i in lg.index if 'china' in str(i).lower() or 'hong kong' in str(i).lower()]].sum()
kor = lg[[i for i in lg.index if 'korea' in str(i).lower()]].sum()
print('\n  => 중국(홍콩 포함) $%.1fM (%.0f%%) | 한국 $%.1fM (%.0f%%)'
      % (china, china / tot * 100, kor, kor / tot * 100))

print('\n[대형 ITS 계약 TOP8]')
for _, r in o.sort_values(AMT, ascending=False).head(8).iterrows():
    print('  %-14s $%5.1fM  %s' % (str(r['supplier_country'])[:13], r[AMT] / 1e6,
                                   str(r['contract_description'])[:80]))
