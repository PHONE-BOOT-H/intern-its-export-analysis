"""ITS 키워드 필터 — CRS·AidData·WB 층 공용 단일 소스.

키워드 매칭 후 오탐을 거른다:
- 소유격 'its' (영어 소유격이 대문자 ITS로 잡히는 것 포함)
- 항공관제·해상교통 (교통이지만 도로 ITS 아님)

정규식이 여기 한 곳에만 있어, 바뀌면 노트북과 테스트가 같이 본다.
notebooks/14가 이 정규식을 import해서 벡터 연산에 쓴다. test_its_filter.py가 classify()로 검증.
"""
import re

ITS_RE = re.compile(
    r'\bintelligent transport|\bITS\b|\bC-ITS\b|\bV2X\b|\btraffic management|'
    r'\btraffic signal|\btraffic control|\bATMS\b|\belectronic toll|\btolling\b|'
    r'\bsmart mobility|\bsmart traffic|\bvariable message|\bvehicle detection|'
    r'\bincident management|\bATC\b|\badaptive signal', re.IGNORECASE)
# ITS_RE에서 대문자 약어 \bITS\b만 뺀 것 — 소유격 판별용(진짜 ITS 어휘가 하나라도 있나)
NON_ITS_RE = re.compile(ITS_RE.pattern.replace(r'\bITS\b|', ''), re.IGNORECASE)
UPPER_ITS = re.compile(r'\bITS\b')                    # 대문자 ITS만 (IGNORECASE 아님)
AIR_SEA_RE = re.compile(
    r'\bair.traffic|\baviation\b|\bairport|\bairspace|\bmaritime\b|\bmarine\b|'
    r'\bvessel traffic|\bport authority|\bharbou?r\b|\brailway signal', re.IGNORECASE)
# "... AND ITS ROAD/APPROACHES ..." 처럼 대문자 ITS가 소유격인 경우
POSS_UPPER = re.compile(
    r'\bITS\s+(?:road|approach|approaches|own|respective|components?|tributar)', re.IGNORECASE)


def classify(text, title=''):
    """한 건을 분류: 'no_match' | 'possessive' | 'air_sea' | 'candidate'.

    notebooks/14의 벡터 마스크와 같은 규칙의 단일-건 버전.
    title = 항공해상 예외 판정에 쓰는 필드(대문자 ITS 있으면 진짜 ITS로 봄).
    """
    blob = f'{text} {title}'
    if not ITS_RE.search(blob):
        return 'no_match'
    has_nonits = bool(NON_ITS_RE.search(blob))
    has_upper = bool(UPPER_ITS.search(blob))
    # 소유격: 진짜 ITS 어휘가 없고 (대문자 ITS도 없거나 / 있어도 소유격 패턴)
    if not has_nonits and (not has_upper or POSS_UPPER.search(blob)):
        return 'possessive'
    if AIR_SEA_RE.search(blob) and not UPPER_ITS.search(title):
        return 'air_sea'
    return 'candidate'
