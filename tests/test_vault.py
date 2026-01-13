"""Tests for Vault class including the new clear() method."""

from llm_guard.vault import Vault


def test_vault_clear():
    """Test that the clear method removes all tuples from the vault."""
    vault = Vault()
    
    # Add some test data
    vault.append(("[REDACTED_PERSON_1]", "John Doe"))
    vault.append(("[REDACTED_EMAIL_ADDRESS_1]", "john@example.com"))
    
    # Verify data is present
    assert len(vault.get()) == 2
    
    # Clear the vault
    vault.clear()
    
    # Verify vault is empty
    assert len(vault.get()) == 0
    assert vault.get() == []


def test_vault_clear_empty():
    """Test that clearing an empty vault doesn't cause errors."""
    vault = Vault()
    
    # Clear empty vault
    vault.clear()
    
    # Verify vault is still empty
    assert len(vault.get()) == 0


def test_vault_clear_then_append():
    """Test that we can add new data after clearing."""
    vault = Vault()
    
    # Add and clear
    vault.append(("[REDACTED_PERSON_1]", "John Doe"))
    vault.clear()
    
    # Add new data
    vault.append(("[REDACTED_PERSON_2]", "Jane Doe"))
    
    # Verify only new data is present
    assert len(vault.get()) == 1
    assert vault.get()[0] == ("[REDACTED_PERSON_2]", "Jane Doe")


def test_vault_get_and_clear():
    """Test that get_and_clear atomically retrieves and clears vault data."""
    vault = Vault()
    
    # Add some test data
    vault.append(("[REDACTED_PERSON_1]", "John Doe"))
    vault.append(("[REDACTED_EMAIL_ADDRESS_1]", "john@example.com"))
    
    # Get and clear in one operation
    vault_data = vault.get_and_clear()
    
    # Verify we got the data
    assert len(vault_data) == 2
    assert vault_data[0] == ("[REDACTED_PERSON_1]", "John Doe")
    assert vault_data[1] == ("[REDACTED_EMAIL_ADDRESS_1]", "john@example.com")
    
    # Verify vault is now empty
    assert len(vault.get()) == 0


def test_vault_get_and_clear_empty():
    """Test that get_and_clear on empty vault returns empty list."""
    vault = Vault()
    
    # Get and clear empty vault
    vault_data = vault.get_and_clear()
    
    # Verify we got an empty list
    assert vault_data == []
    assert len(vault.get()) == 0


def test_vault_get_returns_copy():
    """Test that get() returns a copy, not a reference to internal data."""
    vault = Vault()
    vault.append(("[REDACTED_PERSON_1]", "John Doe"))
    
    # Get vault data
    vault_data = vault.get()
    
    # Modify the returned data
    vault_data.append(("[REDACTED_EMAIL_ADDRESS_1]", "john@example.com"))
    
    # Verify the vault still only has the original data
    assert len(vault.get()) == 1
    assert vault.get()[0] == ("[REDACTED_PERSON_1]", "John Doe")
