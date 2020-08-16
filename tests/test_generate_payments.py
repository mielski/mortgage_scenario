"""
tests for the generate_payments generator
"""
import pytest

from mortgage_scenarios.core import generate_payments


def input_dict():
    yield {'amount_boy': 100,
              'fv': 20,
              'rate': 0.001,
              'npers': 30,
           }
    yield {'amount_boy': 200,
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
    payment_parameters['fv'] = payment_parameters['amount_boy']  # set to interest-only loan
    gen = generate_payments(**payment_parameters)

    # act
    result = next(gen)

    # assert
    assert result['amount_boy'] == result['amount_eoy']
