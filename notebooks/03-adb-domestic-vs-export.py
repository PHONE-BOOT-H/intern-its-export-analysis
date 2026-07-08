"""ADB 교통 낙찰: '자국 업체 안방 낙찰(domestic)' vs '국경 넘은 수출(cross-border)' 분해.
결정적 시험: nationality 리그의 상위(인도·필리핀 등)가 사업국==등록국이라 뻥튀기된 건지,
한국 4위는 전부 cross-border라 진짜 수출인지. 등록국 때문에 순위가 왜곡됐는지 대조한다.

배관은 여기서, 해석은 한태영이. 각 숫자를 한태영이 방어할 수 있어야 한다."""
import pandas as pd

AMT = 'ADB-FINANCED AMOUNT'


def load_transport(path, sheet):
    df = pd.read_excel(path, sheet_name=sheet, header=1)
    df.columns = [str(c).strip() for c in df.columns]
    df[AMT] = pd.to_numeric(df[AMT], errors='coerce')
    for c in ['NATIONALITY', 'BORROWING COUNTRY']:
        df[c] = df[c].astype(str).str.strip()
    return df[df['SECTOR'].astype(str).str.contains('transport', case=False, na=False)].copy()


tr = load_transport('data/raw/adb_procurement_by_nationality.xlsx',
                    'By Nationality (download only)')
print('교통 계약행:', len(tr), '| 총 ADB자금 $%.0fM' % (tr[AMT].sum() / 1e6))

# 핵심: 등록국==사업국이면 domestic(안방), 아니면 cross-border(국경 넘은 수출)
tr['is_domestic'] = tr['NATIONALITY'] == tr['BORROWING COUNTRY']
dom = tr[tr['is_domestic']][AMT].sum() / 1e6
xb = tr[~tr['is_domestic']][AMT].sum() / 1e6
print('  domestic(등록국=사업국) $%.0fM (%.1f%%)  |  cross-border $%.0fM (%.1f%%)'
      % (dom, dom / (dom + xb) * 100, xb, xb / (dom + xb) * 100))

# 리그테이블에 domestic 비중을 붙인다: 상위국이 안방 덕에 큰 건지 드러낸다
g = tr.groupby('NATIONALITY').agg(
    건수=('NATIONALITY', 'size'),
    금액M=(AMT, lambda s: s.sum() / 1e6),
    안방M=(AMT, lambda s: 0),  # placeholder, 아래서 계산
)
dom_by_nat = tr[tr['is_domestic']].groupby('NATIONALITY')[AMT].sum() / 1e6
g['안방M'] = g.index.map(dom_by_nat).fillna(0.0)
g['안방%'] = (g['안방M'] / g['금액M'] * 100).round(0)
g = g.sort_values('금액M', ascending=False)
tot = g['금액M'].sum()

print('\n=== 교통 낙찰 리그 TOP15 (안방% = 자국내 낙찰 비중) ===')
print('%-4s%-26s%7s%10s%8s%9s' % ('순위', '등록국', '건수', '금액$M', '점유%', '안방%'))
for i, (nat, r) in enumerate(g.head(15).iterrows(), 1):
    n = nat.lower()
    mk = ' ★한국' if 'korea' in n else (' <중국' if 'china' in n else (' <일본' if n == 'japan' else ''))
    print('%-4d%-26s%7d%10.1f%7.1f%%%8.0f%%%s'
          % (i, nat[:24], int(r.건수), r.금액M, r.금액M / tot * 100, r['안방%'], mk))

# cross-border만 남긴 '진짜 수출 리그' — 안방 빼면 순위가 어떻게 바뀌나
xbdf = tr[~tr['is_domestic']]
gx = xbdf.groupby('NATIONALITY').agg(건수=('NATIONALITY', 'size'),
                                     금액M=(AMT, lambda s: s.sum() / 1e6)).sort_values('금액M', ascending=False)
totx = gx['금액M'].sum()
print('\n=== 안방 제거 후 = 순수 수출(cross-border) 리그 TOP15 ===')
print('%-4s%-26s%7s%10s%8s' % ('순위', '등록국', '건수', '금액$M', '점유%'))
for i, (nat, r) in enumerate(gx.head(15).iterrows(), 1):
    n = nat.lower()
    mk = ' ★한국' if 'korea' in n else (' <중국' if 'china' in n else (' <일본' if n == 'japan' else ''))
    print('%-4d%-26s%7d%10.1f%7.1f%%%s' % (i, nat[:24], int(r.건수), r.금액M, r.금액M / totx * 100, mk))
for lab, key in [('한국', 'korea'), ('중국', 'china'), ('일본', 'japan')]:
    hits = [(rk, nn) for rk, nn in enumerate(gx.index, 1) if key in nn.lower()]
    if hits:
        rk, nn = hits[0]
        print('   · %s: 안방 전 %s위 -> 안방 후 %d위' % (
            lab, [j for j, x in enumerate(g.index, 1) if x == nn][0], rk))

# 보너스 대조: origin 파일로 한국 등록 교통 낙찰의 '실제 물자 원산지'가 정말 한국인가
o = pd.read_excel('data/raw/adb_procurement_by_origin.xlsx', sheet_name='By Origin (for download)', header=1)
o.columns = [str(c).strip() for c in o.columns]
o[AMT] = pd.to_numeric(o[AMT], errors='coerce')
otr = o[o['SECTOR'].astype(str).str.contains('transport', case=False, na=False)]
kor = otr[otr['NATIONALITY'].astype(str).str.contains('korea', case=False, na=False)]
print('\n[대조] origin 파일 — 한국 등록 교통 낙찰 %d행, 실제 ORIGIN OF GOODS 상위:' % len(kor))
og = kor.groupby('ORIGIN OF GOODS')[AMT].sum().sort_values(ascending=False) / 1e6
for org, v in og.head(6).items():
    print('   %-28s $%8.1fM' % (str(org)[:26], v))
