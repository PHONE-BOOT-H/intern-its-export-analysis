"""ADB Procurement by Nationality (공개 오픈데이터) -> 교통부문 계약자국 리그테이블.
A' 결정적 시험: '누가 개도국 교통·ITS 딜을 따가나'가 데이터로 나오나."""
import pandas as pd

AMT = 'ADB-FINANCED AMOUNT'
path = 'data/raw/adb_procurement_by_nationality.xlsx'
df = pd.read_excel(path, sheet_name='By Nationality (download only)', header=1)
df.columns = [str(c).strip() for c in df.columns]
df[AMT] = pd.to_numeric(df[AMT], errors='coerce')
print('전체 계약 행:', len(df), '| 기간', df['CONTRACT YEAR'].min(), '~', df['CONTRACT YEAR'].max())

tr = df[df['SECTOR'].astype(str).str.contains('transport', case=False, na=False)].copy()
tr_sum = tr[AMT].sum() / 1e6
print('교통(Transport) 부문 계약: {:,}건, 총 ADB자금 ${:,.0f}M'.format(len(tr), tr_sum))

def league(sub, title, topn=15):
    g = sub.groupby('NATIONALITY').agg(cnt=('NATIONALITY', 'size'),
                                       amtM=(AMT, lambda s: s.sum() / 1e6))
    g = g.sort_values('amtM', ascending=False)
    tot = g['amtM'].sum()
    print('\n=== {} — 계약자국 리그테이블 TOP{} ==='.format(title, topn))
    print('{:<4}{:<30}{:>7}{:>12}{:>8}'.format('순위', '계약자국', '건수', '금액$M', '점유%'))
    for i, (nat, row) in enumerate(g.head(topn).iterrows(), 1):
        n = str(nat).lower()
        mark = '  ★한국' if 'korea' in n else ('  <중국' if 'china' in n else ('  <일본' if n.strip() == 'japan' else ''))
        print('{:<4}{:<30}{:>7,}{:>12,.1f}{:>7.1f}%{}'.format(i, str(nat)[:28], int(row.cnt), row.amtM, row.amtM/tot*100, mark))
    for lab, key in [('한국', 'korea'), ('중국', 'china'), ('일본', 'japan')]:
        hits = [(r, nn) for r, nn in enumerate(g.index, 1) if key in str(nn).lower()]
        if hits:
            r, nn = hits[0]
            print('   · {}({}): {}위 / {}개국, ${:,.1f}M'.format(lab, nn, r, len(g), g.loc[nn, 'amtM']))

league(tr, '개도국 교통 전체')

its = tr[tr['SUBSECTOR'].astype(str).str.contains('traffic|intelligent|signal|ITS', case=False, na=False)].copy()
its_sum = its[AMT].sum() / 1e6
print('\n\nITS 근접(subsector=traffic/intelligent 등): {:,}건, ${:,.0f}M'.format(len(its), its_sum))
if len(its):
    print('  subsector 종류:', its['SUBSECTOR'].value_counts().head(6).to_dict())
    league(its, 'ITS 근접(교통관리 등)', topn=12)
