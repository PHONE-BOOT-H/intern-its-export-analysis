"""데이터 충분성 점검: ITS 니치 636건을 works/goods/consulting로 쪼개서
'중국 54%'가 진짜 ITS 기술인지 도로공사인지, 그리고 진짜-ITS N이 분석할 만큼 남는지 확인."""
import pandas as pd

AMT = 'ADB-FINANCED AMOUNT'
path = 'data/raw/adb_procurement_by_nationality.xlsx'
df = pd.read_excel(path, sheet_name='By Nationality (download only)', header=1)
df.columns = [str(c).strip() for c in df.columns]
df[AMT] = pd.to_numeric(df[AMT], errors='coerce')

tr = df[df['SECTOR'].astype(str).str.contains('transport', case=False, na=False)]
its = tr[tr['SUBSECTOR'].astype(str).str.contains('traffic|intelligent|signal|ITS', case=False, na=False)].copy()
print('ITS 근접(교통관리) 총:', len(its), '건, $%.0fM' % (its[AMT].sum()/1e6))

print('\n[NATURE OF PROCUREMENT 분해] (이게 works면 도로공사, goods/consulting이면 기술/장비)')
g = its.groupby('NATURE OF PROCUREMENT').agg(건수=('NATURE OF PROCUREMENT','size'),
                                             금액M=(AMT, lambda s: s.sum()/1e6)).sort_values('금액M', ascending=False)
for nat, row in g.iterrows():
    print('  %-32s %5d건  $%9.1fM' % (str(nat)[:30], int(row.건수), row.금액M))

# works 제외 = 기술/장비/컨설팅 proxy
tech = its[~its['NATURE OF PROCUREMENT'].astype(str).str.contains('works|civil', case=False, na=False)].copy()
print('\n[works 제외 = 진짜 ITS 기술 proxy] N =', len(tech), '건, $%.0fM' % (tech[AMT].sum()/1e6))
if len(tech):
    lg = tech.groupby('NATIONALITY').agg(건수=('NATIONALITY','size'),
                                         금액M=(AMT, lambda s: s.sum()/1e6)).sort_values('금액M', ascending=False)
    tot = lg['금액M'].sum()
    print('  계약자국 TOP10:')
    for i,(nat,row) in enumerate(lg.head(10).iterrows(),1):
        n=str(nat).lower(); mk='  ★한국' if 'korea' in n else ('  <중국' if 'china' in n else '')
        print('   %2d. %-26s %4d건  $%8.1fM  %4.1f%%%s' % (i,str(nat)[:24],int(row.건수),row.금액M,row.금액M/tot*100,mk))
    for lab,key in [('한국','korea'),('중국','china'),('일본','japan')]:
        hits=[(r,nn) for r,nn in enumerate(lg.index,1) if key in str(nn).lower()]
        if hits: r,nn=hits[0]; print('    · %s: %d위/%d개국 $%.1fM' % (lab,r,len(lg),lg.loc[nn,'금액M']))

# 진짜 'ITS/intelligent/C-ITS' 키워드가 설명/제목에 실제 몇 건이나?
kwmask = (its['CONTRACT DESCRIPTION'].astype(str)+' '+its['PROJECT TITLE'].astype(str)).str.contains(
    'intelligent|ITS|C-ITS|V2X|smart traffic|ATMS|signal|tolling|electronic toll', case=False, na=False)
print('\n[설명/제목에 ITS 키워드 실제 포함] N =', int(kwmask.sum()), '건 (교통관리 636건 중)')
