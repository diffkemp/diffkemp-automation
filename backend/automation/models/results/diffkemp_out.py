"""
Module for working with DiffKemp output file.

:author: Lukas Petr
"""

from pathlib import Path
from typing import Any, Dict

import yaml


class DiffKempOutYaml:
    """Class for working with DiffKemp output file."""

    def __init__(self, results: Dict[str, Any]):
        self.results = results

    @classmethod
    def from_file(cls, path: Path) -> "DiffKempOutYaml":
        """Loads DiffKemp results from YAML file."""
        with path.open("r", encoding="utf-8") as file:
            results = yaml.safe_load(file)
        return cls(results)

    def get_differing(self) -> set[str]:
        """Returns names of differing functions."""
        differing = set()
        for result in self.results["results"]:
            differing.update([diff["function"] for diff in result["diffs"]])
        return differing

    def get_no_differing(self) -> int:
        """Returns number of differing functions."""
        return len(self.get_differing())

    def get_non_equal(self) -> set[str]:
        """Returns name of compared functions evaluated as non equal."""
        return {result["function"] for result in self.results["results"]}
