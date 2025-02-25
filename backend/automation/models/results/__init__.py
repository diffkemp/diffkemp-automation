"""
Package containing results representation.

:author: Lukas Petr
"""

from .results import Results
from .types import DiffKempResultType
from .versions import ResultsVersions, ResultVersion

__all__ = ["Results", "ResultsVersions", "ResultVersion", "DiffKempResultType"]
