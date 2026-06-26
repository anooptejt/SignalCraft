import httpx

from app.core.config import Settings
from app.llm.client import LLMClient


def test_azure_openai_client_uses_efd_contract():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/openai/deployments/gpt-4o/chat/completions"
        assert request.url.params["api-version"] == "2024-08-01-preview"
        assert request.headers["api-key"] == "test-key"
        return httpx.Response(
            200,
            json={
                "choices": [{"message": {"content": "CONNECTION_OK"}}],
                "usage": {"prompt_tokens": 3, "completion_tokens": 1},
            },
        )

    settings = Settings(
        llm_provider="azure-openai",
        azure_openai_api_key="test-key",
        azure_openai_endpoint="https://efd-demo.openai.azure.com",
        azure_openai_deployment="gpt-4o",
        azure_openai_api_version="2024-08-01-preview",
    )
    client = LLMClient(settings=settings, http_client=httpx.Client(transport=httpx.MockTransport(handler)))

    result = client.test_connection()

    assert result["success"] is True
    assert result["provider"] == "azure-openai"
    assert result["model"] == "gpt-4o"
