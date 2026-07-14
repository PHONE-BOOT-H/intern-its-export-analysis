"""한국 실측 층(Layer 4): ITS 국제협력센터 수출통계 대시보드.
페이지 차트가 쓰는 공개 JSON API(인증 불필요)를 그대로 받아 data/raw에 캐시.
주의: 페이지에 보이는 요약 숫자는 JS 렌더 전 플레이스홀더 — 반드시 API 값을 쓴다.
출처 표기: "ITS 국제협력센터 수출통계(intl.its.go.kr), 조회일" (KOGL 미표기라 재배포는 지양)
"""
import json
import os
import urllib.request

BASE = 'https://intl.its.go.kr/api/export/statistics/'
ENDPOINTS = ['annual', 'nation', 'continent', 'service', 'biz-kind']
RAW = 'data/raw/itskorea_dashboard'
os.makedirs(RAW, exist_ok=True)

data = {}
for ep in ENDPOINTS:
    path = f'{RAW}/{ep}.json'
    if os.path.exists(path):
        data[ep] = json.load(open(path, encoding='utf-8'))
    else:
        req = urllib.request.Request(BASE + ep, headers={'User-Agent': 'Mozilla/5.0'})
        data[ep] = json.load(urllib.request.urlopen(req))
        json.dump(data[ep], open(path, 'w', encoding='utf-8'), ensure_ascii=False)
        print('받음:', ep, len(data[ep]), '행')

ann = data['annual']
total_amt = sum(r['totalAmtUsd'] for r in ann)
total_cnt = sum(r['bizCnt'] for r in ann)
years = sorted(r['year'] for r in ann)
print(f'\n연도별 합계: {years[0]}~{years[-1]} | {total_cnt}건 | ${total_amt/1e9:.2f}B')
print('국가 수:', len(data['nation']))

print('\n[국가별 상위 5 — 금액]')
for r in sorted(data['nation'], key=lambda r: -r['totalAmtUsd'])[:5]:
    print(f"  {r['ntnl']:<12} {r['bizCnt']:>4}건  ${r['totalAmtUsd']/1e6:>7.1f}M  {r['rate']}%")

print('\n[서비스별 — 금액]')
for r in sorted(data['service'], key=lambda r: -r['totalAmtUsd']):
    print(f"  {r['serviceTy']:<14} {r['bizCnt']:>4}건  ${r['totalAmtUsd']/1e6:>7.1f}M")

print('\n[사업종류별]')
for r in data['biz-kind']:
    print(f"  {r['bizKind']:<8} {r['bizCnt']:>4}건  ${r['totalAmtUsd']/1e6:>7.1f}M  {r['rate']}%")
