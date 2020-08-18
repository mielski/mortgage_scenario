from bisect import bisect

import pandas as pd

from mortgage_scenarios import MortgageLoanRunner, LoanPartIterator

houseprice = 62000

def get_ltv_tranch(amount, houseprice):
    ltv_boundaries = (0.675, 0.9, 1.0)
    ltv_tranch_names = ('<67.5%', '67.5% - 90%', '90% - 100%', '>100%')
    ltv = amount / houseprice
    ltv_index = bisect(ltv_boundaries, ltv)
    return ltv_index, ltv_tranch_names[ltv_index]

PERIODS = 30

pd.options.display.precision = 2
pd.options.display.float_format = '{:,.2f}'.format

loan1 = LoanPartIterator(92500, 0.0215, PERIODS, future=92500, fixed=1.7)
loan2 = LoanPartIterator(150000, 0.0195, PERIODS, fixed=1.7)
loan3 = LoanPartIterator(144000, 0.0195, PERIODS, fixed=1.7)
loans = [loan1, loan2, loan3]

# ----

mortgage = MortgageLoanRunner()
for loan in loans:
    mortgage.add_loanpart(loan)

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
    if new_ltv != ltv_info and new_ltv[0] == 0:
        events.append('ltv < 67.5%')
        mortgage.replace_loanpart(loan1, loan1.new_loanpart_with_rate(0.019))
        mortgage.replace_loanpart(loan2, loan2.new_loanpart_with_rate(0.0175))
        mortgage.replace_loanpart(loan3, loan3.new_loanpart_with_rate(0.0175))
        ltv_info = new_ltv

    # repayment check

    if mortgage.period in [10, 20]:
        print('do repayment')
        events.append('repayment')

    eventlog.append(";".join(events))

df = mortgage.to_dataframe()
df['events'] = eventlog
df['ltv'] = df['amount'] / houseprice

print(df)

