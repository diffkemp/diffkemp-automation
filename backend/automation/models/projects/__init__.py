"""
Package containing projects representation.

:author: Lukas Petr
"""

from .project import BaseProject
from .projects import ProjectsManager
from .versions import ProjectVersions

__all__ = ["ProjectsManager", "ProjectVersions", "BaseProject"]
