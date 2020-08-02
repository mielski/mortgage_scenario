"""Main module"""
from copy import copy, deepcopy
from bisect import bisect

import pandas as pd
import numpy as np



PERIODS = 12 * 30

class Settings:
    tax_percentage = 0.3735
    fixed_rate = 1.7
    
    rates = {'Annuity': {'67': 1.75, '90': 1.95},
             'Interest-only': {'67': 1.95, '90': 2.15}
             }

class HouseSettings:
    woz_value = 550000.
    taxation_price = 631000.


def generate_payments(amount_boy, rate, npers, fv=0, fixed=0):
    """
    The heart of this module. This generator returns payment information
    over the lifetime of loan
    """
    
    payment = -np.pmt(rate, npers, amount_boy, -fv, 'end') + fixed
    for i in range(npers):
        
        interest = amount_boy*rate + fixed
        repayment = payment - interest
        amount_eoy = amount_boy - repayment
        result = dict(interest=interest, repayment=repayment,
                      amount_eoy=amount_eoy, payment=payment,
                      amount_boy=amount_boy)
        yield result
        amount_boy = amount_eoy
    
    interest = amount_boy*rate + fixed
    yield dict(interest=interest, repayment=repayment,
               amount_eoy=amount_eoy, payment=payment,
               amount_boy=amount_boy)

    
class PaymentData():
    """
    dataclass with yearly payment data of a loan
    
    has functionality to add data from other loans
    """
    _payment_attrs = {'interest', 'repayment', 'payment', 
                      'amount_boy', 'amount_eoy'}
    
    
    def __init__(self, data=None):
        
        self.interest = 0.
        self.repayment = 0.
        self.payment = 0.
        self.amount_boy = 0.
        self.amount_eoy = 0.
        
            
    def as_dict(self):
        
        return {attr: getattr(self, attr) for attr in self._payment_attrs}
        
        
    def __add__(self, other):
        
        if isinstance(other, int):
            return self
        
        out = copy(self)
        out += other
        return out
    
    def __radd__(self, other):
        return self.__add__(other)
    
    def __iadd__(self, other):
        
        if isinstance(other, PaymentData):
            for attr in self._payment_attrs:
                value = getattr(self, attr) + getattr(other, attr)
                setattr(self, attr, value)
        elif isinstance(other, dict):
            for attr in self._payment_attrs:
                value = getattr(self, attr) + other[attr]
                setattr(self, attr, value)
        elif isinstance(other, int):
            if other == 0:
                return self
            
        else:
            raise TypeError('cannot add input of type ' + str(other.__class__))
        
        return self
    
        
class LoanPart:
    """
    Representation of a Loanpart that is able to compute repayments
    and contains loan remaining period information
    """
    
    def __init__(self, amount, year_rate, periods, future=0, fixed=0):
        self.start_amount = amount
        self.n_periods = periods
        self.rate = get_monthly_rate(year_rate)
        self.future = future
        self.fixed = 0
        self.reset()

    
    @property
    def remaining_periods(self):
        return self.n_periods - self.current_period
    
    
    def initialize_calculator(self):
        self.calculator = generate_payments(self.current_amount,
                                           self.rate,
                                           self.n_periods,
                                           self.future,
                                           self.fixed)
        return self.calculator
    
    def reset(self):
        self.current_period = 0
        self.current_amount = self.start_amount
        self.initialize_calculator()
        
    
    def __iter__(self):
        return self
    
    def __next__(self):
        
        result = next(self.calculator)
        result['period'] = self.current_period
        result['remaining'] = self.remaining_periods
        
        self.current_amount = result['amount_eoy']
        self.current_period += 1
        
        return result
    
    def new_loanpart_with_rate(self, rate):
        """
        create a new LoanPart with the same status as the current loanpart
        (using the current amount and remaining periods), but with an
        updated interest rate
        """
        
        return LoanPart(self.current_amount, rate,
                        self.remaining_periods, self.future, self.fixed)

