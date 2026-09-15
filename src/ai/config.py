"""
RouteX AI Module — Configuration.

Manages environment settings for IBM Bob / watsonx.ai integration,
model parameters, timeouts, and fallback policies.
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class AIConfig:
    """Configuration for AI Copilot and IBM Bob integration."""

    # IBM watsonx / Bob API credentials
    watsonx_api_key: Optional[str] = os.getenv("WATSONX_API_KEY")
    watsonx_project_id: Optional[str] = os.getenv("WATSONX_PROJECT_ID")
    watsonx_url: str = os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")

    ibm_bob_api_key: Optional[str] = os.getenv("IBM_BOB_API_KEY")
    ibm_bob_endpoint: Optional[str] = os.getenv("IBM_BOB_ENDPOINT")

    # Model settings
    model_id: str = os.getenv("WATSONX_MODEL_ID", "ibm/granite-13b-chat-v2")
    temperature: float = float(os.getenv("AI_TEMPERATURE", "0.2"))
    max_tokens: int = int(os.getenv("AI_MAX_TOKENS", "1024"))
    timeout_seconds: float = float(os.getenv("AI_TIMEOUT_SECONDS", "8.0"))

    # Server port for standalone execution
    ai_port: int = int(os.getenv("AI_PORT", "8001"))

    @property
    def has_ibm_credentials(self) -> bool:
        """Check if active credentials for IBM Bob / watsonx are provided."""
        return bool(
            (self.ibm_bob_api_key and self.ibm_bob_endpoint)
            or (self.watsonx_api_key and self.watsonx_project_id)
        )


ai_config = AIConfig()
