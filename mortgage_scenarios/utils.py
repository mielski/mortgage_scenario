import numpy as np


def get_monthly_rate(rate) -> float:
    """
    computes the monthy interest rate based on the yearly interest rate

    :param float rate: the yearly interest rate
    :return: the monthly interest rate

    This computation uses the 12th root on the growth factor
    """

    growth_year = rate + 1
    growth_month = np.power(growth_year, 1./12)
    rate_month = growth_month - 1
    return rate_month
