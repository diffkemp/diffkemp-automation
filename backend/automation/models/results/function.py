"""
Result of function.

:author: Lukas Petr
"""

from typing import Optional

from .types import DiffKempResultType, ExpectedResultType


class FunctionResult:
    """Represents the comparison result for a single function."""

    def __init__(
        self,
        name: str,
        diffkemp_result: DiffKempResultType,
        expected_result: ExpectedResultType = ExpectedResultType.UNKNOWN,
    ) -> None:
        self.name: str = name
        self.diffkemp_result: DiffKempResultType = diffkemp_result
        self.expected_result: Optional[ExpectedResultType] = expected_result
        self.expected_result_changed_by: Optional[str] = None

    def set_expected_result(self, result: ExpectedResultType) -> None:
        self.expected_result = result
