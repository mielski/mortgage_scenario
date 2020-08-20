"""
use test with LoanRunner of one or two loans, without additional events such as
prepayments or interest changes during course of mortgage
"""
from io import StringIO
from re import sub

import pandas as pd

import mortgage_scenarios


def read_markdown_string(md_string: str) -> pd.DataFrame:
    """
    Converts a markdown string into a pandas dataframe.

    This utility function is used in tests to visualize the expected output
    and load this in the test setup

    operations:
    - trim | characters in each line
    - remove opening and trailing empty lines
    """

    md_string = md_string.replace(" ", "")
    md_string = sub(r'\|?\n\|?', r'\n', md_string)
    md_string = sub(r'[-:|]+\n', '', md_string, count=1)
    md_string = md_string[1:-1]
    return pd.read_csv(StringIO(md_string), sep="|", index_col=0)


def test_vanilla_annuity():
    """
    use test of an annuity loan. Given loan specification, the loan is iterated
    and converted into a dataframe. This dataframe is compared to the expected values
    """

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
    rate = 0.01
    loan = mortgage_scenarios.LoanPartIterator(amount, rate, periods)

    expected_df = read_markdown_string(expected_md)

    # act
    runner = mortgage_scenarios.MortgageLoanRunner()
    runner.add_loanpart(loan)
    runner.step_all()
    df = runner.to_dataframe()

    # assert
    pd.testing.assert_frame_equal(df, expected_df)


def test_vanilla_interest_only():
    """
    use test of an interest-only loan.
    Given loan specification, the loan is iterated and converted into a dataframe.
    This dataframe is compared to the expected values
    """

    # arrange
    expected_md = """
|   period |   amount |   payment |   interest |   repayment |   amount_end |
|---------:|---------:|----------:|-----------:|------------:|-------------:|
|        0 | 100.     | 0.9999997 |  0.9999997 | 0.0         | 100.         |
|        1 | 100.     | 0.9999997 |  0.9999997 | 0.0         | 100.         |
|        2 | 100.     | 0.9999997 |  0.9999997 | 0.0         | 100.         |
    """

    amount = 100
    periods = 3
    rate = 0.01
    fv = 100
    loan = mortgage_scenarios.LoanPartIterator(amount, rate, periods, fv)

    expected_df = read_markdown_string(expected_md)

    # act
    runner = mortgage_scenarios.MortgageLoanRunner()
    runner.add_loanpart(loan)
    runner.step_all()
    df = runner.to_dataframe()

    # assert
    pd.testing.assert_frame_equal(df, expected_df)


def test_annuity_plus_fixed_rate():
    """
    use test of the previous annuity loan, including a fixed amount.
    Given loan specification, the loan is iterated and converted into a dataframe.
    This dataframe is compared to the expected values
    """

    # arrange
    expected_md = """
|   period |   amount |   payment |   interest |   repayment |   amount_end |
|---------:|---------:|----------:|-----------:|------------:|-------------:|
|        0 | 100      |   36.0022 |  2.9999997 |     33.0022 | 66.9977      |
|        1 |  66.9977 |   36.0022 |  2.6699777 |     33.3322 | 33.6655      |
|        2 |  33.6655 |   36.0022 |  2.3366554 |     33.6655 |  7.10543e-15 |
    """

    amount = 100
    periods = 3
    rate = 0.01
    fixed = 2
    loan = mortgage_scenarios.LoanPartIterator(amount, rate, periods, fixed=fixed)

    expected_df = read_markdown_string(expected_md)

    # act
    runner = mortgage_scenarios.MortgageLoanRunner()
    runner.add_loanpart(loan)
    runner.step_all()
    df = runner.to_dataframe()

    # assert
    pd.testing.assert_frame_equal(df, expected_df)
