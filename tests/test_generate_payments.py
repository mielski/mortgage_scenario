"""
tests for the generate_payments generator and loanpart iterator
"""
from unittest.mock import MagicMock

import pytest

from core import PaymentData
from mortgage_scenarios.core import generate_payments, LoanPartIterator


def input_dict():
    yield {'amount': 100,
              'fv': 20,
              'rate': 0.001,
              'npers': 30,
           }
    yield {'amount': 200,
              'fv': 100,
              'rate': 0.001,
              'npers': 30,
           }


@pytest.mark.parametrize('payment_parameters', input_dict())
def test_generate_interest_only(payment_parameters):
    """
    tests that calling the generate_payments with current value == future value leads to a scheme without
    repayments
    """
    # arrange
    payment_parameters['fv'] = payment_parameters['amount']  # set to interest-only loan
    gen = generate_payments(**payment_parameters)

    # act
    result = next(gen)

    # assert
    assert result.amount == result.amount_end


@pytest.fixture(scope="function")
def lpi():
    """
    LoanPartIterator object with a MagicMock for the generator
    """
    lpi = LoanPartIterator(amount=1000., year_rate=0.01, periods=2)
    lpi._calculator = MagicMock(spec=generate_payments(0, 0, 1))
    lpi._calculator.__next__.return_value = PaymentData(0, 0, 0)
    return lpi


def test_lpi_next_gives_paymentdata(lpi):
    """
    given a LoanPartIterator, checks if the next function works as expected
    """
    # act
    result = next(lpi)

    # assert
    assert isinstance(result, PaymentData)


def test_lpi_next_update_internal_periods(lpi):
    """
    given a LoanPartIterator, checks if the next function updates the internal properties
    """
    # act
    result = next(lpi)

    # assert
    assert lpi.remaining_periods == 1
    assert lpi.current_amount == result.amount_end
