"""
RouteX AI Module — NVIDIA NIM / Gemma Integration.

Allows ChainGuard AI to utilize NVIDIA NIM cloud endpoints (e.g. google/gemma-4-31b-it)
for live reasoning when configured. Reads credentials from environment variables.
Never leaks or commits secrets.
"""

import logging
import os
from typing import Any, Dict, List, Optional

import httpx

logger = logging.getLogger("routex.ai.nvidia")

NVIDIA_INVOKE_URL = os.getenv(
    "NVIDIA_INVOKE_URL", "https://integrate.api.nvidia.com/v1/chat/completions"
)
NVIDIA_MODEL = os.getenv("NVIDIA_MODEL", "google/gemma-4-31b-it")
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")


class NvidiaClient:
    """Client for NVIDIA NIM hosted models."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        invoke_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout_seconds: float = 10.0,
    ):
        self.api_key = api_key or os.getenv("NVIDIA_API_KEY")
        self.invoke_url = invoke_url or NVIDIA_INVOKE_URL
        self.model = model or NVIDIA_MODEL
        self.timeout_seconds = timeout_seconds

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)

    def generate(self, system_prompt: str, user_prompt: str) -> Optional[str]:
        """Send chat completion request to NVIDIA API endpoint."""
        if not self.is_configured:
            logger.info("NVIDIA API key not configured; skipping NVIDIA generation.")
            return None

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        payload = {
            "model": self.model,
            "max_tokens": 1024,
            "temperature": 0.5,
            "top_p": 1.0,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }

        try:
            with httpx.Client(timeout=self.timeout_seconds) as client:
                resp = client.post(self.invoke_url, json=payload, headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    choices = data.get("choices", [])
                    if choices:
                        return choices[0].get("message", {}).get("content")
                    return None
                else:
                    logger.warning(f"NVIDIA API returned HTTP {resp.status_code}")
                    return None
        except httpx.TimeoutException:
            logger.warning("NVIDIA API request timed out.")
            return None
        except Exception as err:
            logger.warning(f"NVIDIA API request failed: {type(err).__name__}")
            return None
