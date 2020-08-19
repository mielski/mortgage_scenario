"""
tests related to the PaymentData class
"""

import pytest

from mortgage_scenarios.core import PaymentData

AM = 'amount'
IP = 'interest'
RP = 'repayment'

payment_fixture_data = {
    'item1': {
        AM: 1000,
        IP: 10,
        RP: 20,
    },
    'item2': {
        AM: 1000,
        IP: 50,
        RP: 50,
    },
    'item3': {
        AM: 0.,
        IP: -5.,
        RP: -10.,
    },
}


@pytest.fixture(params=list(payment_fixture_data.values()),
                ids=list(payment_fixture_data.keys()))
def payment_fixture(request):
    """Fixture payment data will all attributes assigned"""
    payment_data = PaymentData(amount=request.param[AM],
                               interest=request.param[IP],
                               repayment=request.param[RP])
    return payment_data


def test_add_two_payments(payment_fixture):
    """Tests whether all parameters of two payments are added correctly"""

    # arrange
    payment2 = PaymentData(interest=100, amount=0, repayment=0)
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

    assert payment_fixture.amount_end == payment_fixture.amount - \
           payment_fixture.repayment


def test__check_dict_keys_regular(payment_fixture):
    """tests whether _check_dict_keys returns positive for
    given dictionary with variation in keys"""

    dictionary = payment_fixture_data['item1']
    # act
    assert payment_fixture._check_dict_keys(dictionary) is True


def test__check_dict_keys__regular_plus_property_items(payment_fixture):
    """
    dictionaries that contain also keys amount_end or payment
    should also pass
    """

    # arrange
    dictionary = payment_fixture_data['item1'].copy()
    dictionary.update(payment=None, amount_end=None)

    # act
    assert payment_fixture._check_dict_keys(dictionary) is True


def test__check_dict_keys_other_keys_rejected(payment_fixture):
    """
    Checks that a dictionary that contains other keys is rejected
    """
    # arrange
    dictionary = payment_fixture_data['item1'].copy()
    dictionary.update(a=None)  # key a is not accepted

    # act
    assert payment_fixture._check_dict_keys(dictionary) is False


def test__check_dict_keys_missing_keys_rejected(payment_fixture):
    """any input keys missing is rejected"""

    # arrange
    dictionary = payment_fixture_data['item1'].copy()
    del dictionary['amount']  # remove one if the entries

    # act
    assert payment_fixture._check_dict_keys(dictionary) is False


def test_as_dict():
    """simple test for _as_dict"""

    # arrange
    sut = PaymentData(amount=2, interest=1, repayment=2)
    expected_dict = {'amount': 2, 'interest': 1, 'repayment': 2,
                     'payment': 3, 'amount_end': 0}
    # act
    payment_dict = sut.as_dict()

    # assert
    assert payment_dict == expected_dict


def test_sum():
    """
    tests summation of three PaymentData instances
    """

    # arrange
    data1 = PaymentData(**payment_fixture_data['item1'])
    data2 = PaymentData(**payment_fixture_data['item2'])
    data3 = PaymentData(**payment_fixture_data['item3'])

    # count amounts based in input data
    total_amount_expected = sum(payment_fixture_data[name]['amount']
                                for name in ['item1', 'item2', 'item3'])

    # act
    data_total = sum([data1, data2, data3])

    # assert
    assert data_total.amount == total_amount_expected
