"""notebook 16 — 타겟 매트릭스 (스캐폴드).

우리 ITS 데이터(누가 어디서 이겼나) + 한태영이 검색·정리한 국가별 ITS 정부기관
파일을 붙여, "양자에서 싸워라"를 "어느 시장·누구랑"으로 구체화한다.
스코프 고정: 우리 데이터에 실제 ITS 거래가 뜬 나라만. 새 나라 안 끌어옴.

PART A (완성): 3개 채널 판정 O에서 바이어국 x 채널 x 승자 x 금액 뽑음.
PART B (한태영 TODO): 정부기관 파일과 merge + 전략 read-off. 아래 지시대로.

주의: 정부기관 파일은 공개출처 검색·정리물(회사 내부자료 아님, 사용 OK).
data/raw/its_reference/ 에 두고 참조. data/raw는 gitignore라 커밋 안 됨(로컬 재현).
"""
import pandas as pd

AG_FILE = 'data/raw/its_reference/국가별 ITS 정부기관.xlsx'

# 영문 수원/차주국 -> 한글 (기관파일과 조인 키). 지역묶음·중국(바이어로는 무의미)은 제외.
NAME_MAP = {
    'Viet Nam': '베트남', 'India': '인도', 'Indonesia': '인도네시아', 'Cambodia': '캄보디아',
    'Mexico': '멕시코', 'Colombia': '콜롬비아', 'Paraguay': '파라과이', 'Sri Lanka': '스리랑카',
    'Brazil': '브라질', 'Egypt': '이집트', 'Bangladesh': '방글라데시', 'Nigeria': '나이지리아',
    'Ukraine': '우크라이나', 'Türkiye': '튀르키예', 'Peru': '페루', 'Philippines': '필리핀',
    'Ecuador': '에콰도르', "Lao People's Democratic Republic": '라오스', 'El Salvador': '엘살바도르',
    'Benin': '베냉', 'Azerbaijan': '아제르바이잔', 'Burundi': '부룬디', 'Gambia': '감비아',
    'Rwanda': '르완다', 'Mozambique': '모잠비크', 'Tanzania': '탄자니아', 'Tunisia': '튀니지',
    'Thailand': '태국', 'Uganda': '우간다', 'Venezuela': '베네수엘라',
    'Moldova': '몰도바', 'Belarus': '벨라루스', 'Liberia': '라이베리아',
    'Ethiopia': '에티오피아', 'Mongolia': '몽골', 'Albania': '알바니아', 'Ghana': '가나',
    'Georgia': '조지아', 'Uzbekistan': '우즈베키스탄', 'Kenya': '케냐', 'Sierra Leone': '시에라리온',
}


def ko(name):
    return NAME_MAP.get(str(name).strip())


rows = []  # (국가명, 채널, 승자, 금액M)

# --- CRS 10년 (양자 원조). 승자 = 약정액 최다 공여국(값 캡처 기준) ---
crs = pd.read_csv('data/processed/crs_multiyear_its_review.csv', encoding='utf-8-sig')
co = crs[crs['판정'].astype(str).str.strip() == 'O']
for rec, d in co.groupby('RecipientName'):
    k = ko(rec)
    if not k:
        continue
    amt = d.groupby('DonorName')['USD_Commitment'].sum()
    winner = amt.idxmax() if amt.max() > 0 else d['DonorName'].value_counts().idxmax()
    rows.append((k, 'CRS(양자원조)', winner, round(d['USD_Commitment'].sum(), 1)))

# --- AidData 중국 (BRI). 이행분만(Recommended For Aggregates=Yes). 승자 전부 중국.
#     민스크 $102M 등 pledge(미이행)는 제외 — 브리프 3절과 동일 처리. ---
ai = pd.read_csv('data/processed/aiddata_its_review.csv', encoding='utf-8-sig')
ao = ai[(ai['판정'].astype(str).str.strip() == 'O')
        & (ai['Recommended For Aggregates'].astype(str).str.strip() == 'Yes')]
