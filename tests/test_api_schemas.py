"""Tests for API response schemas with vault data."""

from llm_guard_api.app.schemas import AnalyzeOutputResponse, AnalyzePromptResponse


def test_analyze_prompt_response_with_vault():
    """Test AnalyzePromptResponse schema with vault data."""
    response = AnalyzePromptResponse(
        sanitized_prompt="My name is [REDACTED_PERSON_1]",
        is_valid=False,
        scanners={"Anonymize": 0.95},
        vault=[("[REDACTED_PERSON_1]", "John Doe")],
    )
    
    assert response.sanitized_prompt == "My name is [REDACTED_PERSON_1]"
    assert response.is_valid == False
    assert response.scanners == {"Anonymize": 0.95}
    assert response.vault == [("[REDACTED_PERSON_1]", "John Doe")]


def test_analyze_prompt_response_empty_vault():
    """Test AnalyzePromptResponse schema with empty vault."""
    response = AnalyzePromptResponse(
        sanitized_prompt="Just a simple prompt",
        is_valid=True,
        scanners={},
        vault=[],
    )
    
    assert response.vault == []


def test_analyze_prompt_response_vault_default():
    """Test AnalyzePromptResponse schema with default vault value."""
    response = AnalyzePromptResponse(
        sanitized_prompt="Just a simple prompt",
        is_valid=True,
        scanners={},
    )
    
    # Vault should default to empty list
    assert response.vault == []


def test_analyze_output_response_with_vault():
    """Test AnalyzeOutputResponse schema with vault data."""
    response = AnalyzeOutputResponse(
        sanitized_output="My email is [REDACTED_EMAIL_ADDRESS_1]",
        is_valid=False,
        scanners={"Anonymize": 0.90},
        vault=[("[REDACTED_EMAIL_ADDRESS_1]", "john@example.com")],
    )
    
    assert response.sanitized_output == "My email is [REDACTED_EMAIL_ADDRESS_1]"
    assert response.is_valid == False
    assert response.scanners == {"Anonymize": 0.90}
    assert response.vault == [("[REDACTED_EMAIL_ADDRESS_1]", "john@example.com")]


def test_analyze_output_response_multiple_vault_entries():
    """Test AnalyzeOutputResponse schema with multiple vault entries."""
    response = AnalyzeOutputResponse(
        sanitized_output="My name is [REDACTED_PERSON_1] and my email is [REDACTED_EMAIL_ADDRESS_1]",
        is_valid=False,
        scanners={"Anonymize": 0.95},
        vault=[
            ("[REDACTED_PERSON_1]", "John Doe"),
            ("[REDACTED_EMAIL_ADDRESS_1]", "john@example.com"),
        ],
    )
    
    assert len(response.vault) == 2
    assert response.vault[0] == ("[REDACTED_PERSON_1]", "John Doe")
    assert response.vault[1] == ("[REDACTED_EMAIL_ADDRESS_1]", "john@example.com")


def test_analyze_output_response_vault_default():
    """Test AnalyzeOutputResponse schema with default vault value."""
    response = AnalyzeOutputResponse(
        sanitized_output="Just a simple output",
        is_valid=True,
        scanners={},
    )
    
    # Vault should default to empty list
    assert response.vault == []
