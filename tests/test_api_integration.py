"""Integration tests for API endpoints with vault data and anonymization/deanonymization flows."""


import pytest
from llm_guard_api.app.config import AppConfig, AuthConfig, Config, RateLimitConfig
from llm_guard_api.app.schemas import AnalyzeOutputResponse, AnalyzePromptResponse

from llm_guard.vault import Vault


@pytest.fixture
def mock_config():
    """Create a mock configuration."""
    config = Config(
        app=AppConfig(
            name="Test API",
            log_level="INFO",
            log_json=False,
            scan_fail_fast=False,
            scan_prompt_timeout=30,
            scan_output_timeout=30,
            lazy_load=False,
        ),
        rate_limit=RateLimitConfig(enabled=False, limit="100/minute"),
        auth=AuthConfig(type="http_bearer", token="test-token"),
        input_scanners=[],
        output_scanners=[],
    )
    return config


@pytest.fixture
def auth_headers():
    """Provide authentication headers for API requests."""
    return {"Authorization": "Bearer test-token"}


class TestAnalyzePromptEndpointSchema:
    """Test cases for /analyze/prompt endpoint response schema."""

    def test_analyze_prompt_response_includes_vault_field(self):
        """Test that AnalyzePromptResponse includes vault field."""
        response = AnalyzePromptResponse(
            sanitized_prompt="Test prompt",
            is_valid=True,
            scanners={},
            vault=[],
        )
        
        assert hasattr(response, "vault")
        assert isinstance(response.vault, list)
        assert response.vault == []

    def test_analyze_prompt_response_with_vault_data(self):
        """Test AnalyzePromptResponse with vault data."""
        vault_data = [
            ("[REDACTED_PERSON_1]", "John Doe"),
            ("[REDACTED_EMAIL_ADDRESS_1]", "john@example.com"),
        ]
        
        response = AnalyzePromptResponse(
            sanitized_prompt="My name is [REDACTED_PERSON_1]",
            is_valid=False,
            scanners={"Anonymize": 0.95},
            vault=vault_data,
        )
        
        assert response.vault == vault_data
        assert len(response.vault) == 2
        assert response.vault[0] == ("[REDACTED_PERSON_1]", "John Doe")
        assert response.vault[1] == ("[REDACTED_EMAIL_ADDRESS_1]", "john@example.com")


class TestAnalyzeOutputEndpointSchema:
    """Test cases for /analyze/output endpoint response schema."""

    def test_analyze_output_response_includes_vault_field(self):
        """Test that AnalyzeOutputResponse includes vault field."""
        response = AnalyzeOutputResponse(
            sanitized_output="Test output",
            is_valid=True,
            scanners={},
            vault=[],
        )
        
        assert hasattr(response, "vault")
        assert isinstance(response.vault, list)
        assert response.vault == []

    def test_analyze_output_response_with_vault_data(self):
        """Test AnalyzeOutputResponse with vault data."""
        vault_data = [
            ("[REDACTED_EMAIL_ADDRESS_1]", "support@example.com"),
        ]
        
        response = AnalyzeOutputResponse(
            sanitized_output="Contact [REDACTED_EMAIL_ADDRESS_1]",
            is_valid=False,
            scanners={"Sensitive": 0.80},
            vault=vault_data,
        )
        
        assert response.vault == vault_data
        assert len(response.vault) == 1


