"""Phase 0 smoke tests for the analysis worker skeleton."""

from __future__ import annotations

import json

from rr_contracts.generated.states import AnalysisTaskType

from worker.app.main import advertised_task_types, main


def test_task_types_come_from_the_state_contract() -> None:
    assert advertised_task_types() == [m.value for m in AnalysisTaskType]
    assert advertised_task_types() == ["label", "summary", "direction_phrasing"]


def test_embedding_is_not_a_worker_task() -> None:
    """REQ-D48/REQ-D50: embedding runs locally on the server, not on the worker."""
    assert "embedding" not in advertised_task_types()


def test_cli_prints_valid_json_with_no_providers(capsys) -> None:  # type: ignore[no-untyped-def]
    assert main(["--print-capabilities"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["ai_providers"] == []
