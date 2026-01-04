"""
Tests for commit results.

:author: Lukas Petr
"""

from pathlib import Path

from automation.models.results.commits import ResultCommit, ResultsCommits
from automation.models.results.types import DiffKempResultType


def test_result_from_analyzer1():
    """Tests parsing results from tool for commit comparison output for
    specific commit."""
    analyzer_result = {
        "confident": True,
        "empty": 0,
        "eq": 1,
        "err": 0,
        "functions": {
            "check_ctx_access": "neq",
            "check_packet_access": "eq",
        },
        "neq": 1,
        "no_functions": 2,
        "unk": 0,
        "verdict": "not equal"
    }
    result = ResultCommit.from_analyzer_results(
        "bpf-next", "bpf-next", "201b62ccc83153d2925d310a2afe762905e0c455",
        "ffe6d594d0973dc4d90d15090ef4119b34467ff8", analyzer_result)
    assert result.all_diffs_matched is True
    assert result.equal == 1
    assert result.non_equal == 1
    assert len(result.functions) == 2
    assert "check_ctx_access" in result.functions
    assert "check_packet_access" in result.functions
    assert (result.functions["check_ctx_access"].diffkemp_result
            == DiffKempResultType.NON_EQUAL)
    assert (result.functions["check_packet_access"].diffkemp_result
            == DiffKempResultType.EQUAL)
    assert result.get_diffkemp_verdict() == "non equal"


def test_result_from_analyzer2():
    analyzer_result = {
        "confident": True,
        "empty": 0,
        "eq": 0,
        "err": 0,
        "functions": {
            "check_ctx_access": "unk",
            "check_packet_access": "unk",
        },
        "neq": 0,
        "no_functions": 2,
        "unk": 2,
        "verdict": "equal"
    }
    result = ResultCommit.from_analyzer_results(
        "bpf-next", "bpf-next", "201b62ccc83153d2925d310a2afe762905e0c455",
        "ffe6d594d0973dc4d90d15090ef4119b34467ff8", analyzer_result)
    assert result.all_diffs_matched is True
    assert result.unknown == 2
    assert len(result.functions) == 2
    assert "check_ctx_access" in result.functions
    assert "check_packet_access" in result.functions
    assert (result.functions["check_ctx_access"].diffkemp_result
            == DiffKempResultType.UNKNOWN)
    assert (result.functions["check_packet_access"].diffkemp_result
            == DiffKempResultType.UNKNOWN)
    assert result.get_diffkemp_verdict() == "unknown"


def test_results_from_analyzer(mocker):
    """Tests parsing results from tool for commit comparison output for
    multiple commits."""
    file_data = """
09206af69c5238909af208b3f46a4aa7997ac0e1:
  confident: true
  empty: 0
  eq: 0
  err: 0
  functions:
    __bpf_dynptr_read: unk
    __bpf_dynptr_write: unk
  neq: 0
  no_functions: 2
  unk: 2
  verdict: equal
201b62ccc83153d2925d310a2afe762905e0c455:
  confident: true
  empty: 0
  eq: 1
  err: 0
  functions:
    check_ctx_access: neq
    check_packet_access: eq
  neq: 1
  no_functions: 2
  unk: 0
  verdict: not equal
"""
    mocker.patch("pathlib.Path.open", mocker.mock_open(read_data=file_data))
    results_list = ResultsCommits.from_analyzer_results(
        "bpf-next", "bpf-next", "ffe6d594d0973dc4d90d15090ef4119b34467ff8",
        Path("results.yml"))
    assert len(results_list) == 2
    assert set(map(lambda r: r.commit, results_list)) == {
        "09206af69c5238909af208b3f46a4aa7997ac0e1",
        "201b62ccc83153d2925d310a2afe762905e0c455"}
