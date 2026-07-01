"""M1b tests — stateful domains: healthy trajectories validate, call-changing faults break state,
replay is deterministic, and the resume harness reconstructs success under an oracle policy."""

import pytest

from d2b import FaultSpec, FaultType, inject
from d2b.domains import ALL_DOMAINS, REPO_TRIAGE, TRAVEL
from d2b.replay import evaluate, replay, replay_tail_policy, resume


@pytest.mark.parametrize("task", ALL_DOMAINS, ids=lambda t: t.name)
def test_healthy_trajectory_validates(task):
    assert evaluate(task, task.make_trajectory()).ok


@pytest.mark.parametrize("task", ALL_DOMAINS, ids=lambda t: t.name)
def test_replay_is_deterministic(task):
    t = task.make_trajectory()
    assert replay(t, task.make_env()) == replay(t, task.make_env())


@pytest.mark.parametrize("task", ALL_DOMAINS, ids=lambda t: t.name)
def test_wrong_tool_at_critical_step_breaks_validation(task):
    # A call-changing fault at the load-bearing step is caught by STATIC replay + the validator
    # (no model needed) — the validator judges state, not prose.
    t = task.make_trajectory()
    c = inject(t, FaultSpec(FaultType.WRONG_TOOL, position=task.critical_step, volume=2))
    assert not evaluate(task, c.corrupted).ok


@pytest.mark.parametrize("task", ALL_DOMAINS, ids=lambda t: t.name)
def test_context_only_fault_leaves_static_replay_valid(task):
    # debris changes context, not the recorded calls — so static replay still succeeds; its damage
    # only shows under resume-live (M2). This documents the two-mode design.
    t = task.make_trajectory()
    c = inject(t, FaultSpec(FaultType.DEBRIS, position=1, volume=3))
    assert evaluate(task, c.corrupted).ok


def test_repo_validator_reasons():
    good = evaluate(REPO_TRIAGE, REPO_TRIAGE.make_trajectory())
    assert good.ok and "pass" in good.reason.lower()


def test_resume_oracle_reconstructs_success():
    t = TRAVEL.make_trajectory()
    cut = 3
    res = resume(TRAVEL, t, cut, replay_tail_policy(t, cut))
    assert res.ok
