"""
Types of DiffKemp results.

:author: Lukas Petr
"""

from enum import StrEnum


class DiffKempResultType(StrEnum):
    """Types of comparison results from DiffKemp analysis."""

    # Functions are semantically and syntactically equal.
    EQUAL_NO_DIFF = "equal (no diff)"
    # Functions are semantically equal but they do not have to be syntactically
    # equal.
    EQUAL = "equal"
    # Functions have semantic differences.
    NON_EQUAL = "non equal"
    # Analysis could not determine equality (e.g., the functions is only in one
    # version)
    UNKNOWN = "unknown"
    # Error occurred during analysis.
    ERROR = "error"


class ExpectedResultType(StrEnum):
    """Types of expected comparison results from DiffKemp analysis."""
    UNKNOWN = "unknown"
    EQUAL = "equal"
    NON_EQUAL = "non equal"


class ComparisonStatus(StrEnum):
    """Status of the comparison."""

    # Comparison failed due to an error.
    FAIL = "fail"
    # The comparison was successful.
    SUCCESS = "success"
    # No functions were located to be analyzed.
    NO_FUNCTIONS = "no-functions"


class OverallResult(StrEnum):
    """Overall verdict for comparison based on function results."""

    NON_EQUAL = "non equal"
    UNKNOWN = "unknown"
    EQUAL = "equal"
