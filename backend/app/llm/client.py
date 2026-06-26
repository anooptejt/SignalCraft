from dataclasses import dataclass
from typing import Any

import httpx

from app.core.config import Settings, get_settings


@dataclass(frozen=True)
class LLMResponse:
    content: str
    provider: str
    model: str
    usage: dict[str, int]


class LLMClient:
    def __init__(self, settings: Settings | None = None, http_client: httpx.Client | None = None):
        self.settings = settings or get_settings()
        self.http_client = http_client or httpx.Client(timeout=60)

    def send_message(
        self,
        messages: list[dict[str, str]],
        system_prompt: str | None = None,
        max_tokens: int = 1200,
        temperature: float = 0.4,
    ) -> LLMResponse:
        provider = self.settings.llm_provider
        if provider == "azure-openai":
            return self._send_azure_openai(messages, system_prompt, max_tokens, temperature)
        if provider == "openai":
            return self._send_openai(messages, system_prompt, max_tokens, temperature)
        raise ValueError(f'Unsupported LLM provider "{provider}". Supported: openai, azure-openai')

    def test_connection(self) -> dict[str, Any]:
        try:
            response = self.send_message(
                messages=[{"role": "user", "content": "Respond with only: CONNECTION_OK"}],
                max_tokens=20,
                temperature=0,
            )
            return {
                "success": response.content.strip() == "CONNECTION_OK",
                "provider": response.provider,
                "model": response.model,
                "response": response.content.strip(),
            }
        except Exception as exc:  # noqa: BLE001 - returned to health endpoint without secrets.
            return {
                "success": False,
                "provider": self.settings.llm_provider,
                "model": self._configured_model(),
                "error": str(exc),
            }

    def _send_openai(
        self,
        messages: list[dict[str, str]],
        system_prompt: str | None,
        max_tokens: int,
        temperature: float,
    ) -> LLMResponse:
        if not self.settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is not set")

        model = self.settings.openai_model or self.settings.llm_model
        payload = {
            "model": model,
            "messages": self._messages(messages, system_prompt),
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        response = self.http_client.post(
            f"{self.settings.openai_base_url.rstrip('/')}/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.settings.openai_api_key}",
            },
            json=payload,
        )
        response.raise_for_status()
        data = response.json()
        return LLMResponse(
            content=data.get("choices", [{}])[0].get("message", {}).get("content", ""),
            provider="openai",
            model=model,
            usage=self._usage(data),
        )

    def _send_azure_openai(
        self,
        messages: list[dict[str, str]],
        system_prompt: str | None,
        max_tokens: int,
        temperature: float,
    ) -> LLMResponse:
        if not self.settings.azure_openai_api_key:
            raise ValueError("AZURE_OPENAI_API_KEY is not set")
        if not self.settings.azure_openai_endpoint:
            raise ValueError("AZURE_OPENAI_ENDPOINT is not set")

        deployment = self.settings.azure_openai_deployment
        endpoint = self.settings.azure_openai_endpoint.rstrip("/")
        url = (
            f"{endpoint}/openai/deployments/{deployment}/chat/completions"
            f"?api-version={self.settings.azure_openai_api_version}"
        )
        payload = {
            "messages": self._messages(messages, system_prompt),
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        response = self.http_client.post(
            url,
            headers={
                "Content-Type": "application/json",
                "api-key": self.settings.azure_openai_api_key,
            },
            json=payload,
        )
        response.raise_for_status()
        data = response.json()
        return LLMResponse(
            content=data.get("choices", [{}])[0].get("message", {}).get("content", ""),
            provider="azure-openai",
            model=deployment,
            usage=self._usage(data),
        )

    def _configured_model(self) -> str:
        if self.settings.llm_provider == "azure-openai":
            return self.settings.azure_openai_deployment
        return self.settings.openai_model or self.settings.llm_model

    @staticmethod
    def _messages(messages: list[dict[str, str]], system_prompt: str | None) -> list[dict[str, str]]:
        prepared: list[dict[str, str]] = []
        if system_prompt:
            prepared.append({"role": "system", "content": system_prompt})
        prepared.extend(messages)
        return prepared

    @staticmethod
    def _usage(data: dict[str, Any]) -> dict[str, int]:
        usage = data.get("usage") or {}
        return {
            "inputTokens": int(usage.get("prompt_tokens") or 0),
            "outputTokens": int(usage.get("completion_tokens") or 0),
        }
