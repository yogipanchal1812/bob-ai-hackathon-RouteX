"""
config.py — Environment-based configuration for Module 4 (Optimization).

All values are read from environment variables.
No secrets are hardcoded here.

Usage:
    from optimization.config import settings
    print(settings.port)
"""

import os


class Settings:
    """
    Module 4 configuration.

    Environment variables (see src/.env.example for full list):
        OPT_PORT            Server port (default: 8001)
        OPT_LOG_LEVEL       Logging level (default: INFO)
        DISRUPTION_API_URL  Base URL of Member 1's disruption API (optional).
                            When set, the module can be wired to live data.
                            When absent, seed data is used (dev/demo mode).
        APP_ENV             'development' | 'production' (default: development)
        CORS_ORIGINS        Comma-separated allowed CORS origins for Member 2 frontend.
    """

    def __init__(self) -> None:
        self.port: int = int(os.getenv("OPT_PORT", "8001"))
        self.log_level: str = os.getenv("OPT_LOG_LEVEL", "INFO").upper()
        self.app_env: str = os.getenv("APP_ENV", "development")
        self.disruption_api_url: str | None = os.getenv("DISRUPTION_API_URL", None)

        # Parse CORS origins (comma-separated)
        cors_raw = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173")
        self.cors_origins: list[str] = [
            origin.strip() for origin in cors_raw.split(",") if origin.strip()
        ]

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"

    @property
    def use_seed_data(self) -> bool:
        """True when no live disruption API is configured (dev/demo mode)."""
        return self.disruption_api_url is None


settings = Settings()