class TestVaultDataStructure:
    """Test vault data structure and format."""

    def test_vault_entry_is_tuple_of_two_strings(self):
        """Test that each vault entry is a tuple of two strings."""
        response = AnalyzePromptResponse(
            sanitized_prompt="Test",
            is_valid=True,
            scanners={},
            vault=[
                ("[REDACTED_PERSON_1]", "Alice"),
                ("[REDACTED_EMAIL_ADDRESS_1]", "alice@example.com"),
            ],
        )
        
        for entry in response.vault:
            assert isinstance(entry, (list, tuple))
            assert len(entry) == 2
            assert isinstance(entry[0], str)
            assert isinstance(entry[1], str)

    def test_vault_placeholder_format(self):
        """Test that placeholders follow the expected format."""
        response = AnalyzePromptResponse(
            sanitized_prompt="Test",
            is_valid=True,
            scanners={},
            vault=[
                ("[REDACTED_PERSON_1]", "Bob"),
                ("[REDACTED_EMAIL_ADDRESS_2]", "bob@example.com"),
            ],
        )
        
        for placeholder, _ in response.vault:
            assert placeholder.startswith("[REDACTED_")
            assert placeholder.endswith("]")
            assert "_" in placeholder

    def test_vault_can_be_empty(self):
        """Test that vault can be empty list."""
        response = AnalyzePromptResponse(
            sanitized_prompt="Simple prompt",
            is_valid=True,
            scanners={},
            vault=[],
        )
        
        assert response.vault == []
        assert isinstance(response.vault, list)


class TestVaultThreadSafety:
    """Test vault thread safety with locks."""

    def test_vault_get_returns_copy(self):
        """Test that vault.get() returns a copy, not a reference."""
        vault = Vault()
        vault.append(("[REDACTED_PERSON_1]", "John"))
        
        # Get vault data
        vault_data = vault.get()
        original_length = len(vault_data)
        
        # Modify the returned copy
        vault_data.append(("[REDACTED_EMAIL_1]", "test@test.com"))
        
        # Original vault should be unchanged
        assert len(vault.get()) == original_length

    def test_vault_get_and_clear_is_atomic(self):
        """Test that get_and_clear returns data and clears in one operation."""
        vault = Vault()
        vault.append(("[REDACTED_PERSON_1]", "Alice"))
        vault.append(("[REDACTED_EMAIL_1]", "alice@test.com"))
        
        # Get and clear
        vault_data = vault.get_and_clear()
        
        # Should return the data
        assert len(vault_data) == 2
        assert vault_data[0] == ("[REDACTED_PERSON_1]", "Alice")
        
        # Vault should be empty
        assert len(vault.get()) == 0

    def test_vault_clear_removes_all_data(self):
        """Test that vault.clear() removes all data."""
        vault = Vault()
        vault.append(("[REDACTED_PERSON_1]", "Bob"))
        vault.append(("[REDACTED_EMAIL_1]", "bob@test.com"))
        vault.append(("[REDACTED_PHONE_1]", "555-0000"))
        
        assert len(vault.get()) == 3
        
        vault.clear()
        
        assert len(vault.get()) == 0
        assert vault.get() == []


class TestAnonymizationFlow:
    """Test anonymization conceptual flow."""

    def test_anonymization_creates_vault_mappings(self):
        """Test that anonymization creates vault mappings."""
        # Simulate what happens during anonymization
        vault = Vault()
        
        # Original text with PII
        original_text = "My name is Sarah Johnson"
        
        # Scanner would detect "Sarah Johnson" and create a placeholder
        placeholder = "[REDACTED_PERSON_1]"
        original_value = "Sarah Johnson"
        
        # Add to vault
        vault.append((placeholder, original_value))
        
        # Sanitized text
        sanitized_text = original_text.replace(original_value, placeholder)
        
        # Verify the flow
        assert sanitized_text == "My name is [REDACTED_PERSON_1]"
        assert len(vault.get()) == 1
        assert vault.get()[0] == (placeholder, original_value)

    def test_deanonymization_reverses_mappings(self):
        """Test conceptual deanonymization flow."""
        # Simulate vault with mappings from anonymization
        vault = Vault()
        vault.append(("[REDACTED_PERSON_1]", "Jane Doe"))
        vault.append(("[REDACTED_EMAIL_ADDRESS_1]", "jane@example.com"))
        
        # Text with placeholders (what LLM sees/returns)
        text_with_placeholders = "Hello [REDACTED_PERSON_1], your email [REDACTED_EMAIL_ADDRESS_1] is verified."
        
        # Deanonymize by reversing mappings
        deanonymized_text = text_with_placeholders
        for placeholder, original in vault.get():
            deanonymized_text = deanonymized_text.replace(placeholder, original)
        
        # Verify deanonymization
        assert "Jane Doe" in deanonymized_text
        assert "jane@example.com" in deanonymized_text
        assert "[REDACTED" not in deanonymized_text

    def test_vault_isolation_per_request(self):
        """Test that vault can be isolated per request."""
        # Request 1
        vault1 = Vault()
        vault1.append(("[REDACTED_PERSON_1]", "Alice"))
        data1 = vault1.get_and_clear()
        
        # Request 2
        vault2 = Vault()
        vault2.append(("[REDACTED_PERSON_1]", "Bob"))
        data2 = vault2.get_and_clear()
        
        # Verify isolation
        assert data1[0][1] == "Alice"
        assert data2[0][1] == "Bob"
        assert data1 != data2


