from bisect import bisect

import pandas as pd
import numpy as np

from mortgage_scenarios import MortgageLoanRunner, LoanPartIterator, get_monthly_rate
from mortgage_scenarios.core import group_by_year
####
# Settings
####
USE_LTV = False

houseprice = 631000

def get_ltv_tranch(amount, houseprice):
    ltv_boundaries = (0.675, 0.9, 1.0)
    ltv_tranch_names = ('<67.5%', '67.5% - 90%', '90% - 100%', '>100%')
    ltv = amount / houseprice
    ltv_index = bisect(ltv_boundaries, ltv)
    return ltv_index, ltv_tranch_names[ltv_index]

PERIODS = 30

pd.options.display.precision = 2
pd.options.display.float_format = '{:,.2f}'.format

rates = np.array([0.0215, 0.0195, 0.0195])
rates += 0.00017
fixed = 0
loan1 = LoanPartIterator(92500, rates[0], PERIODS, future=92500, fixed=fixed, yearly=True)
loan2 = LoanPartIterator(198183, rates[1], PERIODS, fixed=fixed, yearly=True)
loan3 = LoanPartIterator(144000, rates[2], PERIODS, fixed=fixed, yearly=True)
loans = [loan1, loan2, loan3]

# ----

mortgage = MortgageLoanRunner()
for loan in loans:
    mortgage.add_loanpart(loan)

print('total loan %.2f euro' % mortgage.current_amount)
# TODO: set rates based on current ltv
ltv_info = get_ltv_tranch(mortgage.current_amount, houseprice)

eventlog = []
while True:
    events = []
    try:
        mortgage.step()
    except StopIteration:
        break

    # ltv check
    new_ltv = get_ltv_tranch(mortgage.current_amount, houseprice)
    if USE_LTV and new_ltv != ltv_info and new_ltv[0] == 0:
        events.append('ltv < 67.5%')
        mortgage.replace_loanpart(loan1, loan1.new_loanpart_with_rate(
            get_monthly_rate(0.019)))
        mortgage.replace_loanpart(loan2, loan2.new_loanpart_with_rate(
            get_monthly_rate(.0175)))
        mortgage.replace_loanpart(loan3, loan3.new_loanpart_with_rate(
            get_monthly_rate(.0175)))
        ltv_info = new_ltv

    # repayment check

    if mortgage.period in [10, 20]:
        print('do repayment')
        events.append('repayment')

    eventlog.append(";".join(events))

df = mortgage.to_dataframe()
df['events'] = eventlog
df['ltv'] = df['amount'] / houseprice

# print(df)
df2 = mortgage.to_dataframe()

df_agg = group_by_year(df2, '2020-9')
print(df_agg)

# print(df2.loc[:3])