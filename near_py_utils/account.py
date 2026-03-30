"""
NEAR Account ID Validation Utilities

Provides validation for NEAR Protocol account IDs according to the official spec.
"""

import re
from typing import TypeVar, Union

T = TypeVar('T')

class AccountValidationError(ValueError):
    """Raised when account ID validation fails."""
    pass

# NEAR account ID regex pattern
# - 2-64 characters
# - Lowercase letters, numbers, and separators (. or -)
# - Must start and end with alphanumeric
# - No consecutive separators
ACCOUNT_ID_PATTERN = re.compile(
    r'^(([a-z0-9]+[\-.])*[a-z0-9]+|[a-z0-9]+)$'
)

MAX_ACCOUNT_LENGTH = 64
MIN_ACCOUNT_LENGTH = 2


def is_valid_account_id(account_id: str) -> bool:
    """
    Validate a NEAR account ID.
    
    Args:
        account_id: The account ID to validate
        
    Returns:
        True if valid, False otherwise
        
    Examples:
        >>> is_valid_account_id("example.near")
        True
        >>> is_valid_account_id("test-account.testnet")
        True
        >>> is_valid_account_id("INVALID")
        False
        >>> is_valid_account_id("ab")
        True
        >>> is_valid_account_id("a")
        False
    """
    if not account_id:
        return False
    
    if len(account_id) < MIN_ACCOUNT_LENGTH:
        return False
    
    if len(account_id) > MAX_ACCOUNT_LENGTH:
        return False
    
    # Must be lowercase
    if account_id != account_id.lower():
        return False
    
    # Check pattern
    if not ACCOUNT_ID_PATTERN.match(account_id):
        return False
    
    # No consecutive separators
    if '..' in account_id or '--' in account_id:
        return False
    
    return True


def validate_account_id(account_id: str) -> str:
    """
    Validate a NEAR account ID and return it if valid.
    
    Args:
        account_id: The account ID to validate
        
    Returns:
        The validated account ID
        
    Raises:
        AccountValidationError: If the account ID is invalid
        
    Examples:
        >>> validate_account_id("example.near")
        'example.near'
        >>> validate_account_id("INVALID")
        Traceback (most recent call last):
            ...
        AccountValidationError: Account ID must be lowercase
    """
    if not account_id:
        raise AccountValidationError("Account ID cannot be empty")
    
    if len(account_id) < MIN_ACCOUNT_LENGTH:
        raise AccountValidationError(
            f"Account ID must be at least {MIN_ACCOUNT_LENGTH} characters"
        )
    
    if len(account_id) > MAX_ACCOUNT_LENGTH:
        raise AccountValidationError(
            f"Account ID must be at most {MAX_ACCOUNT_LENGTH} characters"
        )
    
    if account_id != account_id.lower():
        raise AccountValidationError("Account ID must be lowercase")
    
    if not ACCOUNT_ID_PATTERN.match(account_id):
        raise AccountValidationError(
            "Account ID must contain only lowercase letters, numbers, "
            "and separators (. or -)"
        )
    
    if '..' in account_id or '--' in account_id:
        raise AccountValidationError(
            "Account ID cannot have consecutive separators"
        )
    
    return account_id


def normalize_account_id(account_id: str) -> str:
    """
    Normalize an account ID to lowercase and strip whitespace.
    
    Args:
        account_id: The account ID to normalize
        
    Returns:
        Normalized account ID
        
    Raises:
        AccountValidationError: If the normalized ID is invalid
    """
    normalized = account_id.strip().lower()
    return validate_account_id(normalized)
