"""
tests related to the PaymentData class
"""

import pytest

from core import PaymentData


@pytest.fixture()
def simple_payment():
    """Fixture payment data will all attributes assigned"""
    payment_data = PaymentData()
    payment_data.amount_boy = 1000.
    payment_data.interest = 10.
    payment_data.repayment = 20
    return payment_data


def test_add_two_payments(simple_payment):
    """Tests whether all parameters of two payments are added correctly"""

    # arrange
    payment2 = PaymentData()
    payment2.interest = 100.
    expected_interest = payment2.interest + simple_payment.interest

    # act
    added = simple_payment + payment2

    # assert
    assert added.interest == expected_interest


def test_payment_property(simple_payment):
    """tests whether payment is the sum of interest and repayment"""

    assert simple_payment.payment == simple_payment.interest + simple_payment.repayment


def test_end_amount(simple_payment):
    """tests whether amount end equals start minus repayment"""

    assert simple_payment.amount_end == simple_payment.amount_boy - simple_payment.repayment
