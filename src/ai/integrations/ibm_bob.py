"""
RouteX AI Module — IBM Bob & watsonx.ai Integration.

Robust client for IBM Bob / watsonx text generation with strict timeout,
safe credential handling, and graceful offline fallback.
Never leaks or logs secrets.
"""

import json
import logging
from typing import Any, Dict, Optional

import httpx

from ai.config import ai_config

logger = logging.getLogger("routex.ai.ibm_bob")


class IBMBobClient:
    """Client for connecting to IBM Bob or IBM watsonx.ai endpoints."""

    def __init__(self, config=None):
        self.config = config or ai_config
        self.is_configured = self.config.has_ibm_credentials

    def generate(self, prompt: str) -> Optional[str]:
        """
        Send prompt to IBM Bob or watsonx.ai generation endpoint.
        Returns generated text or None if offline, unconfigured, or timed out.
        """
        if not self.is_configured:
            logger.info("IBM Bob/watsonx credentials not configured; using deterministic decision engine.")
            return None

        # Route to IBM Bob custom endpoint or watsonx foundation model
        if self.config.ibm_bob_endpoint and self.config.ibm_bob_api_key:
            return self._call_ibm_bob(prompt)
        elif self.config.watsonx_api_key and self.config.watsonx_project_id:
            return self._call_watsonx(prompt)

        return None

    def _call_ibm_bob(self, prompt: str) -> Optional[str]:
        """Call dedicated IBM Bob endpoint."""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config.ibm_bob_api_key}",
        }
        payload = {
            "prompt": prompt,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
        }

        try:
            with httpx.Client(timeout=self.config.timeout_seconds) as client:
                response = client.post(
                    self.config.ibm_bob_endpoint,
                    json=payload,
                    headers=headers,
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("text") or data.get("generated_text") or data.get("response")
                else:
                    logger.warning(f"IBM Bob endpoint returned status {response.status_code}")
                    return None
        except httpx.TimeoutException:
            logger.warning("IBM Bob request timed out; falling back to deterministic reasoning.")
            return None
        except Exception as err:
            logger.warning(f"IBM Bob connection failed ({type(err).__name__}); falling back to deterministic reasoning.")
            return None

    def _call_watsonx(self, prompt: str) -> Optional[str]:
        """Call standard IBM watsonx.ai generation endpoint."""
        url = f"{self.config.watsonx_url.rstrip('/')}/ml/v1/text/generation?version=2023-05-29"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {self.config.watsonx_api_key}",
        }
        payload = {
            "model_id": self.config.model_id,
            "project_id": self.config.watsonx_project_id,
            "input": prompt,
            "parameters": {
                "decoding_method": "greedy",
                "max_new_tokens": self.config.max_tokens,
                "temperature": self.config.temperature,
            },
        }

        try:
            with httpx.Client(timeout=self.config.timeout_seconds) as client:
                response = client.post(url, json=payload, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    results = data.get("results", [])
                    if results:
                        return results[0].get("generated_text")
                    return None
                else:
                    logger.warning(f"watsonx API returned status {response.status_code}")
                    return None
        except httpx.TimeoutException:
            logger.warning("watsonx request timed out; falling back to deterministic reasoning.")
            return None
        except Exception as err:
            logger.warning(f"watsonx connection failed ({type(err).__name__}); falling back to deterministic reasoning.")
            return None
