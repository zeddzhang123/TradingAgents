import os
from typing import Any, Optional

import httpx
import anthropic
from langchain_anthropic import ChatAnthropic

from .base_client import BaseLLMClient, normalize_content
from .validators import validate_model

_PASSTHROUGH_KWARGS = (
    "timeout", "max_retries", "api_key", "max_tokens",
    "callbacks", "default_headers",
    # "effort",  # Disabled: Venus proxy doesn't support this parameter
)


class BearerAuthTransport(httpx.BaseTransport):
    """Transport that converts x-api-key to Bearer auth."""

    def __init__(self, token: str, transport: httpx.BaseTransport = None):
        self._token = token
        self._transport = transport or httpx.HTTPTransport()

    def handle_request(self, request):
        # Remove x-api-key and add Bearer auth
        if "x-api-key" in request.headers:
            del request.headers["x-api-key"]
        request.headers["Authorization"] = f"Bearer {self._token}"
        return self._transport.handle_request(request)


class NormalizedChatAnthropic(ChatAnthropic):
    """ChatAnthropic with normalized content output and custom auth support.

    Claude models with extended thinking or tool use return content as a
    list of typed blocks. This normalizes to string for consistent
    downstream handling.
    """

    _custom_client: Optional[anthropic.Anthropic] = None

    def __init__(self, custom_client: Optional[anthropic.Anthropic] = None, **kwargs):
        super().__init__(**kwargs)
        self._custom_client = custom_client

    @property
    def _client(self) -> anthropic.Anthropic:
        """Return custom client if set, otherwise default."""
        if self._custom_client is not None:
            return self._custom_client
        return super()._client

    def invoke(self, input, config=None, **kwargs):
        return normalize_content(super().invoke(input, config, **kwargs))


class AnthropicClient(BaseLLMClient):
    """Client for Anthropic Claude models."""

    def __init__(self, model: str, base_url: Optional[str] = None, **kwargs):
        super().__init__(model, base_url, **kwargs)

    def get_llm(self) -> Any:
        """Return configured ChatAnthropic instance."""
        self.warn_if_unknown_model()
        llm_kwargs = {"model": self.model}

        if self.base_url:
            llm_kwargs["anthropic_api_url"] = self.base_url

        for key in _PASSTHROUGH_KWARGS:
            if key in self.kwargs:
                llm_kwargs[key] = self.kwargs[key]

        # Support custom headers from environment (e.g., Venus proxy)
        headers = {}
        custom_headers_env = os.getenv("ANTHROPIC_CUSTOM_HEADERS")
        if custom_headers_env:
            for item in custom_headers_env.split(","):
                if ":" in item:
                    k, v = item.split(":", 1)
                    headers[k.strip()] = v.strip()

        if "default_headers" in llm_kwargs:
            llm_kwargs["default_headers"].update(headers)
        else:
            llm_kwargs["default_headers"] = headers

        # Use Bearer auth for Venus proxy (detects by checking base URL)
        use_bearer = os.getenv("ANTHROPIC_USE_BEARER_AUTH", "").lower() == "true"
        if not use_bearer and self.base_url and "venus" in self.base_url.lower():
            use_bearer = True

        custom_client = None
        if use_bearer:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if api_key:
                # Create custom httpx client with Bearer auth transport
                http_client = httpx.Client(
                    transport=BearerAuthTransport(api_key)
                )
                custom_client = anthropic.Anthropic(
                    api_key=api_key,  # Still needed but will be replaced by Bearer
                    base_url=self.base_url,
                    default_headers=headers,
                    http_client=http_client,
                )

        return NormalizedChatAnthropic(custom_client=custom_client, **llm_kwargs)

    def validate_model(self) -> bool:
        """Validate model for Anthropic."""
        return validate_model("anthropic", self.model)
