# <code-map>
# Generated definition map; @L is the exact declaration line.
# Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
# functions: record(mode)@L18; test_observed_fault_is_required_and_must_be_blocked(mode)@L39; test_write_failure_must_follow_valid_successful_target_observation()@L58
# variables: observed@L20; actual@L41; changed@L43; changed@L47; actual@L60
# parameters: mode@L18; mode@L39
# </code-map>

"""Jason Stys: fault-injection evidence must prove the intended actual collector fault."""

import copy

import pytest

from scripts.csharp_coverage_checks import validate_collector_fault


def record(mode):
    """Inert records model three distinct fault contracts, not actual .NET execution."""
    observed = {"exit_code": 0, "timeout": False, "option_rejected": False, "valid_target_observation": False}
    if mode == "invalid-option":
        observed["option_rejected"] = True
    elif mode == "unwritable-output":
        observed.update(exit_code=3, valid_target_observation=True, target_exit_code=0)
    else:
        observed.update(exit_code=-9, timeout=True)
    return {
        "fault": mode,
        "actual_collector": observed,
        "worker_result": {
            "tool_status": "completed",
            "checks": {"passed": 1, "failed": 0},
            "coverage": {"status": "blocked"},
        },
    }


@pytest.mark.parametrize("mode", ["invalid-option", "unwritable-output", "timeout"])
def test_observed_fault_is_required_and_must_be_blocked(mode):
    """Healthy output, missing actual fault, or measured coverage cannot satisfy a fault control."""
    actual = record(mode)
    validate_collector_fault(actual)
    changed = copy.deepcopy(actual)
    changed["worker_result"]["coverage"]["status"] = "measured"
    with pytest.raises(ValueError, match="falsely accepted"):
        validate_collector_fault(changed)
    changed = copy.deepcopy(actual)
    if mode == "invalid-option":
        changed["actual_collector"]["option_rejected"] = False
    elif mode == "unwritable-output":
        changed["actual_collector"]["exit_code"] = 0
    else:
        changed["actual_collector"]["timeout"] = False
    with pytest.raises(ValueError, match="not observed"):
        validate_collector_fault(changed)


def test_write_failure_must_follow_valid_successful_target_observation():
    """An unrelated collector/target launch failure cannot stand in for a report-write failure."""
    actual = record("unwritable-output")
    actual["actual_collector"]["valid_target_observation"] = False
    with pytest.raises(ValueError, match="Post-target"):
        validate_collector_fault(actual)
