"""
Tests for IBM Bob & watsonx.ai Integration.

Verifies:
- Graceful offline fallback when unconfigured
- Timeout handling without application crashes
- Secure handling of secrets
"""

from ai.config import AIConfig
from ai.integrations.ibm_bob import IBMBobClient


def test_ibm_bob_unconfigured_fallback():
    """When credentials are not set, client returns None gracefully without error."""
    empty_config = AIConfig(
        watsonx_api_key=None,
        watsonx_project_id=None,
        ibm_bob_api_key=None,
        ibm_bob_endpoint=None,
    )
    client = IBMBobClient(config=empty_config)
    assert client.is_configured is False

    result = client.generate("Hello IBM Bob")
    assert result is None


def test_ibm_bob_timeout_graceful_handling():
    """Simulated timeout or unreachable endpoint returns None gracefully."""
    timeout_config = AIConfig(
        ibm_bob_api_key="test_dummy_key",
        ibm_bob_endpoint="http://10.255.255.1:9999/dummy",  # Non-routable IP
        timeout_seconds=0.1,
    )
    client = IBMBobClient(config=timeout_config)
    assert client.is_configured is True

    result = client.generate("Test query")
    assert result is None


def test_no_secrets_in_copilot_response(client):
    """Copilot response envelope must never leak environment variable keys or tokens."""
    resp = client.post("/api/copilot", json={"question": "What is the status of D001?"})
    assert resp.status_code == 200
    text_content = resp.text.lower()

    # Verify no secret keywords leaked
    assert "api_key" not in text_content
    assert "bearer" not in text_content
    assert "password" not in text_content
    assert "watsonx_project_id" not in text_content
