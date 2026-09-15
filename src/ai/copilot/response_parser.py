"""
RouteX AI Module — Response Parser.

Parses AI/LLM outputs, extracts referenced entity source tags,
and formats unified responses.
"""

import re
from typing import List, Set


class ResponseParser:
    """Extracts verifiable sources and cleans response strings."""

    SOURCE_PATTERNS = {
        "shipment": re.compile(r"\b(SH\d{3,4})\b", re.IGNORECASE),
        "disruption": re.compile(r"\b(D\d{3,4})\b", re.IGNORECASE),
        "route": re.compile(r"\b(R\d{3,4})\b", re.IGNORECASE),
        "carrier": re.compile(r"\b(C\d{3,4})\b", re.IGNORECASE),
    }

    @classmethod
    def extract_sources(cls, text: str, initial_sources: List[str] = None) -> List[str]:
        """
        Extract all entities referenced in the response text,
        combining with initial sources from retrieval.
        """
        sources: Set[str] = set(initial_sources or [])

        for entity_type, pattern in cls.SOURCE_PATTERNS.items():
            matches = pattern.findall(text)
            for m in matches:
                sources.add(f"{entity_type}:{m.upper()}")

        return sorted(list(sources))

    @classmethod
    def clean_response(cls, text: str) -> str:
        """Strip unnecessary whitespace or artifact tokens from response."""
        cleaned = text.strip()
        # Remove repeated [FACT] tags if duplicate
        return cleaned
