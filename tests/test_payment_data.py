"""
tests related to the PaymentData class
"""

import pytest

from core import PaymentData

AM = 'amount_boy'
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
    payment_data = PaymentData(amount_boy=request.param[AM],
                               interest=request.param[IP],
                               repayment=request.param[RP])
    return payment_data

def test_add_two_payments(payment_fixture):
    """Tests whether all parameters of two payments are added correctly"""

    # arrange
    payment2 = PaymentData(interest=100, amount_boy=0, repayment=0)
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


def test_sum():
    """
    tests summation of three PaymentData instances
    """

    # arrange
    data1 = PaymentData(**payment_fixture_data['reg1'])
    data2 = PaymentData(**payment_fixture_data['reg2'])
    data3 = PaymentData(**payment_fixture_data['reg3'])

    # count amounts based in input data
    total_amount_expected = sum(payment_fixture_data[name]['amount_boy'] for name in ['reg1', 'reg2', 'reg3'])

    # act
    data_total = sum([data1, data2, data3])

    # assert
    assert data_total.amount_boy == total_amount_expected
