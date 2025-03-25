"""Testing ProjectVersions class."""
from typing import cast

from packaging.version import Version

from automation.models.projects.projects import ProjectsManager
from automation.models.projects.versions import ProjectVersions


def test_has_new_release_success(mocker):
    """Test that checking for new releases works if new release exists."""
    project = ProjectsManager.get("mbedtls")
    mocker.patch.object(project, "get_latest_compared_version",
                        return_value=Version("3.6.0"))
    assert isinstance(project, ProjectVersions)
    assert project.has_new_release() is True


def test_has_new_release_failure(mocker):
    """
    Test that checking for new releases works if new release does not exist.
    """
    project = ProjectsManager.get("mbedtls")
    mocker.patch.object(project, "get_latest_compared_version",
                        return_value=Version("150.6.0"))
    assert isinstance(project, ProjectVersions)
    assert project.has_new_release() is False


def test_get_github_latest_version():
    """Tests getting latest version from github works."""
    mbedtls = cast(ProjectVersions, ProjectsManager.get("mbedtls"))
    assert mbedtls.get_latest_release() is not None
    nettle = cast(ProjectVersions, ProjectsManager.get("nettle"))
    assert nettle.get_latest_release() is not None


def test_get_tags_to_compare(mocker):
    """Tests that getting tags to compare works."""
    project = cast(ProjectVersions, ProjectsManager.get("mbedtls"))
    mocker.patch.object(project, "get_latest_compared_version",
                        return_value=Version("3.5.2"))
    mocker.patch.object(project, "get_release_tags", return_value=[
        "v3.6.2", "v3.5.1", "v3.5.0", "v3.6.0", "v3.6.1", "v3.5.2",
    ])
    assert project.get_tags_to_compare() == [
        "v3.5.2", "v3.6.0", "v3.6.1", "v3.6.2"]

    project = cast(ProjectVersions, ProjectsManager.get("nettle"))
    mocker.patch.object(project, "get_latest_compared_version",
                        return_value=Version("3.9.1"))
    tags = project.get_tags_to_compare()
    assert len(tags) >= 3
    assert "nettle_3.9.1_release_20230601" in tags
    assert "nettle_3.10_release_20240616" in tags
    assert "nettle_3.10.1_release_20241230" in tags
    assert "nettle_3.10rc2" not in tags
    assert "nettle_3.10rc1" not in tags
