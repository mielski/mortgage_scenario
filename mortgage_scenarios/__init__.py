"""Top-level package for mortgage scenarios."""

__version__ = '0.1.0'

from .core import MortgageLoanRunner, LoanPartIterator  # noqa: F401
from .utils import get_monthly_rate  # noqa: F401
