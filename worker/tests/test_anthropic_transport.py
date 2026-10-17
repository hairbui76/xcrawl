"""``AnthropicTransport`` against a fake SDK client — no network, no key.

What is asserted is the request the transport builds and how it reads the answer: the model
and effort come from the registry, no tools and no thinking field are sent, retries are off,
and a refusal is a provider failure rather than an empty result.
"""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest

from worker.app.adapter.api_provider import (
    AnthropicTransport,
    ProviderRequest,
    ProviderUnavailable,
)
from worker.app.adapter.base import TaskCredential, load_registered_adapters

CANARY = "sk-test-not-a-real-key"


class FakeClient:
    def __init__(self, reply: Any, **config: Any) -> None:
        self.config = config
        self.calls: list[dict[str, Any]] = []
        self._reply = reply
        self.messages = SimpleNamespace(create=self._create)

    def _create(self, **kwargs: Any) -> Any:
        self.calls.append(kwargs)
        return self._reply


def _reply(*, stop_reason: str = "end_turn", text: str = '{"ok": true}') -> Any:
    return SimpleNamespace(
        stop_reason=stop_reason,
        content=[
            SimpleNamespace(type="thinking", thinking=""),
            SimpleNamespace(type="text", text=text),
        ],
        usage=SimpleNamespace(input_tokens=11, output_tokens=7),
    )


def _request(task_type: str = "label") -> ProviderRequest:
    entry = load_registered_adapters()[0]
    return ProviderRequest(
        url=entry.endpoint,
        model=entry.model_name,
        system="system",
        messages=({"role": "user", "content": "<source id=s1>text</source id=s1>"},),
        response_schema={"task_type": task_type},
        timeout_seconds=entry.request_timeout_seconds,
    )


def _credential() -> TaskCredential:
    return TaskCredential(
        value=CANARY, provider_config_id="pc-1", task_id="t-1", expires_at="2099-01-01"
    )


def test_the_registry_entry_is_opus_5_5_on_the_anthropic_endpoint_and_still_disabled() -> None:
    (entry,) = load_registered_adapters()
    assert entry.model_name == "claude-opus-5-5"
    assert entry.endpoint == "https://api.anthropic.com"
    assert entry.endpoint_allowlist == frozenset({"api.anthropic.com"})
    assert entry.enabled is False, "OD-20261017-13 changes the model, not the isolation gate"


def test_request_shape_effort_per_task_no_tools_and_no_retries() -> None:
    made: list[FakeClient] = []

    def factory(**config: Any) -> FakeClient:
        client = FakeClient(_reply(), **config)
        made.append(client)
        return client

    entry = load_registered_adapters()[0]
    transport = AnthropicTransport(effort_by_task=entry.effort_by_task, client_factory=factory)
    response = transport.send(_request("label"), credential=_credential())

    (client,) = made
    assert client.config["max_retries"] == 0, "the adapter counts calls; the SDK may not retry"
    assert client.config["api_key"] == CANARY
    assert client.config["base_url"] == "https://api.anthropic.com"
    (call,) = client.calls
    assert call["model"] == "claude-opus-5-5"
    assert call["output_config"] == {"effort": "low"}
    assert "tools" not in call and "thinking" not in call
    assert response.body == '{"ok": true}'
    assert (response.tokens_in, response.tokens_out, response.tool_requests) == (11, 7, 0)

    transport.send(_request("summary"), credential=_credential())
    assert made[1].calls[0]["output_config"] == {"effort": "medium"}


def test_a_refusal_is_a_provider_failure_not_an_empty_answer() -> None:
    transport = AnthropicTransport(
        effort_by_task={"label": "low"},
        client_factory=lambda **config: FakeClient(
            _reply(stop_reason="refusal", text=""), **config
        ),
    )
    with pytest.raises(ProviderUnavailable):
        transport.send(_request("label"), credential=_credential())


def test_an_effort_the_model_does_not_accept_is_refused_before_any_call() -> None:
    with pytest.raises(ValueError):
        AnthropicTransport(effort_by_task={"label": "minimal"})