class MortgageLoanRunner:
    """
    class that contains a set of loanparts, can iterate over them and 
    return the total amount of interest and payments each period
    """
    
    def __init__(self):
        self.loanparts = []
        self.names = []
        self.data = []
        self.loanpart_active = []
        self.period = 0
        
        
    def add_loanpart(self, loanpart: LoanPart, name=None):
        
        if not isinstance(loanpart, LoanPart):
            raise TypeError("LoanPart instance expected for argument loanpart")

        self.loanparts.append(loanpart)
        self.names.append(name)
        self.loanpart_active.append(True)
        
        

    def step(self):
        
        any_loan_active = 0
        
        total_payment = PaymentData()
        for i_loan, loanpart in enumerate(self.loanparts):
            if loanpart.remaining_periods <= 0:
                continue
            any_loan_active = 1
            
            payment_info = next(loanpart)
            total_payment += payment_info
        
        if not any_loan_active:
            raise StopIteration('no more loans active')
        
        payment_dict = total_payment.as_dict()
        payment_dict['period'] = self.period
        self.period += 1
        self.data.append(payment_dict)
    
    def step_all(self):
        
        while True:
            try:
                self.step()
            except StopIteration:
                break
        
    
    @property
    def current_amount(self):
        return sum(x.current_amount for x in self.loanparts)
    
    @property
    def periods_remaining(self):
        return max(loan.remaining_periods for loan in self.loanparts)
    
    @staticmethod
    def _convert_data_to_dataframe(dataitem):
        """
        used to convert an item in self.data into a dataframe and to tweak
        its columns
        """
        
        df = pd.DataFrame(dataitem).set_index('period').drop(columns='remaining')
        return df
    
    def to_dataframe(self):
        df = pd.DataFrame(self.data).set_index('period')
        
        df = df[['amount_boy', 'payment', 'interest', 'repayment', 'amount_eoy']]
        return df
    
    def replace_loanpart_by_index(self, loanpart, index=None, name=None):
        """
        replaces one of the existing loanparts with a new one
        
        arguments
        loanpart: the new loanpart
        index: the index of the loanpart that is replaced
        name: the name of the loanpart that is replaced
        
        Replacement can be done by index or by name. One of these arguments
        should be provided. Providing None or two will raise an Exception
        """
        
        if name and index:
            raise ValueError('replace_loanpart required either name or index' \
                             ' but both are provided ')
        if index is None and name is None:
            raise ValueError('replace_loanpart required either name or index' + 
                             ' but none provided')
        if index is None:
            index = self.names.index(name)
        
        self.loanparts[index] = loanpart
    
    def replace_loanpart(self, old: LoanPart, new: LoanPart) -> None: 
        """
        replaces one of the loanparts in the internal list
        
        param old: the original loanpart. Its id will be used to locate
        it inside the list
        
        param new: the new loanpart that it is replaced with
        """
        index = self.loanparts.index(old)
        self.loanparts[index] = new
        
        

def calc_eigenwoning_forfait_tax():
    # monthy 
    
    return 0.006 * Settings.woz


class MortgageScenarioRunner:
    """
    returns the payments over time of a mortgage, using particular scenario
    events:
        
    - change of rent based on LTV
    - scheduled prepayments
    """
    
    def __init__(self, mortgage):
        
        # make a copy of the mortgage and loans, to avoid side effects
        self._mortgage = copy(mortgage)
        self._mortgage_loans = deepcopy(mortgage.loanparts)        
        if not len(mortgage.data) == 0:
            raise ValueError('mortgage input should not have started running')
            
        
        self._scenarios = {}



class mortgageScenario:
    pass

def get_monthly_rate(rate):
    """
    computes the interest amount for each month, given that the input rate is the
    yearly rate
    """
    
    growth_year = rate + 1
    growth_month = np.power(growth_year, 1./12)
    rate_month = growth_month - 1
    return rate_month


def classic(*loans):
    
    df_list = []
    for l in loans:
        df = pd.DataFrame((period for period in l)).set_index('period').\
            drop(columns='remaining')
        df_list.append(df)
    
    return sum(df_list)

def houseprice():
    return 640000.

def get_ltv_tranch(amount, houseprice):
    ltv_boundaries = (0.675, 0.9, 1.0)
    ltv_tranch_names = ('<67.5%', '67.5% - 90%', '90% - 100%', '>100%')
    ltv = amount / houseprice()
    ltv_index = bisect(ltv_boundaries, ltv)
    return (ltv_index, ltv_tranch_names[ltv_index])

    

if __name__ == "__main__":
    
    pd.options.display.precision = 2
    pd.options.display.float_format = '{:,.2f}'.format
    
    loan1 = LoanPart( 92500, 0.0215, PERIODS, future=92500, fixed=1.7)
    loan2 = LoanPart(150000, 0.0195, PERIODS, fixed=1.7)
    loan3 = LoanPart(144000, 0.0195, PERIODS, fixed=1.7)
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
        
        if mortgage.period in [10,20]:
            print('do repayment')
            events.append('repayment')
        
        eventlog.append(";".join(events))
        
    
    df = mortgage.to_dataframe()
    df['events'] = eventlog
    df['ltv'] = df['amount_boy'] / houseprice()
    
    print(df)

    
    