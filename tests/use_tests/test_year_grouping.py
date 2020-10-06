import pandas as pd
import pytest

from mortgage_scenarios.core import group_by_year


@pytest.fixture
def df_month_fixture():
    """fixture of monthy payment data with three columns"""
    periods = 24
    index = pd.RangeIndex(periods)
    columns = ['amount', 'repayment', 'amount_end']
    df_months = pd.DataFrame(index=index, columns=columns)
    df_months.amount = pd.RangeIndex(periods, 0, -1)
    df_months.amount *= 100  # [2400, 2300, 2200, ..., 200, 100]
    df_months.repayment = 100  # [100, 100, 100, ..., 100, 100]
    df_months.amount_end = df_months.amount - 100  # [2300, 2200, 2100, ..., 100,   0]
    return df_months


def test_group_by_year(df_month_fixture):
    """
    validate result of group_by_year based on
    artificial input dataframe

    dataset is a simple loan of 2400 euros where each month 100 is repaid.
    This makes is easy to formulate the data and expected output
    """

    columns = df_month_fixture.columns

    # set up the output data
    expected_data = {'amount': [2400, 2000, 800],
                     'repayment': [100, 100, 100],
                     'amount_end': [2000, 800, 0]}
    expected_df = pd.DataFrame(expected_data, columns=columns, index=[2020, 2021, 2022])

    # act
    actual_df = group_by_year(df_month_fixture, '2020-09')

    # assert
    pd.testing.assert_frame_equal(actual_df, expected_df, check_dtype=False)


def test_group_by_year_wrong_column(df_month_fixture):
    """
    asserts that group_by_year uses default raises KeyError
    if the input data contains a column that is not in the converstion list
    """

    new_columns = 'x'
    df_month_fixture['x'] = df_month_fixture.amount

    with pytest.raises(KeyError):
        group_by_year(df_month_fixture, '2020-09')

