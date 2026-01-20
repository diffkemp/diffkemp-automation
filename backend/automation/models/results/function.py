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

    def to_yaml(self) -> dict:
        return {
            "name": self.name,
            "diffkemp_result": str(self.diffkemp_result),
            "expected_result": str(self.expected_result)
        }

    @classmethod
    def from_yaml(cls, result: dict) -> "FunctionResult":
        name = result["name"]
        diffkemp_result = result["diffkemp_result"]
        expected_result = result.get("expected_result", "unknown")
        return cls(
            name=name,
            diffkemp_result=DiffKempResultType(diffkemp_result),
            expected_result=ExpectedResultType(expected_result),
        )
