"""
Comparator of projects.

:author: Lukas Petr
"""

import argparse
import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Any, List, Tuple

import yaml
from git import Optional

from .models.projects import ProjectsManager, ProjectVersions
from .models.results import Results, ResultsVersions
from .utils import REPOS_DIR, VIEW_RESULTS_DIR

logger = logging.getLogger(__name__)
# Paths to repos in container
C_REPO_PATH = "/repos"


class ComparatorError(Exception):
    """Base exception for Comparator errors."""

    pass


class Comparator:
    """
    Comparator of projects.

    Runs comparison in a Podman container. Uses context manager
    to ensure proper cleanup.

    Usage:
        with Comparator() as comparator:
            comparator.compare_projects_tags(projects_tags)
    """

    def __init__(self) -> None:
        """
        Initialize comparator and launch container.

        :param projects_tags: List of tuples (project, tags[]).
        """
        self.container_id: Optional[str] = None
        self.diffkemp_sha: Optional[str] = None

        try:
            self.container_id = self._launch_container()
            self._build_diffkemp()
            self.diffkemp_sha = self._get_diffkemp_sha()
        except Exception as e:
            self.cleanup()
            raise ComparatorError("Failed to initialize comparator") from e

    def _launch_container(self) -> str:
        """
        Launch container.

        :return: Container ID.
        """
        logger.debug("Launching container")
        try:
            container_id = subprocess.check_output(
                [
                    "podman",
                    "run",
                    "-di",
                    "--rm",
                    "-v",
                    f"{REPOS_DIR}:{C_REPO_PATH}:O",
                    "--ulimit",
                    "nofile=65536:65536",
                    "diffkemp-automation",
                ],
                text=True,
            ).strip()
        except Exception as e:
            raise ComparatorError(
                f"It was not possible to start a container: {e}"
            ) from e
        logger.debug(f"Container {container_id} is running")
        return container_id

    def run_cmd(self, command: List[str], description: str = "") -> None:
        """
        Run command in the container.

        :param command: Command which should be run in the container.
        :param description: Description of the command, used for logging.
        """
        if self.container_id is None:
            raise ComparatorError("The container is not running")

        cmd = ["podman", "exec", self.container_id]
        cmd.extend(command)
        if not logger.isEnabledFor(logging.DEBUG):
            subprocess.check_call(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return

        # If logger is set to DEBUG level log the stdout and stderr
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.stdout:
            logger.debug(f"{description} stdout: {result.stdout}")
        if result.stderr:
            logger.debug(f"{description} stderr: {result.stderr}")

        result.check_returncode()

    def _build_diffkemp(self) -> None:
        if self.container_id is None:
            return

        logger.debug("Building DiffKemp")
        self.run_cmd(["/runner/build_diffkemp.sh"], "Build")
        logger.debug("DiffKemp is built")

    def _get_diffkemp_sha(self) -> str:
        if self.container_id is None:
            return ""

        return subprocess.check_output(
            ["podman", "exec", self.container_id,
             "/runner/get_diffkemp_sha.sh"],
            text=True,
        ).strip()

    def __enter__(self) -> "Comparator":
        return self

    def __exit__(self, *_: Any) -> None:
        self.cleanup()

    def cleanup(self) -> None:
        if self.container_id is None:
            return
        logger.debug("Stopping container")
        subprocess.check_call(
            ["podman", "kill", self.container_id],
            stderr=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
        )
        self.container_id = None

    def compare_projects_tags(
        self,
        projects_tags: List[Tuple[ProjectVersions, List[str]]],
    ) -> None:
        """
        Compare multiple projects and their tags.

        :param projects_tags: List of (project, tags) tuples.
        """
        logger.info(f"Comparing {len(projects_tags)} projects")

        for project, tags in projects_tags:
            self._compare_project_tags(project, tags)
            project.set_latest_compared_tag(tags[-1])

        self._create_view_files_for_versions()
        self._update_tag_results(projects_tags)

        logger.info("Comparison completed successfully")

    def _create_view_files_for_versions(self) -> None:
        """
        Create view files for all compared versions.
        """
        if self.container_id is None:
            return

        logger.debug("Creating view directories")
        self.run_cmd(
            ["/runner/version_comparison/build_view_files.sh"],
            "Build view files"
        )
        logger.debug("View directories are created")

    def _compare_project_tags(
        self,
        project: ProjectVersions,
        tags: List[str],
    ) -> None:
        """
        Compares one project and multiple tags in the container.

        :param project: Project to compare.
        :param tags: List of tags to compare.
        """
        if self.container_id is None:
            return

        logging.debug(f"Fetching ({', '.join(tags)}) in {project.name}")
        project.fetch_tags()

        logging.debug(f"Comparing ({', '.join(tags)}) in {project.name}")

        # Save config to container.
        _, tmp_filename = tempfile.mkstemp(text=True)
        config = project.get_config_for_analysis(tags)
        with open(tmp_filename, "w", encoding="utf-8") as file:
            print(yaml.safe_dump(config), file=file)
        subprocess.check_call(
            ["podman", "cp", tmp_filename, f"{self.container_id}:config.yml"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        # Run comparison
        self.run_cmd(
            ["/runner/version_comparison/run_cmp.sh", project.config_name],
            "Comparison"
        )

    def _update_tag_results(
        self,
        projects_tags: List[Tuple[ProjectVersions, List[str]]],
    ) -> None:
        """Save comparison results from container to disk."""
        if self.diffkemp_sha is None:
            return

        logger.debug("Saving results")

        results = Results()

        # For each project:
        # - saves view directories to disk and
        # - updates results with results of the version
        with tempfile.TemporaryDirectory() as tmp_dirname:
            result_file = Path(tmp_dirname) / "results.yml"

            for project, tags in projects_tags:
                config_name = project.config_name
                output_dir = (
                    VIEW_RESULTS_DIR / self.diffkemp_sha / project.config_name
                )

                output_dir.mkdir(parents=True, exist_ok=True)
                # Copy view files
                subprocess.check_call(
                    [
                        "podman",
                        "cp",
                        f"{self.container_id}:/version-view/{config_name}/.",
                        str(output_dir),
                    ],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                # Copy results file
                subprocess.check_call(
                    [
                        "podman",
                        "cp",
                        f"{self.container_id}:"
                        f"/version-output/{config_name}/results.yml",
                        result_file,
                    ],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                # Load results
                results.extend(
                    ResultsVersions.from_analyzer_results(
                        name=project.name,
                        config_file_name=project.config_name,
                        diffkemp_sha=self.diffkemp_sha,
                        path=result_file,
                    )
                )
                project.set_latest_compared_tag(tags[-1])
        # Updating total results
        results.save()

    def __del__(self) -> None:
        self.cleanup()


def compare_new() -> None:
    """Check for new project releases and compare them."""

    def init_amount_checker(amount_str: str) -> int:
        try:
            amount = int(amount_str)
        except Exception:
            raise argparse.ArgumentTypeError(f"{amount_str} is not a number")
        if amount < 2:
            raise argparse.ArgumentTypeError(
                "The initial amount must be greater than 2"
            )
        return amount

    parser = argparse.ArgumentParser(
        prog="Project versions comparator",
        description=(
            "Checks if new releases of projects are available and "
            "compares them"
        ),
    )
    parser.add_argument(
        "--projects",
        action="extend",
        nargs="*",
        type=str,
        help="List of projects to compare",
    )
    parser.add_argument(
        "--init-amount",
        default=3,
        type=init_amount_checker,
        help="Initial amount of version to compare (>=2)",
    )
    parser.add_argument("-v", "--verbose", action="count", default=0)

    args = parser.parse_args()
    log_levels = {
        0: logging.ERROR,
        1: logging.INFO,
    }
    logging.basicConfig(level=log_levels.get(args.verbose, logging.DEBUG))

    projects_tags = ProjectsManager.get_projects_tags_for_comparison(
        projects=args.projects,
        init_amount=args.init_amount,
    )

    if len(projects_tags) == 0:
        logger.info("No new projects to compare")
        return

    logger.info(f"Found {len(projects_tags)} projects with new releases")

    try:
        with Comparator() as comparator:
            comparator.compare_projects_tags(projects_tags)
    except ComparatorError as e:
        logger.error(f"Comparison failed: {e}")
    except Exception as e:
        logger.error(f"Unexpected error occurred during comparison: {e}")
