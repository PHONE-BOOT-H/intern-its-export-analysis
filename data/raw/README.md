# data/raw

원본 데이터. 전부 공개 오픈데이터다. 여기 파일은 수정하지 않고, git에도 올리지 않는다(용량·재배포 문제). 아래 출처에서 직접 받아 이 폴더에 둔다.

| 파일 | 내용 | 출처 | 라이선스 |
|---|---|---|---|
| `adb_procurement_by_nationality.xlsx` | ADB 낙찰, 계약자 국적별 (2016–2026) | data.adb.org/dataset/operational-procurement-database | Open Data Commons Attribution |
| `adb_procurement_by_origin.xlsx` | ADB 낙찰, 원산지별 | 위와 동일 | 위와 동일 |
| `aiddata_gcdf_v3.zip` | AidData 중국 해외 개발금융 v3.0 (교통 210) | aiddata.org | AidData 이용약관 |
| `crs_2014.parquet`~`crs_2023.parquet` | OECD CRS 양자 원조 10년 (교통 ITS 추출) | `oda_reader.download_crs_file(연도)` | OECD |
| `wb_transport_awards.parquet` | WB IPF 교통 낙찰 (FY2020~, 32,598건) | Finances One DS01693 (apiservice/sql, notebooks/13) | CC BY 4.0 |
| `itskorea_dashboard/*.json` | ITS 국제협력센터 수출통계 공개 API 캐시 | intl.its.go.kr (notebooks/11) | 자기보고 집계, 인용만 |
| `its_reference/*.xlsx` | 국가별 ITS 정부기관·정책 (검색·정리) | 공개출처 검색 정리물 (notebooks/16) | 공개출처 |

받는 법: ADB는 브라우저에서 XLSX 내려받는다(봇 다운로드 차단). AidData는 사이트에서 zip. CRS는 파이썬 `oda_reader`로 연도별(`pip install oda_reader`). WB는 notebooks/13이 SQL API로 받아 캐시한다. its_reference는 로컬 정리물(공개출처 검색).