for rec, d in ao.groupby('Recipient'):
    k = ko(rec)
    if not k:
        continue
    rows.append((k, 'AidData(중국BRI)', 'China', round(d['Amount (Constant USD 2021)'].sum() / 1e6, 1)))

# --- WB (IPF 낙찰). 승자 = 낙찰액 최다 공급국. 판정 O는 15와 동일 고정셋 ---
WB_O = {
    '16928', '36916', '41202', '49106', '70129', '84564', '104001', '113917', '138039',
    '161831', '135871', '135872', '135873', '143683', '150204', '150205', '150206',
    '150207', '320', '3781', '14913', '29576', '30577', '39808', '75118', '75119',
    '81913', '82454', '118144', '119517', '120411', '120412', '182036', '182038',
    '278209', '5794', '11556', '20031', '49745', '49746', '51237', '66555', '70918',
    '133674', '154543', '162498', '207469', '211109', '211110', '240949', '86924', '191958',
}
wb = pd.read_parquet('data/raw/wb_transport_awards.parquet')
wo = wb[wb['id_internal'].astype(str).isin(WB_O)].copy()
wo['amt'] = pd.to_numeric(wo['supplier_contract_amount_usd'], errors='coerce').fillna(0)
for bc, d in wo.groupby('borrower_country'):
    k = ko(bc)
    if not k:
        continue
    amt = d.groupby('supplier_country')['amt'].sum()
    rows.append((k, 'WB(IPF낙찰)', amt.idxmax(), round(d['amt'].sum() / 1e6, 1)))

buyers = pd.DataFrame(rows, columns=['국가명', '채널', '승자', '금액M'])
print('바이어국 x 채널 행:', len(buyers), '| 고유국:', buyers['국가명'].nunique())
print(buyers.sort_values(['국가명', '채널']).to_string(index=False))
# 참고: CRS는 한국이 '행수'로는 최다인 나라 많지만 여기 승자는 '금액' 기준이라
#      일본/스페인/미국이 잡힌다(브리프 "한국=소프트 다건, 일본=하드 대액"). read-off 때 기억.

# ======================= PART B — 타겟 매트릭스 =======================
# buyers에 카운터파트 ITS 기관을 붙이고, 전략 후보를 기계적으로 뽑는다.
ag = pd.read_excel(AG_FILE)[['국가명', 'ITS 정부기관']].copy()
ag['국가명'] = ag['국가명'].astype(str).str.strip()
merged = pd.merge(buyers, ag, on='국가명', how='left')   # 우리 바이어국 기준(left)

# read-off (조건 AND): 수요 있음(자동) + 기관 있음(액션 가능) + 한국이 아직 안 먹음
has_agency = merged['ITS 정부기관'].notna()
korea_wins = merged['승자'].astype(str).str.contains('Korea')  # 'Korea'/'Korea, Republic of' 둘 다
cand = merged[has_agency & ~korea_wins].copy()
china = cand['승자'] == 'China'

print('\n=== 집중 후보 (기관 있음 + 한국 아직 안 먹음) — 금액순 ===')
print(cand.sort_values('금액M', ascending=False)[
    ['국가명', '채널', '승자', '금액M', 'ITS 정부기관']].to_string(index=False))
print('\n  그중 중국이 먹는 중(= 뺏기는 시장):',
      ', '.join(cand[china].sort_values('금액M', ascending=False)['국가명']))

# 참고: 한국이 이미 승자(필터에서 빠짐) = 이미 우리 것
print('\n[이미 한국 우위 — 지킬 시장]:',
      ', '.join(sorted(set(merged[korea_wins]['국가명']))))
# 참고: 기관 불명(NaN) = 카운터파트 못 찾음, 진입 난이도↑
print('[카운터파트 불명 — 진입난이도↑]:',
      ', '.join(sorted(set(merged[merged['ITS 정부기관'].isna()]['국가명']))))
