"""
tests related to the PaymentData class
"""

import pytest

from core import PaymentData

AM = 'amount'
IP = 'interest'
RP = 'repayment'

payment_fixture_data = {
    'reg1': {
        AM: 1000,
        IP: 10,
        RP: 20,
    },
    'reg2': {
        AM: 1000,
        IP: 50,
        RP: 50,
    },
    'reg3': {
        AM: 0.,
        IP: -5.,
        RP: -10.,
    },
}


@pytest.fixture(params=list(payment_fixture_data.values()),
                ids=list(payment_fixture_data.keys()))
def payment_fixture(request):
    """Fixture payment data will all attributes assigned"""
    payment_data = PaymentData()
    payment_data.amount_boy = request.param[AM]
    payment_data.interest = request.param[IP]
    payment_data.repayment = request.param[RP]
    return payment_data


def test_add_two_payments(payment_fixture):
    """Tests whether all parameters of two payments are added correctly"""

    # arrange
    payment2 = PaymentData()
    payment2.interest = 100.
    expected_interest = payment2.interest + payment_fixture.interest

    # act
    added = payment_fixture + payment2

    # assert
    assert added.interest == expected_interest


def test_payment_property(payment_fixture):
    """tests whether payment is the sum of interest and repayment"""

    assert payment_fixture.payment == \
        payment_fixture.interest + payment_fixture.repayment


def test_end_amount(payment_fixture):
    """tests whether amount end equals start minus repayment"""

    assert payment_fixture.amount_end == payment_fixture.amount_boy - \
        payment_fixture.repayment
