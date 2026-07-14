"""브리프 3절 숫자의 출처: 판정 끝난 AidData 리뷰 CSV에서 중국 ITS 최종표.
입력: data/processed/aiddata_its_review.csv (판정 O/X 전부 채워진 상태)
이행(집계권고 Yes) vs pledge를 나눠 센다 — 민스크 $102M은 약속만 있고 미이행.
"""
import pandas as pd

df = pd.read_csv('data/processed/aiddata_its_review.csv', encoding='utf-8-sig')
assert df['판정'].isin(['O', 'X']).all(), '판정 안 끝난 행 있음'

o = df[df['판정'] == 'O'].copy()
agg = o['Recommended For Aggregates'].astype(str).str.strip() == 'Yes'
print('교통(210) 검토', len(df), '행 중 ITS 성격 O:', len(o),
      '= 이행', agg.sum(), '+ pledge', (~agg).sum())

cols = ['Commitment Year', 'Recipient', 'Status', 'Flow Class',
        'Amount (Constant USD 2021)', 'Title']
print('\n[이행된 ITS — 전부 소액 그랜트]')
print(o.loc[agg, cols].sort_values('Commitment Year').to_string(index=False))
print('이행 합계 $M (금액 확인분):',
      round(o.loc[agg, 'Amount (Constant USD 2021)'].sum() / 1e6, 1))

print('\n[미이행 pledge — 각주용]')
print(o.loc[~agg, cols].to_string(index=False))

# 무산된 대형 시도 2건의 근거 행 (판정 X지만 브리프에 인용)
acc = df[df['AidData Record ID'] == 73140].iloc[0]
print('\n[아크라 — ITS 계약 취소 근거]')
print(acc['Title'], '| $', round(acc['Amount (Constant USD 2021)'] / 1e6, 1), 'M')
print('비고:', acc['비고'])
