"""
Result of function.

:author: Lukas Petr
"""

from .types import DiffKempResultType


class FunctionResult:
    """Represents the comparison result for a single function."""

    def __init__(self, name: str, diffkemp_result: DiffKempResultType):
        self.name: str = name
        self.diffkemp_result: DiffKempResultType = diffkemp_result

    def to_yaml(self) -> dict:
        return {
            "name": self.name,
            "diffkemp_result": str(self.diffkemp_result),
        }

    @classmethod
    def from_yaml(cls, result: dict) -> "FunctionResult":
        name = result["name"]
        diffkemp_result = result["diffkemp_result"]
        return cls(
            name=name,
            diffkemp_result=DiffKempResultType(diffkemp_result),
        )
