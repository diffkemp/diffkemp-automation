"""
Utility file containing constants and functions.

:author: Lukas Petr
"""

from pathlib import Path

from appdirs import user_data_dir

BACKEND_DIR = Path(__file__).absolute().parent.parent
# Path to projects' configurations
CONFIGS_DIR = BACKEND_DIR / "automation" / "configs"

# Place where will be saved project repositories and results of comparison.
SITE_DATA_DIR = Path(user_data_dir("diffkemp-automation", "diffkemp"))
RESULTS_DIR = SITE_DATA_DIR / "results"
REPOS_DIR = SITE_DATA_DIR / "repos"
# Directory, where will be saved 'websites' for visualizing results.
VIEW_RESULTS_DIR = RESULTS_DIR / "view"

# File, where will be saved the latest compared version for each project.
LATEST_VERSION_PATH = RESULTS_DIR / "latest_versions.yml"
# File, where will be saved the results of comparison.
RESULTS_DB_PATH = RESULTS_DIR / "results.db"
