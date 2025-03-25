"""
Tests for results.

:author: Lukas Petr
"""
from automation.models.results import Results


def test_empty_results_get(mocker):
    """Testing getting results, when there are none."""
    mocker.patch("pathlib.Path.open", mocker.mock_open(read_data="\n"))
    r = Results()
    assert r.get_commit_results().get() == []
    assert r.get_version_results().get() == []


def test_empty_results_to_yaml(mocker):
    """Testing loading and saving results, when they are empty."""
    mocker.patch("pathlib.Path.open", mocker.mock_open(read_data="\n"))
    results = Results()
    commit_results = results.get_commit_results()
    version_results = results.get_commit_results()
    assert version_results.to_yaml() == []
    assert commit_results.to_yaml() == []
    assert results.to_yaml() == []
