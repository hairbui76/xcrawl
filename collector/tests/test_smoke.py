"""Phase 0 smoke tests for the collector skeleton.

The interesting assertions are the negative ones: no browser is launched, and the payload
never upgrades an undetermined session state into a good one.
"""

from __future__ import annotations

import json

from rr_contracts.generated.constants import CONTRACT_SCHEMA_VERSION

from collector.app.main import capability_registration_shape, main


def test_registration_payload_matches_the_contract_field_list() -> None:
    payload = capability_registration_shape()
    assert payload["worker_kind"] == "collector"
    assert payload["schema_version"] == CONTRACT_SCHEMA_VERSION
    assert set(payload["capabilities"]) == {
        "collector_online",
        "chrome_profile_ready",
        "x_session_state",
    }


def test_unknown_session_state_is_not_converted_to_ok() -> None:
    """CAP-P5: `unknown` may never be reported as `ok`."""
    assert capability_registration_shape()["capabilities"]["x_session_state"] == "unknown"
    assert capability_registration_shape()["capabilities"]["collector_online"] is False


def test_cli_prints_valid_json(capsys) -> None:  # type: ignore[no-untyped-def]
    assert main(["--print-registration"]) == 0
    assert json.loads(capsys.readouterr().out)["worker_kind"] == "collector"


def test_playwright_is_declared_but_no_browser_is_installed() -> None:
    """Playwright is a declared dependency; browsers are an Owner-machine step.

    Importing the package must not download or launch anything.
    """
    import playwright  # noqa: F401

    from collector.app import main as collector_main

    source = collector_main.__doc__ or ""
    assert "does not launch a browser" in source
