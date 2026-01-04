"""
Module representing results of projects' comparison.

:author: Lukas Petr
"""

import logging
from typing import Union

from .commits import ResultCommit
from .versions import ResultVersion

logger = logging.getLogger(__name__)

ResultSubType = Union[ResultVersion, ResultCommit]
