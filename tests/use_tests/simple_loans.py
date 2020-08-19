"""
use test of running a loan without further events
"""
import pytest
import mortgage_scenarios
from re import sub
from io import StringIO
import pandas as pd


def read_markdown_string(md_string: str) -> pd.DataFrame:
    """
    Converts a markdown string into a pandas dataframe.

    This utility function is used in tests to visualize the expected output
    and load this in the test setup

    operations:
    - trim | characters in each line
    - remove opening and trailing empty lines
    """

    md_string = sub(r'\|?\n\|?', r'\n', md_string)
    md_string = sub(r'[-:|]+\n', '', md_string, count=1)
    md_string = md_string.replace(" ", "")
    md_string = md_string[1:-1]
    return pd.read_csv(StringIO(md_string), sep="|", index_col=0)


@pytest.mark.slow
def test_vanilla_annuity():

    # arrange
    expected_md = """
|   period |   amount |   payment |   interest |   repayment |   amount_end |
|---------:|---------:|----------:|-----------:|------------:|-------------:|
|        0 | 100      |   34.0022 |  0.9999997 |     33.0022 | 66.9977      |
|        1 |  66.9977 |   34.0022 |  0.6699777 |     33.3322 | 33.6655       |
|        2 |  33.6655 |   34.0022 |  0.3366554 |     33.6655  |  7.10543e-15 |
"""

    amount = 100
    periods = 3
    rate = 0.126825
    loan = mortgage_scenarios.LoanPartIterator(amount, rate, periods)

    expected_df = read_markdown_string(expected_md)

    # act
    runner = mortgage_scenarios.MortgageLoanRunner()
    runner.add_loanpart(loan)
    runner.step_all()
    df = runner.to_dataframe()

    # assert
    pd.testing.assert_frame_equal(df, expected_df)
