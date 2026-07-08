# data/raw

원본 데이터. 전부 공개 오픈데이터다. 여기 파일은 수정하지 않고, git에도 올리지 않는다(용량·재배포 문제). 아래 출처에서 직접 받아 이 폴더에 둔다.

| 파일 | 내용 | 출처 | 라이선스 |
|---|---|---|---|
| `adb_procurement_by_nationality.xlsx` | ADB 낙찰, 계약자 국적별 (2016–2026) | data.adb.org/dataset/operational-procurement-database | Open Data Commons Attribution |
| `adb_procurement_by_origin.xlsx` | ADB 낙찰, 원산지별 (2016–2026) | 위와 동일 | 위와 동일 |
| `aiddata_gcdf_v3.zip` | AidData 중국 해외 개발금융 v3.0 | aiddata.org | AidData 이용약관 |
| `crs_2022.parquet/` | OECD CRS 양자 원조 2022 (교통 ITS 추출용) | `oda_reader.download_crs_file(2022)` | OECD |

받는 법: ADB는 브라우저에서 XLSX를 내려받는다(봇 다운로드는 차단됨). AidData는 사이트에서 zip을 받는다. CRS는 파이썬 `oda_reader`로 연도별 받는다(`pip install oda_reader`).

아직 안 붙인 것: World Bank 낙찰(financesone DS01693, API·벌크), CRS 다년치(현재 2022만).
