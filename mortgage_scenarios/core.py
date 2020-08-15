"""Main module"""
from copy import copy, deepcopy
from dataclasses import dataclass

import pandas as pd
import numpy as np

from utils import get_monthly_rate


def generate_payments(amount_boy, rate, npers, fv=0., fixed=0.):
    """
    The heart of this module. This generator yields payment information for an annuity.
    It yields payment information for each period of the loan
    plus 1 extra on after all payments are done

    :param float amount_boy: the amount of the loan
    :param float rate: the interest rate computed each period
    :param int npers: the number of periods
    :param float fv: the future value (after the payments are done)
    :param float fixed: a fixed payment amount done each period (default is 0)

    This is a wrapper around the np.pmt function with some additional
    information returns for each period:
    - interest paid
    - repayment done
    - loan amount before and after the payment
    - total payment done (= payment + interest)
    """
    if npers < 1:
        raise ValueError('npers should be a positive number, "{}" provided'.format(npers))
    # TODO: pmt is depreciated, use replacement function
    # noinspection PyTypeChecker
    payment = -np.pmt(rate, npers, amount_boy, -fv, when='end') + fixed
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
    # noinspection PyUnboundLocalVariable
    yield dict(interest=interest, repayment=repayment,
               amount_eoy=amount_eoy, payment=payment,
               amount_boy=amount_boy)


@dataclass
class PaymentData:
    """
    dataclass with yearly payment data of a loan

    has functionality to add data from other loans
    """

    interest: float
    repayment: float
    amount_boy: float

    _payment_attrs = {'interest', 'repayment', 'amount_boy', 'payment', 'amount_end'}

    @property
    def payment(self):
        """payment is the sum of interest and repayment"""
        return self.interest + self.repayment

    @property
    def amount_end(self):
        """amount after repayment"""
        return self.amount_boy - self.repayment

    def as_dict(self):

        return {attr: getattr(self, attr) for attr in self._payment_attrs}

    def __add__(self, other):

        if isinstance(other, int):
            if other == 0:
                return self

        out = copy(self)
        out += other
        return out

    def __radd__(self, other):
        return self.__add__(other)

    def __iadd__(self, other):

        if isinstance(other, PaymentData):
            for attr in self.__dict__:
                value = getattr(self, attr) + getattr(other, attr)
                setattr(self, attr, value)
        elif isinstance(other, dict):
            for attr in self.__dict__:
                value = getattr(self, attr) + other[attr]
                setattr(self, attr, value)
        elif isinstance(other, int):
            if other == 0:
                return self

        else:
            raise TypeError('cannot add input of type ' + str(other.__class__))

        return self


class LoanPartIterator:
    """
    Generates payments of a loan and stores remaining amount and period internally

    It is an enhanced version of the generate_payments generator.
    Iteration returns the values from the generator,
    but also the period number and remaining periods
    Also, properties such as current amount are stored in the instance
    """

    def __init__(self, amount, year_rate, periods, future=0., fixed=0.):
        self.start_amount = amount
        self.n_periods = periods
        self.rate = get_monthly_rate(year_rate)
        self.future = future
        self.fixed = fixed
        self._calculator = None

        self.reset()

    # noinspection PyAttributeOutsideInit
    def reset(self):
        self.current_period = 0
        self.current_amount = self.start_amount
        self.initialize_calculator()

    @property
    def remaining_periods(self):
        """the remaining periods to be paid in the loan"""
        return self.n_periods - self.current_period

    def initialize_calculator(self):
        """
        sets the underlying payment generator

        Typically used when resetting or initializing the instance
        """
        self._calculator = generate_payments(self.current_amount,
                                             self.rate,
                                             self.n_periods,
                                             self.future,
                                             self.fixed)
        return self._calculator

    def __iter__(self):
        return self

    def __next__(self):

        result = next(self._calculator)
        result['period'] = self.current_period
        result['remaining'] = self.remaining_periods

        self.current_amount = result['amount_eoy']
        self.current_period += 1

        return result

    def new_loanpart_with_rate(self, rate):
        """
        returns a new LoanPartIterator with the same status as the current loanpart
        (using the current amount and remaining periods), but with an
        updated interest rate
        """

        return LoanPartIterator(self.current_amount, rate,
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

    def add_loanpart(self, loanpart: LoanPartIterator, name=None):

        if not isinstance(loanpart, LoanPartIterator):
            raise TypeError("LoanPartIterator instance expected for argument loanpart")

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
            raise ValueError('replace_loanpart required either name or index' +
                             ' but both are provided ')
        if index is None and name is None:
            raise ValueError('replace_loanpart required either name or index' +
                             ' but none provided')
        if index is None:
            index = self.names.index(name)

        self.loanparts[index] = loanpart

    def replace_loanpart(self, old: LoanPartIterator, new: LoanPartIterator) -> None:
        """
        replaces one of the loanparts in the internal list

        param old: the original loanpart. Its id will be used to locate
        it inside the list

        param new: the new loanpart that it is replaced with
        """
        index = self.loanparts.index(old)
        self.loanparts[index] = new


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
