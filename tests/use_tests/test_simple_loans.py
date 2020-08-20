"""
use test with LoanRunner of one or two loans, without additional events such as
prepayments or interest changes during course of mortgage
"""
from io import StringIO
from re import sub

import pandas as pd

import mortgage_scenarios


def _assert_loan_data_equal(expected_md, loan):
    """
    main assertion script for use cases

    runs the loan and tests whether the output data
    compares to the data stored on the markdown string
    """

    runner = mortgage_scenarios.MortgageLoanRunner()
    runner.add_loanpart(loan)
    runner.step_all()

    expected_df = read_markdown_string(expected_md)
    df = runner.to_dataframe()

    pd.testing.assert_frame_equal(df, expected_df)


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


def test_annuity():
    """
    use test of an annuity loan.
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

    _assert_loan_data_equal(expected_md, loan)


def test_annuity_yearly():
    """
    use test of an annuity loan with param yearly=True.
    """

    expected_md = """
|   period |    amount |   payment |   interest |   repayment |   amount_end |
|---------:|----------:|----------:|-----------:|------------:|-------------:|
|        0 | 100       |   8.37833 | 0.0829538  |     8.29538 | 91.7046      |
|        1 |  91.7046  |   8.37833 | 0.0760725  |     8.30226 | 83.4024      |
|        2 |  83.4024  |   8.37833 | 0.0691854  |     8.30915 | 75.0932      |
|        3 |  75.0932  |   8.37833 | 0.0622927  |     8.31604 | 66.7772      |
|        4 |  66.7772  |   8.37833 | 0.0553942  |     8.32294 | 58.4542      |
|        5 |  58.4542  |   8.37833 | 0.04849    |     8.32984 | 50.1244      |
|        6 |  50.1244  |   8.37833 | 0.0415801  |     8.33675 | 41.7876      |
|        7 |  41.7876  |   8.37833 | 0.0346644  |     8.34367 | 33.444       |
|        8 |  33.444   |   8.37833 | 0.027743   |     8.35059 | 25.0934      |
|        9 |  25.0934  |   8.37833 | 0.0208159  |     8.35752 | 16.7358      |
|       10 |  16.7358  |   8.37833 | 0.013883   |     8.36445 |  8.37139     |
|       11 |   8.37139 |   8.37833 | 0.00694439 |     8.37139 |  1.61648e-13 |
"""

    amount = 100
    periods = 1
    rate = 0.01
    loan = mortgage_scenarios.LoanPartIterator(amount, rate, periods, yearly=True)

    _assert_loan_data_equal(expected_md, loan)


def test_interest_only():
    """
    use test of an interest-only loan.
    """

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

    _assert_loan_data_equal(expected_md, loan)


def test_annuity_with_fixed_rate():
    """
    use test of the previous annuity loan, including a fixed amount.
    """

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

    _assert_loan_data_equal(expected_md, loan)
