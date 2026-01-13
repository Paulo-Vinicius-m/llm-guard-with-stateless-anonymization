"""Tests for Vault class including the new clear() method."""

import pytest

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