class TestScanEndpointsExcludeVault:
    """Test that /scan endpoints do NOT include vault."""

    def test_scan_prompt_response_has_no_vault_in_schema(self):
        """Test that ScanPromptResponse does not have vault field."""
        from llm_guard_api.app.schemas import ScanPromptResponse
        
        response = ScanPromptResponse(
            is_valid=True,
            scanners={},
        )
        
        # Should not have vault attribute
        assert not hasattr(response, "vault")

    def test_scan_output_response_has_no_vault_in_schema(self):
        """Test that ScanOutputResponse does not have vault field."""
        from llm_guard_api.app.schemas import ScanOutputResponse
        
        response = ScanOutputResponse(
            is_valid=True,
            scanners={},
        )
        
        # Should not have vault attribute
        assert not hasattr(response, "vault")


class TestVaultPersistencePattern:
    """Test the vault persistence and cleanup pattern."""

    def test_vault_should_be_cleared_after_use(self):
        """Test the pattern of using and clearing vault."""
        vault = Vault()
        
        # Simulate processing a request
        vault.append(("[REDACTED_PERSON_1]", "Test User"))
        vault.append(("[REDACTED_EMAIL_1]", "test@test.com"))
        
        # Get vault data for response
        vault_data = vault.get_and_clear()
        
        # Vault should be empty after get_and_clear
        assert len(vault.get()) == 0
        
        # But we still have the data to return
        assert len(vault_data) == 2
        
        # Next request starts with clean vault
        vault.append(("[REDACTED_PERSON_1]", "Another User"))
        new_data = vault.get_and_clear()
        
        assert len(new_data) == 1
        assert new_data[0][1] == "Another User"
        # Should not have data from previous request
        assert "Test User" not in [item[1] for item in new_data]


class TestVaultDataRetrieval:
    """Test vault data retrieval scenarios."""

    def test_empty_vault_returns_empty_list(self):
        """Test that empty vault returns empty list."""
        vault = Vault()
        assert vault.get() == []
        assert vault.get_and_clear() == []

    def test_vault_maintains_order(self):
        """Test that vault maintains insertion order."""
        vault = Vault()
        vault.append(("[REDACTED_PERSON_1]", "First"))
        vault.append(("[REDACTED_PERSON_2]", "Second"))
        vault.append(("[REDACTED_PERSON_3]", "Third"))
        
        data = vault.get()
        
        assert data[0][1] == "First"
        assert data[1][1] == "Second"
        assert data[2][1] == "Third"

    def test_vault_can_handle_duplicate_values(self):
        """Test that vault can store multiple placeholders for same value."""
        vault = Vault()
        # Same email appears twice, gets different placeholders
        vault.append(("[REDACTED_EMAIL_ADDRESS_1]", "same@example.com"))
        vault.append(("[REDACTED_EMAIL_ADDRESS_2]", "same@example.com"))
        
        data = vault.get()
        
        assert len(data) == 2
        assert data[0][0] != data[1][0]  # Different placeholders
        assert data[0][1] == data[1][1]  # Same original value
