import pandas as pd
from datetime import date

PERIODS = 24
index = pd.RangeIndex(PERIODS)

columns = ['amount', 'repayment', 'amount_end']

a = pd.DataFrame(index=index, columns=columns)


a.amount = range(PERIODS, 0, -1)
a.amount *= 100
a.repayment = 100
a.amount_end = a.amount - 100

print(a)

# turn index into date

start_date = date(2020, 1, 1)
new_index = pd.period_range('2019-05', periods=PERIODS, freq='M')

b = a.set_index(new_index, drop=True)
print(b)

c = b.groupby(b.index.year).agg(
    amount=pd.NamedAgg(column='amount', aggfunc='first'),
    repayment=pd.NamedAgg(column='repayment', aggfunc='sum'),
    amount_end=pd.NamedAgg(column='amount_end', aggfunc='last'),
)

# aggregate customized
print(c)
