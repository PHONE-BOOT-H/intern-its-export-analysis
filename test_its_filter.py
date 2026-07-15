"""src/its_filter.classify 검증. 실행: python test_its_filter.py (레포 루트에서).

이 필터는 CRS·중국·WB 전 층의 ITS 판정 후보를 정하는 심장이다. 조용히 깨지면
모든 층 숫자가 틀어져도 안 잡히므로, 알려진 오탐/정상 케이스를 여기 고정한다.
프레임워크 없음 — assert만.
"""
from src.its_filter import classify

CASES = [
    # (text, title, expected, 왜)
    ('Intelligent Transport System deployment on the corridor', '', 'candidate', '실명 ITS'),
    ('Supply and installation of Traffic Management Centre hardware', '', 'candidate', '관제센터'),
    ('Electronic Toll Collection (ETC) system', '', 'candidate', '요금징수'),
    # 소유격 오탐 — 브리프가 경고한 그 케이스
    ('CONSTRUCTION OF NGHWANDE BRIDGE AND ITS ROAD APPROACHES', '', 'possessive', '대문자 소유격 ITS'),
    ('Rehabilitation of the road and its drainage components', '', 'possessive', '소문자 소유격 its'),
    # 항공·해상 — 교통이지만 도로 ITS 아님
    ('Air traffic control tower automation', '', 'air_sea', '항공관제'),
    ('Vessel traffic management for the port authority', '', 'air_sea', '해상교통'),
    # 항공해상 어휘 있어도 제목에 대문자 ITS면 진짜 ITS로 봄(예외)
    ('airport access road traffic control', 'Highway ITS Package', 'candidate', 'air_sea 예외: 제목 ITS'),
    # 매칭 자체 없음
    ('Supply of laptops, computers and office furniture', '', 'no_match', 'ITS 어휘 없음'),
    ('Rehabilitation of 40km rural gravel road', '', 'no_match', '도로 토목만'),
]


def demo():
    fail = 0
    for text, title, exp, why in CASES:
        got = classify(text, title)
        ok = got == exp
        fail += not ok
        print(f"  {'OK ' if ok else 'FAIL'} [{exp:>10} | got {got:>10}] {why}")
        assert ok, f'\n  기대 {exp}, 실제 {got}\n  text={text!r} title={title!r}'
    print(f'\n{len(CASES)}건 전부 통과.' if not fail else f'{fail}건 실패.')


if __name__ == '__main__':
    demo()
