from bisect import bisect

import pandas as pd
import numpy as np

from mortgage_scenarios import MortgageLoanRunner, LoanPartIterator, get_monthly_rate
from mortgage_scenarios.core import group_by_year
####
# Settings
####
USE_LTV = True
start_period = '2020-10'
houseprice = 631000
rates_addon = 0.000175
years = 30
#####



pd.options.display.precision = 2
pd.options.display.float_format = '{:,.0f}'.format

rates = np.array([0.0215, 0.0195, 0.0195])

rates += rates_addon
fixed = 0
loan1 = LoanPartIterator(92500, rates[0], years, future=92500, fixed=fixed, yearly=True)
loan2 = LoanPartIterator(198183, rates[1], years, fixed=fixed, yearly=True)
loan3 = LoanPartIterator(144000, rates[2], years, fixed=fixed, yearly=True)
loans = [loan1, loan2, loan3]

# ----

mortgage = MortgageLoanRunner()
for loan in loans:
    mortgage.add_loanpart(loan)

print('total loan %.2f euro' % mortgage.current_amount)
mortgage.step_all()


df = mortgage.to_dataframe()
df_agg = group_by_year(df, start_period)
print(df_agg[['amount', 'interest', 'payment', 'repayment', 'amount_end']])
