import pandas as pd

from mortgage_scenarios.core import group_by_year


def test_group_by_year():
    """
    validate result of group_by_year based on
    artificial input dataframe

    dataset is a simple loan of 2400 euros where each month 100 is repaid.
    This makes is easy to formulate the data and expected output
    """

    # arrange
    periods = 24
    index = pd.RangeIndex(periods)
    columns = ['amount', 'repayment', 'amount_end']
    df_in = pd.DataFrame(index=index, columns=columns)

    df_in.amount = pd.RangeIndex(periods, 0, -1)
    df_in.amount *= 100  # [2400, 2300, 2200, ..., 200, 100]
    df_in.repayment = 100  # [100, 100, 100, ..., 100, 100]
    df_in.amount_end = df_in.amount - 100  # [2300, 2200, 2100, ..., 100,   0]

    # set up the output data
    expected_data = {'amount': [2400, 2000, 800],
                     'repayment': [400, 1200, 800],
                     'amount_end': [2000, 800, 0]}
    expected_df = pd.DataFrame(expected_data, columns=columns, index=[2020, 2021, 2022])

    # act
    actual_df = group_by_year(df_in, '2020-09')

    # assert
    pd.testing.assert_frame_equal(actual_df, expected_df, check_dtype=False)
