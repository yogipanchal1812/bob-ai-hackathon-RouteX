"""
Tests for AI Context Builder.

Verifies:
- Targeted context extraction (no massive data dumps)
- Identification of explicit entity IDs
- Detection of unknown / missing entity IDs to prevent hallucination
"""

from ai.copilot.context_builder import ContextBuilder


def test_extract_entity_ids():
    """Regex detects entity IDs from natural language queries."""
    builder = ContextBuilder()
    query = "Check status of shipment SH001 and disruption D001 along route R001 with carrier C001"
    ids = builder.extract_entity_ids(query)

    assert ids["shipment"] == ["SH001"]
    assert ids["disruption"] == ["D001"]
    assert ids["route"] == ["R001"]
    assert ids["carrier"] == ["C001"]


def test_context_builder_known_shipment():
    """Builder extracts specific details for a known shipment."""
    builder = ContextBuilder()
    context = builder.build_context("Why is SH001 at risk?")

    assert len(context["target_shipments"]) == 1
    s = context["target_shipments"][0]
    assert s["shipment_id"] == "SH001"
    assert s["cargo_type"] == "Electronics"
    assert "shipment:SH001" in context["sources"]
    assert len(context["unknown_entities"]) == 0


def test_context_builder_unknown_entity_flagged():
    """Unregistered entity IDs are flagged under unknown_entities to prevent hallucinations."""
    builder = ContextBuilder()
    context = builder.build_context("What is the status of SH999 and D999?")

    assert "shipment:SH999" in context["unknown_entities"]
    assert "disruption:D999" in context["unknown_entities"]
    assert len(context["target_shipments"]) == 0
    assert len(context["target_disruptions"]) == 0


def test_context_builder_location_matching():
    """Location keywords are linked to active disruptions."""
    builder = ContextBuilder()
    context = builder.build_context("What should we do about the Suez Canal congestion?")

    assert len(context["target_disruptions"]) >= 1
    d = context["target_disruptions"][0]
    assert "suez" in d["location"].lower()
    assert f"disruption:{d['disruption_id']}" in context["sources"]


def test_context_prompt_formatting_bounded():
    """Context prompt remains compact and does not dump full datasets."""
    builder = ContextBuilder()
    context = builder.build_context("Summarize network status")
    prompt_text = builder.format_context_prompt(context)

    # Prompt text should be concise, not thousands of lines
    assert len(prompt_text.splitlines()) < 40
