"""WB 층: World Bank 낙찰(IPF 계약낙찰)에서 교통 부문 수집.

소스: WBG Finances One "EDS03 Contract Awards in Investment Project Financing"
(DS01693, FY2020~현재, STEP 추적). 라이선스 CC BY 4.0.
API는 datasetId/resourceId GET이 아니라 SQL POST로 서빙된다(SPA 요청 관찰로 확인):
  POST https://datacatalogapi.worldbank.org/dexapps/fone/api/apiservice/sql
  body {"sql":"SELECT * FROM {0} WHERE ...","assetId":"DS00005"}
  {0}은 서버가 자산 테이블로 치환. assetId DS00005가 이 데이터셋을 서빙(컬럼·건수로 검증).
  페이지네이션은 SQL Server OFFSET/FETCH, 최대 1000행/요청.

교통 필터: project_global_practice LIKE '%Transport%' (조회 시점 32,598행).
전체 284,114행 중 교통만 받아 캐시. ADB 파이프라인(01~03)과 같은 국적/안방/ITS 분석을 14에서.
"""
import os
import time

import pandas as pd
import requests

API = 'https://datacatalogapi.worldbank.org/dexapps/fone/api/apiservice/sql'
ASSET = 'DS00005'
WHERE = "project_global_practice LIKE '%Transport%'"
PAGE = 1000
CACHE = 'data/raw/wb_transport_awards.parquet'


def run_sql(sql):
    r = requests.post(API, json={'sql': sql, 'assetId': ASSET},
                      headers={'Referer': 'https://financesone.worldbank.org/'}, timeout=60)
    r.raise_for_status()
    return r.json().get('data', [])


if os.path.exists(CACHE):
    tr = pd.read_parquet(CACHE)
    print('캐시 로드:', CACHE, len(tr), '행')
else:
    total = run_sql(f"SELECT COUNT(*) AS 'count' FROM (SELECT 0 AS count FROM {{0}} WHERE {WHERE}) AS t")[0]['count']
    print('교통 총건(서버 COUNT):', total)
    rows = []
    off = 0
    while True:
        page = run_sql(f"SELECT * FROM {{0}} WHERE {WHERE} "
                       f"ORDER BY id_internal OFFSET {off} ROWS FETCH NEXT {PAGE} ROWS ONLY")
        rows += page
        print('  받음', off, '~', off + len(page))
        if len(page) < PAGE:
            break
        off += PAGE
        time.sleep(0.2)
    tr = pd.DataFrame(rows).drop_duplicates('id_internal')
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    tr.to_parquet(CACHE)
    # 수집 == 서버 COUNT (중복 제거 후). 하루 갱신이라 근사 허용.
    assert abs(len(tr) - total) <= PAGE, f'수집 {len(tr)} vs 서버 {total} 불일치'
    print('저장:', CACHE, len(tr), '행 (서버', total, ')')

print('기간 FY', int(tr['fiscal_year'].min()), '~', int(tr['fiscal_year'].max()))
print('컬럼:', list(tr.columns))
