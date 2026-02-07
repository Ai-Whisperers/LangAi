"""Tests for standardized agent error handling utilities."""

from __future__ import annotations

import logging
from typing import Any, Dict, List

import pytest

from company_researcher.agents.base.errors import (
    AgentError,
    AgentErrorContext,
    ErrorSeverity,
    LLMError,
    ParsingError,
    RetryConfig,
    ValidationError,
    create_error_result,
    handle_agent_error,
    validate_company_name,
    validate_search_results,
    with_retry,
)


@pytest.mark.unit
def test_agent_error_to_dict_includes_details() -> None:
    err = AgentError("boom", agent_name="agent", details={"k": "v"})
    payload = err.to_dict()
    assert payload["error_type"] == "AgentError"
    assert payload["message"] == "boom"
    assert payload["agent_name"] == "agent"
    assert payload["details"] == {"k": "v"}


@pytest.mark.unit
def test_parsing_error_includes_preview_and_expected_format() -> None:
    raw = "x" * 500
    err = ParsingError("bad parse", agent_name="parser", raw_response=raw, expected_format="json")
    details = err.to_dict()["details"]
    assert details["expected_format"] == "json"
    assert details["raw_response_preview"] == raw[:200]


@pytest.mark.unit
def test_create_error_result_includes_details_and_partial_result() -> None:
    err = ParsingError(
        "bad parse", agent_name="parser", raw_response="oops", expected_format="json"
    )
    result = create_error_result(
        agent_name="parser", error=err, severity=ErrorSeverity.HIGH, partial_result={"a": 1}
    )

    agent_output = result["agent_outputs"]["parser"]
    assert agent_output["error"] is True
    assert agent_output["error_type"] == "ParsingError"
    assert agent_output["severity"] == "high"
    assert "details" in agent_output
    assert agent_output["partial_result"] == {"a": 1}


@pytest.mark.unit
def test_handle_agent_error_logs_and_can_reraise(caplog: pytest.LogCaptureFixture) -> None:
    logger = logging.getLogger("agent.test")

    with caplog.at_level(logging.WARNING):
        result = handle_agent_error(
            ValueError("bad"),
            agent_name="test",
            logger=logger,
            reraise=False,
            severity=ErrorSeverity.MEDIUM,
        )
    assert "Agent warning: bad" in caplog.text
    assert result["agent_outputs"]["test"]["error"] is True

    with pytest.raises(ValueError, match="bad"):
        handle_agent_error(
            ValueError("bad"),
            agent_name="test",
            logger=logger,
            reraise=True,
            severity=ErrorSeverity.LOW,
        )


@pytest.mark.unit
def test_with_retry_retries_retryable_exceptions_and_invokes_callback(mocker: Any) -> None:
    callback = mocker.Mock()
    sleep = mocker.patch("company_researcher.agents.base.errors.time.sleep")

    calls: List[int] = []

    @with_retry(
        RetryConfig(
            max_retries=2,
            delay=1.0,
            backoff_factor=2.0,
            retryable_exceptions=(LLMError,),
            on_retry=callback,
        )
    )
    def flaky() -> str:
        calls.append(1)
        if len(calls) < 3:
            raise LLMError("transient", agent_name="llm", retryable=True)
        return "ok"

    assert flaky() == "ok"
    assert callback.call_count == 2
    sleep.assert_any_call(1.0)
    sleep.assert_any_call(2.0)


@pytest.mark.unit
def test_agent_error_context_does_not_suppress_exceptions() -> None:
    ctx = AgentErrorContext("agent")
    with pytest.raises(RuntimeError, match="boom"):
        with ctx:
            raise RuntimeError("boom")

    assert ctx.has_error is True
    assert isinstance(ctx.error, RuntimeError)


@pytest.mark.unit
def test_validate_search_results_raises_validation_error_with_details() -> None:
    with pytest.raises(ValidationError) as exc:
        validate_search_results(None, agent_name="a", min_results=1)
    assert exc.value.details["field"] == "search_results"

    with pytest.raises(ValidationError):
        validate_search_results("not-a-list", agent_name="a", min_results=1)

    with pytest.raises(ValidationError):
        validate_search_results([], agent_name="a", min_results=1)

    ok: List[Dict[str, Any]] = [{"url": "x"}]
    assert validate_search_results(ok, agent_name="a", min_results=1) is ok


@pytest.mark.unit
def test_validate_company_name_strips_and_validates() -> None:
    assert validate_company_name("  TestCo  ", agent_name="a") == "TestCo"

    with pytest.raises(ValidationError):
        validate_company_name("", agent_name="a")

    with pytest.raises(ValidationError):
        validate_company_name(123, agent_name="a")
